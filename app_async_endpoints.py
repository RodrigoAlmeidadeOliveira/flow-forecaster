"""
Async endpoints for Flow Forecaster
These endpoints handle background task management for Celery tasks
Import and register these routes in app.py
"""
from flask import jsonify, request
from flask_login import login_required, current_user
from celery.result import AsyncResult
from logger import get_logger

logger = get_logger('async_endpoints')

# Import Celery app and tasks
try:
    from celery_app import celery_app
    from tasks.simulation_tasks import (
        run_monte_carlo_async,
        run_ml_deadline_async,
        run_backtest_async,
        health_check
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not available. Async endpoints will be disabled.")


def register_async_endpoints(app):
    """
    Register async endpoints with the Flask app

    Usage in app.py:
        from app_async_endpoints import register_async_endpoints
        register_async_endpoints(app)
    """

    if not CELERY_AVAILABLE:
        logger.warning("Celery not available. Skipping async endpoint registration.")
        return

    @app.route('/api/async/simulate', methods=['POST'])
    @login_required
    def async_simulate():
        """
        Execute Monte Carlo simulation asynchronously
        Returns task_id immediately for polling
        """
        try:
            simulation_data = request.json

            # Basic validation (same as synchronous endpoint)
            if not simulation_data.get('tpSamples') or not any(n >= 1 for n in simulation_data['tpSamples']):
                return jsonify({
                    'error': 'Must have at least one weekly throughput sample greater than zero'
                }), 400

            # Set defaults
            simulation_data['minContributors'] = simulation_data.get('minContributors') or simulation_data['totalContributors']
            simulation_data['maxContributors'] = simulation_data.get('maxContributors') or simulation_data['totalContributors']
            simulation_data['ltSamples'] = simulation_data.get('ltSamples', [])
            simulation_data['splitRateSamples'] = simulation_data.get('splitRateSamples', [])
            simulation_data['risks'] = simulation_data.get('risks', [])
            simulation_data['dependencies'] = simulation_data.get('dependencies', [])

            team_focus_value = float(simulation_data.get('teamFocus', 1.0))
            team_focus_value = max(0.0, min(1.0, team_focus_value))
            simulation_data['teamFocus'] = team_focus_value

            # Check if user wants to save forecast
            save_forecast = request.args.get('save', 'false').lower() == 'true'

            # Submit task to Celery
            task = run_monte_carlo_async.delay(
                simulation_data=simulation_data,
                user_id=current_user.id,
                save_forecast=save_forecast
            )

            logger.info(f"Submitted Monte Carlo task {task.id} for user {current_user.id}")

            # Return immediately with task_id
            return jsonify({
                'task_id': task.id,
                'status': 'PENDING',
                'message': 'Simulation queued successfully. Use /api/tasks/<task_id> to check progress.',
                'poll_url': f'/api/tasks/{task.id}'
            }), 202  # HTTP 202 Accepted

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/async/deadline-analysis', methods=['POST'])
    @login_required
    def async_deadline_analysis():
        """Execute ML deadline analysis asynchronously"""
        try:
            data = request.json

            # Basic validation
            if not data.get('tpSamples') or not data.get('backlog'):
                return jsonify({
                    'error': 'tpSamples and backlog are required'
                }), 400

            save_forecast = request.args.get('save', 'false').lower() == 'true'

            # Submit task
            task = run_ml_deadline_async.delay(
                data=data,
                user_id=current_user.id,
                save_forecast=save_forecast
            )

            logger.info(f"Submitted ML deadline analysis task {task.id} for user {current_user.id}")

            return jsonify({
                'task_id': task.id,
                'status': 'PENDING',
                'message': 'Analysis queued successfully.',
                'poll_url': f'/api/tasks/{task.id}'
            }), 202

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/async/backtest', methods=['POST'])
    @login_required
    def async_backtest():
        """Execute backtest asynchronously"""
        try:
            data = request.json

            # Validation
            if not data.get('historicalData'):
                return jsonify({
                    'error': 'historicalData is required'
                }), 400

            save_forecast = request.args.get('save', 'false').lower() == 'true'

            # Submit task
            task = run_backtest_async.delay(
                data=data,
                user_id=current_user.id,
                save_forecast=save_forecast
            )

            logger.info(f"Submitted backtest task {task.id} for user {current_user.id}")

            return jsonify({
                'task_id': task.id,
                'status': 'PENDING',
                'message': 'Backtest queued successfully.',
                'poll_url': f'/api/tasks/{task.id}'
            }), 202

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/tasks/<task_id>', methods=['GET'])
    @login_required
    def get_task_status(task_id):
        """
        Check status of an async task

        Returns:
            - PENDING: Task queued but not started
            - PROGRESS: Task running with progress updates
            - SUCCESS: Task completed with result
            - FAILURE: Task failed with error
        """
        try:
            task = AsyncResult(task_id, app=celery_app)

            if task.state == 'PENDING':
                response = {
                    'state': task.state,
                    'status': 'Task is waiting in queue...',
                    'progress': 0,
                    'total': 100,
                    'stage': 'Pending'
                }
            elif task.state == 'PROGRESS':
                # Task is running - get progress info
                info = task.info or {}
                response = {
                    'state': task.state,
                    'status': info.get('status', 'Processing...'),
                    'progress': info.get('progress', 0),
                    'total': info.get('total', 100),
                    'stage': info.get('stage', 'Processing'),
                    'current': info.get('current', 0)
                }
            elif task.state == 'SUCCESS':
                # Task completed successfully
                info = task.info or {}
                result = info.get('result') if isinstance(info, dict) else task.result
                response = {
                    'state': task.state,
                    'status': 'Complete',
                    'progress': 100,
                    'total': 100,
                    'stage': 'Complete',
                    'result': result
                }
            elif task.state == 'FAILURE':
                # Task failed
                error_info = str(task.info) if task.info else 'Unknown error'
                response = {
                    'state': task.state,
                    'status': 'Failed',
                    'stage': 'Failed',
                    'error': error_info,
                    'progress': 0
                }
            else:
                # Other states (RETRY, REVOKED, etc.)
                response = {
                    'state': task.state,
                    'status': str(task.info) if task.info else task.state,
                    'stage': task.state
                }

            return jsonify(response)

        except Exception as e:
            return jsonify({
                'error': str(e),
                'state': 'ERROR'
            }), 500

    @app.route('/api/tasks/<task_id>', methods=['DELETE'])
    @login_required
    def cancel_task(task_id):
        """Cancel a running or pending task"""
        try:
            task = AsyncResult(task_id, app=celery_app)
            task.revoke(terminate=True, signal='SIGKILL')

            return jsonify({
                'message': 'Task cancelled successfully',
                'task_id': task_id
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500

    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def list_tasks():
        """
        List active tasks for the current user
        Note: This requires Celery to be configured with result backend
        """
        try:
            # This is a basic implementation
            # For production, you'd want to store task_id -> user_id mapping in Redis/DB
            return jsonify({
                'message': 'Task listing requires additional configuration',
                'hint': 'Store task metadata in Redis when tasks are created'
            }), 501

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health/celery', methods=['GET'])
    def celery_health():
        """Check if Celery workers are available"""
        try:
            # Send a test task
            task = health_check.delay()
            result = task.get(timeout=5)  # Wait up to 5 seconds

            return jsonify({
                'status': 'healthy',
                'workers': 'available',
                'test_result': result
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'workers': 'unavailable'
            }), 503

    logger.info("Async endpoints registered successfully")
    logger.info("Available async endpoints:")
    logger.info("  POST   /api/async/simulate")
    logger.info("  POST   /api/async/deadline-analysis")
    logger.info("  POST   /api/async/backtest")
    logger.info("  GET    /api/tasks/<task_id>")
    logger.info("  DELETE /api/tasks/<task_id>")
    logger.info("  GET    /api/health/celery")
