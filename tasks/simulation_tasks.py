"""
Celery Tasks for Long-Running Simulations
Handles Monte Carlo simulations, ML forecasts, and backtesting asynchronously
"""
import json
import traceback
from datetime import datetime
from celery import Task
from celery_app import celery_app
from monte_carlo_unified import (
    run_monte_carlo_simulation,
    forecast_how_many,
    forecast_when
)
from ml_deadline_forecaster import ml_analyze_deadline, ml_forecast_how_many, ml_forecast_when
from backtesting import run_walk_forward_backtest, run_expanding_window_backtest
from database import get_session
from models import Forecast, Project


class DatabaseTask(Task):
    """
    Base task class with database session management
    Ensures sessions are properly closed after task execution
    """
    _session = None

    @property
    def session(self):
        """Get or create a database session"""
        if self._session is None:
            self._session = get_session()
        return self._session

    def after_return(self, *args, **kwargs):
        """Close database session after task completes"""
        if self._session is not None:
            try:
                self._session.close()
            except Exception as e:
                print(f"[WARNING] Error closing session: {e}")
            finally:
                self._session = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='tasks.run_monte_carlo_async',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def run_monte_carlo_async(self, simulation_data: dict, user_id: int = None, save_forecast: bool = False):
    """
    Execute Monte Carlo simulation asynchronously

    Args:
        simulation_data (dict): Simulation parameters including:
            - projectName (str): Name of the project
            - numberOfSimulations (int): Number of Monte Carlo runs
            - tpSamples (list): Throughput samples
            - numberOfTasks (int): Backlog size
            - totalContributors (int): Team size
            - etc.
        user_id (int, optional): User who requested the simulation
        save_forecast (bool): Whether to save results to database

    Returns:
        dict: Simulation results including distributions, percentiles, etc.
    """
    try:
        # Update task state to show progress
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Initializing Monte Carlo simulation',
                'progress': 5,
                'total': 100,
                'current': 0,
                'status': 'Starting...'
            }
        )

        # Log task start
        print(f"[CELERY] Starting Monte Carlo simulation task {self.request.id}")
        print(f"[CELERY] User ID: {user_id}, Project: {simulation_data.get('projectName', 'Unknown')}")

        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Running Monte Carlo simulation',
                'progress': 20,
                'total': 100,
                'current': 20,
                'status': f"Running {simulation_data.get('numberOfSimulations', 10000)} simulations..."
            }
        )

        # Run the actual simulation
        result = run_monte_carlo_simulation(simulation_data)

        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Processing simulation results',
                'progress': 80,
                'total': 100,
                'current': 80,
                'status': 'Computing statistics and distributions...'
            }
        )

        # Add task metadata to result
        result['task_id'] = self.request.id
        result['completed_at'] = datetime.utcnow().isoformat()

        # Save to database if requested
        if save_forecast and user_id:
            self.update_state(
                state='PROGRESS',
                meta={
                    'stage': 'Saving forecast to database',
                    'progress': 90,
                    'total': 100,
                    'current': 90,
                    'status': 'Persisting results...'
                }
            )

            session = self.session

            try:
                # Get or create project
                project_id = simulation_data.get('project_id')
                if project_id:
                    project = session.query(Project).filter(Project.id == project_id).one_or_none()
                    if not project:
                        raise ValueError(f"Project {project_id} not found")
                else:
                    # Create new project
                    project = Project(
                        name=simulation_data.get('projectName', 'Unnamed Project'),
                        user_id=user_id,
                        team_size=simulation_data.get('totalContributors', 1)
                    )
                    session.add(project)
                    session.flush()
                    project_id = project.id

                # Create forecast record
                forecast = Forecast(
                    project_id=project_id,
                    user_id=user_id,
                    name=f"Monte Carlo - {simulation_data.get('projectName', 'Simulation')}",
                    forecast_type='monte_carlo',
                    forecast_data=json.dumps(result),
                    input_data=json.dumps(simulation_data),
                    backlog=simulation_data.get('numberOfTasks'),
                    start_date=simulation_data.get('startDate')
                )
                session.add(forecast)
                session.commit()

                result['forecast_id'] = forecast.id
                print(f"[CELERY] Forecast saved with ID: {forecast.id}")

            except Exception as db_error:
                session.rollback()
                print(f"[CELERY] Error saving forecast: {db_error}")
                # Don't fail the task if saving fails - return results anyway
                result['save_error'] = str(db_error)

        # Task completed successfully
        self.update_state(
            state='SUCCESS',
            meta={
                'stage': 'Complete',
                'progress': 100,
                'total': 100,
                'current': 100,
                'status': 'Simulation completed successfully',
                'result': result
            }
        )

        print(f"[CELERY] Monte Carlo simulation task {self.request.id} completed successfully")
        return result

    except Exception as exc:
        # Log error
        print(f"[CELERY] Error in Monte Carlo simulation task {self.request.id}: {exc}")
        print(traceback.format_exc())

        # Update state with error
        self.update_state(
            state='FAILURE',
            meta={
                'stage': 'Failed',
                'error': str(exc),
                'traceback': traceback.format_exc(),
                'status': f'Simulation failed: {str(exc)}'
            }
        )

        # Re-raise to trigger retry
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='tasks.run_ml_deadline_async',
    max_retries=3,
    default_retry_delay=60
)
def run_ml_deadline_async(self, data: dict, user_id: int = None, save_forecast: bool = False):
    """
    Execute ML deadline analysis asynchronously

    Args:
        data (dict): Analysis parameters including:
            - tpSamples (list): Throughput samples
            - backlog (int): Number of items
            - deadlineDate (str): Target deadline
            - startDate (str): Start date
            - nSimulations (int): Number of simulations
        user_id (int, optional): User who requested the analysis
        save_forecast (bool): Whether to save results

    Returns:
        dict: ML analysis results
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Training ML models',
                'progress': 20,
                'total': 100,
                'status': 'Training Random Forest, XGBoost, and Neural Network...'
            }
        )

        print(f"[CELERY] Starting ML deadline analysis task {self.request.id}")

        # Run ML analysis
        result = ml_analyze_deadline(
            tp_samples=data['tpSamples'],
            backlog=data['backlog'],
            deadline_date=data.get('deadlineDate'),
            start_date=data.get('startDate'),
            n_simulations=data.get('nSimulations', 10000)
        )

        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'ML analysis complete',
                'progress': 90,
                'total': 100,
                'status': 'Finalizing results...'
            }
        )

        result['task_id'] = self.request.id
        result['completed_at'] = datetime.utcnow().isoformat()

        # Save if requested
        if save_forecast and user_id:
            session = self.session
            try:
                project_id = data.get('project_id')
                if not project_id:
                    project = Project(
                        name=data.get('projectName', 'ML Analysis'),
                        user_id=user_id
                    )
                    session.add(project)
                    session.flush()
                    project_id = project.id

                forecast = Forecast(
                    project_id=project_id,
                    user_id=user_id,
                    name=f"ML Deadline Analysis - {data.get('projectName', 'Analysis')}",
                    forecast_type='ml_deadline',
                    forecast_data=json.dumps(result),
                    input_data=json.dumps(data),
                    backlog=data['backlog'],
                    deadline_date=data.get('deadlineDate'),
                    start_date=data.get('startDate')
                )
                session.add(forecast)
                session.commit()
                result['forecast_id'] = forecast.id
            except Exception as db_error:
                session.rollback()
                result['save_error'] = str(db_error)

        self.update_state(
            state='SUCCESS',
            meta={
                'stage': 'Complete',
                'progress': 100,
                'total': 100,
                'status': 'ML analysis completed',
                'result': result
            }
        )

        print(f"[CELERY] ML deadline analysis task {self.request.id} completed")
        return result

    except Exception as exc:
        print(f"[CELERY] Error in ML deadline analysis: {exc}")
        print(traceback.format_exc())

        self.update_state(
            state='FAILURE',
            meta={
                'stage': 'Failed',
                'error': str(exc),
                'traceback': traceback.format_exc()
            }
        )
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='tasks.run_backtest_async',
    max_retries=2,
    default_retry_delay=120
)
def run_backtest_async(self, data: dict, user_id: int = None, save_forecast: bool = False):
    """
    Execute walk-forward backtest asynchronously

    Args:
        data (dict): Backtest parameters including:
            - historicalData (list): Historical throughput data
            - trainWindow (int): Training window size
            - testWindow (int): Test window size
            - nSimulations (int): Simulations per window
        user_id (int, optional): User ID
        save_forecast (bool): Whether to save results

    Returns:
        dict: Backtest results with accuracy metrics
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Preparing backtest',
                'progress': 10,
                'total': 100,
                'status': 'Setting up walk-forward validation...'
            }
        )

        print(f"[CELERY] Starting backtest task {self.request.id}")

        # Determine backtest type
        backtest_type = data.get('backtest_type', 'walk_forward')

        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Running backtest',
                'progress': 30,
                'total': 100,
                'status': f'Executing {backtest_type} backtest...'
            }
        )

        if backtest_type == 'expanding_window':
            result = run_expanding_window_backtest(
                historical_data=data['historicalData'],
                initial_train_window=data.get('initialTrainWindow', 5),
                test_window=data.get('testWindow', 2),
                n_simulations=data.get('nSimulations', 5000)
            )
        else:
            result = run_walk_forward_backtest(
                historical_data=data['historicalData'],
                train_window=data.get('trainWindow', 10),
                test_window=data.get('testWindow', 2),
                n_simulations=data.get('nSimulations', 5000)
            )

        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'Computing accuracy metrics',
                'progress': 80,
                'total': 100,
                'status': 'Analyzing backtest results...'
            }
        )

        result['task_id'] = self.request.id
        result['completed_at'] = datetime.utcnow().isoformat()

        # Save if requested
        if save_forecast and user_id:
            session = self.session
            try:
                project_id = data.get('project_id')
                if not project_id:
                    project = Project(
                        name=data.get('projectName', 'Backtest'),
                        user_id=user_id
                    )
                    session.add(project)
                    session.flush()
                    project_id = project.id

                forecast = Forecast(
                    project_id=project_id,
                    user_id=user_id,
                    name=f"Backtest - {backtest_type}",
                    forecast_type='backtest',
                    forecast_data=json.dumps(result),
                    input_data=json.dumps(data)
                )
                session.add(forecast)
                session.commit()
                result['forecast_id'] = forecast.id
            except Exception as db_error:
                session.rollback()
                result['save_error'] = str(db_error)

        self.update_state(
            state='SUCCESS',
            meta={
                'stage': 'Complete',
                'progress': 100,
                'total': 100,
                'status': 'Backtest completed',
                'result': result
            }
        )

        print(f"[CELERY] Backtest task {self.request.id} completed")
        return result

    except Exception as exc:
        print(f"[CELERY] Error in backtest: {exc}")
        print(traceback.format_exc())

        self.update_state(
            state='FAILURE',
            meta={
                'stage': 'Failed',
                'error': str(exc),
                'traceback': traceback.format_exc()
            }
        )
        raise


@celery_app.task(
    bind=True,
    name='tasks.health_check',
    max_retries=0
)
def health_check(self):
    """
    Health check task to verify Celery workers are running

    Returns:
        dict: Worker status information
    """
    return {
        'status': 'healthy',
        'task_id': self.request.id,
        'timestamp': datetime.utcnow().isoformat(),
        'worker': self.request.hostname
    }
