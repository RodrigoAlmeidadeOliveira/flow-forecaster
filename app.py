"""
Project Forecaster - Flask Application
Monte Carlo simulation for project forecasting
"""

import os
import json
import base64
import numpy as np
import re
import pickle
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_compress import Compress
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse, urljoin
from monte_carlo_unified import (
    run_monte_carlo_simulation,
    simulate_throughput_forecast,
    analyze_deadline,
    forecast_how_many,
    forecast_when,
    percentile as mc_percentile,
    calculate_risk_summary,
)
from ml_forecaster import MLForecaster
from ml_deadline_forecaster import ml_analyze_deadline, ml_forecast_how_many, ml_forecast_when
from cod_forecaster import CoDForecaster, generate_sample_cod_data
from visualization import ForecastVisualizer
from demand_forecasting import DemandForecastService
from cost_pert_beta import (
    simulate_pert_beta_cost,
    calculate_risk_metrics,
    calculate_effort_based_cost,
    calculate_effort_based_cost_with_percentiles
)
from database import get_session, close_session, init_db
from models import Project, Forecast, Actual, User, CoDTrainingDataset, CoDModel
from accuracy_metrics import (
    calculate_accuracy_metrics,
    calculate_time_series_metrics,
    detect_data_quality_issues,
    generate_recommendations
)
from backtesting import (
    run_walk_forward_backtest,
    run_expanding_window_backtest,
    compare_confidence_levels,
    generate_backtest_report
)
from portfolio_analyzer import (
    calculate_project_health_score,
    analyze_portfolio_capacity,
    create_prioritization_matrix,
    generate_portfolio_alerts
)
from trend_analysis import comprehensive_trend_analysis

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLOW_FORECASTER_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'change-me-in-production'

BASE_DIR = Path(__file__).resolve().parent
COD_SAMPLE_PATH = BASE_DIR / 'data' / 'cod_training_sample.csv'

# Enable GZIP compression for better performance over slow networks
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json',
    'application/javascript', 'text/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # Balance between speed and compression (1-9)
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress responses > 500 bytes
Compress(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize database
init_db()


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login session management."""
    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    session = get_session()
    try:
        user = session.get(User, user_id)
        if user:
            session.expunge(user)
        return user
    finally:
        session.close()


@app.teardown_appcontext
def remove_session(exception=None):
    """Ensure scoped sessions are properly removed at request end."""
    close_session()


@app.context_processor
def inject_auth_context():
    """Expose auth helpers to Jinja templates."""
    return {
        'is_admin_user': current_user_is_admin(),
        'ADMIN_ROLES': ADMIN_ROLES
    }

# Debugging: Print routes at startup
import sys
import math
print("="*60, flush=True)
print("Flask app created successfully!", flush=True)
print(f"App name: {app.name}", flush=True)
print(f"Template folder: {app.template_folder}", flush=True)
print(f"Root path: {app.root_path}", flush=True)
print("="*60, flush=True)
sys.stdout.flush()

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
ADMIN_ROLES = {'admin', 'instructor'}

COD_REQUIRED_COLUMNS = {
    'budget_millions',
    'duration_weeks',
    'team_size',
    'num_stakeholders',
    'business_value',
    'complexity',
    'cod_weekly',
}
COD_OPTIONAL_COLUMNS = {'project_type', 'risk_level'}


def convert_to_native_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return [convert_to_native_types(item) for item in obj.tolist()]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        value = float(obj)
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj


def is_safe_redirect_url(target: Optional[str]) -> bool:
    """Ensure redirect targets stay within the same host to avoid open redirects."""
    if not target:
        return False

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc
    )


def current_user_is_admin() -> bool:
    """Determine if the logged-in user has elevated privileges."""
    if not getattr(current_user, 'is_authenticated', False):
        return False

    role = getattr(current_user, 'role', None)
    return isinstance(role, str) and role.lower() in ADMIN_ROLES


def scoped_project_query(session):
    """Return a Project query scoped to the current user when needed."""
    query = session.query(Project)
    if current_user_is_admin():
        return query
    return query.filter(Project.user_id == current_user.id)


def scoped_forecast_query(session):
    """Return a Forecast query scoped to the current user when needed."""
    query = session.query(Forecast).outerjoin(Project, Forecast.project_id == Project.id)
    if current_user_is_admin():
        return query
    user_id = getattr(current_user, 'id', None)
    user_email = getattr(current_user, 'email', None)

    filters = []
    if user_id is not None:
        filters.append(Forecast.user_id == user_id)
        filters.append(Project.user_id == user_id)

    if user_email:
        filters.append(Forecast.created_by == user_email)

    if not filters:
        # No authenticated user context; return no records
        return query.filter(Forecast.id == -1)

    return query.filter(or_(*filters))


def scoped_actual_query(session):
    """Return an Actual query scoped to the current user."""
    query = session.query(Actual)
    if current_user_is_admin():
        return query
    return query.join(Forecast).filter(Forecast.user_id == current_user.id)


def has_record_access(record, attr='user_id') -> bool:
    """Check whether the logged-in user can access the given record."""
    if record is None:
        return False
    if current_user_is_admin():
        return True
    return getattr(record, attr, None) == current_user.id


def parse_flexible_date(date_str: str) -> datetime:
    """
    Parse a date string in common day-month-year formats.

    Raises:
        ValueError: If the string doesn't match supported formats.
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
    value = date_str.strip()
    if not value:
        raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
    for fmt in ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date {date_str} doesn't match expected day-month-year formats")


@app.after_request
def add_no_cache_headers(response):
    """Add no-cache headers to HTML responses to prevent browser caching issues."""
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Allow students/instructors to create an account."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    errors = []
    form_data = {
        'name': '',
        'email': ''
    }

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email_raw = (request.form.get('email') or '').strip()
        email = email_raw.lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        form_data['name'] = name
        form_data['email'] = email_raw

        if not name:
            errors.append('Informe seu nome completo.')

        if not email or not EMAIL_REGEX.match(email):
            errors.append('Informe um e-mail válido.')

        if len(password) < 8:
            errors.append('A senha deve ter pelo menos 8 caracteres.')

        if password != confirm_password:
            errors.append('As senhas informadas não coincidem.')

        session = None
        new_user = None

        if not errors:
            session = get_session()
            try:
                is_first_user = session.query(User.id).first() is None
                role = 'admin' if is_first_user else 'student'

                registration_date = datetime.utcnow()
                new_user = User(
                    email=email,
                    name=name,
                    role=role,
                    registration_date=registration_date,
                    access_expires_at=registration_date + timedelta(days=365),
                )
                new_user.set_password(password)

                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                session.expunge(new_user)

                login_user(new_user)
                flash('Conta criada com sucesso! Bem-vindo ao Flow Forecaster.', 'success')
                return redirect(url_for('index'))
            except IntegrityError:
                if session:
                    session.rollback()
                errors.append('Este e-mail já está cadastrado. Faça login ou escolha outro e-mail.')
            finally:
                if session:
                    session.close()

    return render_template('auth/register.html', errors=errors, form_data=form_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    errors = []
    form_data = {
        'email': ''
    }

    next_url = request.args.get('next') if request.method == 'GET' else request.form.get('next')

    if request.method == 'POST':
        email_raw = (request.form.get('email') or '').strip()
        email = email_raw.lower()
        password = request.form.get('password') or ''
        remember = bool(request.form.get('remember'))

        form_data['email'] = email_raw

        session = get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user or not user.check_password(password):
                errors.append('E-mail ou senha inválidos. Verifique e tente novamente.')
            elif not user.is_active:
                errors.append('Sua conta está desativada. Entre em contato com o instrutor.')
            elif user.access_expires_at and datetime.utcnow() > user.access_expires_at:
                errors.append('Seu acesso expirou. Entre em contato com o instrutor para renovação.')
            else:
                user.last_login = datetime.utcnow()
                session.commit()
                session.refresh(user)
                session.expunge(user)

                login_user(user, remember=remember)
                flash(f'Bem-vindo de volta, {user.name}!', 'success')

                if next_url and is_safe_redirect_url(next_url):
                    return redirect(next_url)
                return redirect(url_for('index'))
        finally:
            session.close()

    return render_template('auth/login.html', errors=errors, form_data=form_data, next=next_url)


@app.route('/logout')
@login_required
def logout():
    """Terminate the current user session."""
    logout_user()
    flash('Você saiu da aplicação com segurança.', 'info')
    return redirect(url_for('login'))


@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok", "routes": len(list(app.url_map.iter_rules()))}


@app.route('/')
@login_required
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback if template rendering fails
        return f"""
        <html>
        <head><title>Flow Forecasting - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading template: {str(e)}</p>
            <p>Template path: {app.template_folder}</p>
        </body>
        </html>
        """, 500


@app.route('/advanced')
@login_required
def advanced():
    """Redirect to the unified advanced forecasting section."""
    return redirect(url_for('index') + '#advanced-forecast')


@app.route('/dependency-analysis')
@login_required
def dependency_analysis_page():
    """Render the dependency analysis page."""
    try:
        return render_template('dependency_analysis.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Dependency Analysis - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading dependency analysis template: {str(e)}</p>
        </body>
        </html>
        """, 500


@app.route('/documentacao')
def documentation():
    """Render the user manual/documentation page."""
    try:
        return render_template('documentacao.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Documentação - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading documentation template: {str(e)}</p>
        </body>
        </html>
        """, 500


@app.route('/docs')
def docs_redirect():
    """Redirect /docs to /documentacao."""
    return redirect(url_for('documentation'))


@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    """
    Execute Monte Carlo simulation based on provided data.

    Expected JSON payload:
    {
        "projectName": str,
        "numberOfSimulations": int,
        "confidenceLevel": int,
        "tpSamples": list[float],
        "ltSamples": list[float],
        "splitRateSamples": list[float],
        "risks": list[dict],
        "numberOfTasks": int,
        "totalContributors": int,
        "minContributors": int,
        "maxContributors": int,
        "sCurveSize": int,
        "startDate": str (optional)
    }

    Returns:
        JSON with simulation results
    """
    try:
        simulation_data = request.json

        # Validation
        if not simulation_data.get('tpSamples') or not any(n >= 1 for n in simulation_data['tpSamples']):
            return jsonify({
                'error': 'Must have at least one weekly throughput sample greater than zero'
            }), 400

        split_rate_samples = simulation_data.get('splitRateSamples', [])
        if split_rate_samples and any(n > 10 or n < 0.2 for n in split_rate_samples):
            return jsonify({
                'error': 'Your split rates don\'t seem correct. For a 10% split rate, you should put \'1.1\'.'
            }), 400

        # Set defaults for optional fields
        simulation_data['minContributors'] = (simulation_data.get('minContributors') or
                                             simulation_data['totalContributors'])
        simulation_data['maxContributors'] = (simulation_data.get('maxContributors') or
                                             simulation_data['totalContributors'])
        simulation_data['ltSamples'] = simulation_data.get('ltSamples', [])
        simulation_data['splitRateSamples'] = split_rate_samples
        simulation_data['risks'] = simulation_data.get('risks', [])
        simulation_data['dependencies'] = simulation_data.get('dependencies', [])
        team_focus_raw = simulation_data.get('teamFocus')
        try:
            team_focus_value = float(team_focus_raw) if team_focus_raw is not None else 1.0
        except (TypeError, ValueError):
            team_focus_value = 1.0
        team_focus_value = max(0.0, min(1.0, team_focus_value))
        simulation_data['teamFocus'] = team_focus_value
        if 'teamFocusPercent' not in simulation_data:
            simulation_data['teamFocusPercent'] = round(team_focus_value * 100, 2)

        # Debug: log dependencies
        print(f"[INFO] Received {len(simulation_data['dependencies'])} dependencies", flush=True)
        if simulation_data['dependencies']:
            print(f"[INFO] First dependency: {simulation_data['dependencies'][0]}", flush=True)

        # Run the simulation
        result = run_monte_carlo_simulation(simulation_data)

        # Debug: check if dependency_analysis is in result
        if 'dependency_analysis' in result:
            print(f"[INFO] dependency_analysis is in result with {result['dependency_analysis']['total_dependencies']} deps", flush=True)
        else:
            print(f"[WARNING] dependency_analysis NOT in result. Result keys: {list(result.keys())}", flush=True)

        # Compute 30-day probability table for quick planning
        items_forecast_30_days = None
        try:
            tp_samples = simulation_data.get('tpSamples', [])
            if tp_samples:
                start_date_raw = simulation_data.get('startDate') or datetime.now().strftime('%d/%m/%Y')
                start_dt = parse_flexible_date(start_date_raw)
                horizon_dt = start_dt + timedelta(days=30)
                horizon_str = horizon_dt.strftime('%d/%m/%Y')
                focus_factor = simulation_data['teamFocus']
                forecast_30_days = forecast_how_many(
                    tp_samples=tp_samples,
                    start_date=start_date_raw,
                    end_date=horizon_str,
                    n_simulations=simulation_data.get('numberOfSimulations', 10000),
                    focus_factor=focus_factor
                )
                distribution_30 = forecast_30_days.get('distribution') or []
                probability_rows_30 = []
                if distribution_30:
                    seen_probs = set()
                    for prob in range(100, 0, -5):
                        # FIX: Probability interpretation
                        # 100% probability = percentile 0 (minimum value that occurs in 100% of cases)
                        # 1% probability = percentile 99 (value that only 1% of cases exceed)
                        percentile_value = mc_percentile(distribution_30, (100 - prob) / 100)
                        probability_rows_30.append({
                            'probability': prob,
                            'items': int(round(percentile_value))
                        })
                        seen_probs.add(prob)
                    if 1 not in seen_probs:
                        percentile_value = mc_percentile(distribution_30, 0.99)
                        probability_rows_30.append({
                            'probability': 1,
                            'items': int(round(percentile_value))
                        })

                items_forecast_30_days = {
                    'start_date': forecast_30_days.get('start_date', start_dt.strftime('%d/%m/%Y')),
                    'end_date': forecast_30_days.get('end_date', horizon_str),
                    'days': forecast_30_days.get('days', 30),
                    'weeks': forecast_30_days.get('weeks'),
                    'items_mean': forecast_30_days.get('items_mean'),
                    'probability_table': probability_rows_30
                }
        except Exception:
            items_forecast_30_days = None

        result['items_forecast_30_days'] = items_forecast_30_days

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/encode', methods=['POST'])
@login_required
def encode_data():
    """
    Encode simulation data to base64 for URL sharing.

    Returns:
        JSON with encoded string
    """
    try:
        data = request.json
        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        return jsonify({'encoded': encoded})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/decode', methods=['POST'])
@login_required
def decode_data():
    """
    Decode base64 simulation data from URL.

    Returns:
        JSON with decoded data
    """
    try:
        encoded = request.json.get('encoded', '')
        decoded_bytes = base64.b64decode(encoded.encode('utf-8'))
        data = json.loads(decoded_bytes.decode('utf-8'))
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml-forecast', methods=['POST'])
@login_required
def ml_forecast():
    """
    Execute ML-based forecast.

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "forecastSteps": int (default: 4),
        "model": str (default: "ensemble")
    }

    Returns:
        JSON with ML forecast results and visualizations
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        forecast_steps = data.get('forecastSteps', 4)
        model_name = data.get('model', 'ensemble')
        start_date = data.get('startDate')

        # Validate minimum samples for reliable ML
        if not tp_samples or len(tp_samples) < 15:
            return jsonify({
                'error': 'insufficient_data',
                'message': f'Machine Learning requires at least 15 samples for reliable results. You provided {len(tp_samples)} samples.',
                'recommendation': 'Use Monte Carlo simulation instead, which works well with 5+ samples.',
                'min_required': 15,
                'provided': len(tp_samples),
                'use_monte_carlo': True
            }), 400

        # Convert to numpy array
        tp_data = np.array(tp_samples, dtype=float)

        # Initialize ML forecaster with K-Fold CV protocol
        forecaster = MLForecaster(max_lag=4, n_splits=5, validation_size=0.2)

        # Train models using K-Fold CV with Grid Search
        forecaster.train_models(tp_data, use_kfold_cv=True)

        # Generate forecasts
        forecasts = forecaster.forecast(tp_data, steps=forecast_steps, model_name=model_name)

        # Get ensemble statistics
        ensemble_stats = forecaster.get_ensemble_forecast(forecasts)

        # Get model results summary
        model_results = forecaster.get_results_summary()
        walk_forward_results = forecaster.walk_forward_validation(tp_data, forecast_steps=forecast_steps)

        # Get risk assessment
        risk_assessment = forecaster.assess_forecast_risk(tp_data)

        # Generate visualization
        visualizer = ForecastVisualizer()
        chart_ml = visualizer.plot_ml_forecasts(tp_data, forecasts, ensemble_stats, start_date)
        walk_forward_charts = visualizer.plot_walk_forward_forecasts(
            tp_data,
            walk_forward_results,
            start_date
        )
        chart_history = visualizer.plot_historical_analysis(tp_data, start_date)

        response_data = {
            'forecasts': {k: v.tolist() for k, v in forecasts.items()},
            'ensemble_stats': {k: v.tolist() if isinstance(v, np.ndarray) else v
                             for k, v in ensemble_stats.items()},
            'model_results': model_results,
            'risk_assessment': convert_to_native_types(risk_assessment),
            'walk_forward': convert_to_native_types(walk_forward_results),
            'charts': {
                'ml_forecast': chart_ml,
                'historical_analysis': chart_history,
                'walk_forward': walk_forward_charts
            }
        }
        return jsonify(response_data)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/demand/forecast', methods=['POST'])
@login_required
def demand_forecast():
    """
    Execute demand forecasting based on arrival dates provided by the user.

    Expected JSON payload:
    {
        "dates": list[str],               # Demand arrival timestamps
        "forecastDays": int (default 14), # Horizon for daily forecast
        "forecastWeeks": int (default 8), # Horizon for weekly forecast
        "excludeWeekends": bool           # Optional, drop Saturday/Sunday from history
    }
    """
    try:
        payload = request.json or {}
        raw_dates = payload.get('dates') or payload.get('demandDates') or []
        if isinstance(raw_dates, str):
            raw_dates = [raw_dates]

        forecast_days = int(payload.get('forecastDays', 14))
        forecast_weeks = int(payload.get('forecastWeeks', 8))
        exclude_weekends = bool(payload.get('excludeWeekends', False))

        service = DemandForecastService(
            raw_dates,
            exclude_weekends=exclude_weekends,
        )

        results = service.generate(
            daily_horizon=max(1, forecast_days),
            weekly_horizon=max(1, forecast_weeks),
        )

        visualizer = ForecastVisualizer()
        charts = {}

        if 'daily_forecast' in results:
            daily = results['daily_forecast']
            daily_dates = [
                datetime.strptime(date_str, '%Y-%m-%d')
                for date_str in daily.get('dates', [])
            ]
            charts['daily'] = visualizer.plot_demand_forecast(
                service.daily_series,
                daily_dates,
                daily['ensemble'],
                title='Previsão diária de demanda',
                ylabel='Itens por dia'
            )

        if 'weekly_forecast' in results:
            weekly = results['weekly_forecast']
            weekly_dates = [
                datetime.strptime(date_str, '%Y-%m-%d')
                for date_str in weekly.get('dates', [])
            ]
            charts['weekly'] = visualizer.plot_demand_forecast(
                service.weekly_series,
                weekly_dates,
                weekly['ensemble'],
                title='Previsão semanal de demanda',
                ylabel='Itens por semana'
            )

        results['charts'] = charts
        return jsonify(results)

    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        import traceback
        return jsonify({
            'error': 'Erro ao gerar a previsão de demanda',
            'details': str(exc),
            'trace': traceback.format_exc()
        }), 500


@app.route('/api/mc-throughput', methods=['POST'])
@login_required
def mc_throughput():
    """
    Execute Monte Carlo throughput-based forecast.

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "backlog": int,
        "nSimulations": int (default: 10000)
    }

    Returns:
        JSON with Monte Carlo results and visualizations
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        backlog = data.get('backlog', 0)
        n_simulations = data.get('nSimulations', 10000)
        start_date = data.get('startDate')

        if not tp_samples:
            return jsonify({'error': 'Need throughput samples'}), 400

        if backlog <= 0:
            return jsonify({'error': 'Backlog must be greater than zero'}), 400

        # Run Monte Carlo simulation
        mc_results = simulate_throughput_forecast(tp_samples, backlog, n_simulations)

        # Generate visualization
        visualizer = ForecastVisualizer()
        chart_mc = visualizer.plot_monte_carlo_results(
            np.array(tp_samples),
            mc_results,
            start_date
        )

        response_data = {
            'percentile_stats': convert_to_native_types(mc_results['percentile_stats']),
            'mean': convert_to_native_types(mc_results['mean']),
            'std': convert_to_native_types(mc_results['std']),
            'input_stats': convert_to_native_types(mc_results.get('input_stats')),
            'charts': {
                'monte_carlo': chart_mc
            }
        }
        return jsonify(response_data)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/combined-forecast', methods=['POST'])
@login_required
def combined_forecast():
    """
    Execute combined ML + Monte Carlo forecast.

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "backlog": int,
        "forecastSteps": int,
        "nSimulations": int
    }

    Returns:
        JSON with combined results and comparison charts
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        backlog = data.get('backlog', 0)
        forecast_steps = data.get('forecastSteps', 4)
        n_simulations = data.get('nSimulations', 10000)
        start_date = data.get('startDate')

        # Validate minimum samples for reliable ML
        if not tp_samples or len(tp_samples) < 15:
            return jsonify({
                'error': 'insufficient_data',
                'message': f'Machine Learning requires at least 15 samples for reliable results. You provided {len(tp_samples)} samples.',
                'recommendation': 'Use Monte Carlo simulation instead, which works well with 5+ samples.',
                'min_required': 15,
                'provided': len(tp_samples),
                'use_monte_carlo': True
            }), 400

        tp_data = np.array(tp_samples, dtype=float)

        # ML Forecast with K-Fold CV protocol
        forecaster = MLForecaster(max_lag=4, n_splits=5, validation_size=0.2)
        forecaster.train_models(tp_data, use_kfold_cv=True)
        forecasts = forecaster.forecast(tp_data, steps=forecast_steps, model_name='ensemble')
        ensemble_stats = forecaster.get_ensemble_forecast(forecasts)
        risk_assessment = forecaster.assess_forecast_risk(tp_data)
        model_results = forecaster.get_results_summary()
        walk_forward_results = forecaster.walk_forward_validation(tp_data, forecast_steps=forecast_steps)

        # Monte Carlo Forecast
        mc_results = simulate_throughput_forecast(tp_samples, backlog, n_simulations)

        # Generate visualizations
        visualizer = ForecastVisualizer()
        chart_ml = visualizer.plot_ml_forecasts(tp_data, forecasts, ensemble_stats, start_date)
        chart_mc = visualizer.plot_monte_carlo_results(tp_data, mc_results, start_date)
        chart_comparison = visualizer.plot_comparison_chart(
            tp_data,
            ensemble_stats['mean'],
            mc_results['percentile_stats'],
            start_date
        )
        walk_forward_charts = visualizer.plot_walk_forward_forecasts(
            tp_data,
            walk_forward_results,
            start_date
        )

        response_data = {
            'ml': {
                'forecasts': {k: v.tolist() for k, v in forecasts.items()},
                'ensemble': {k: v.tolist() if isinstance(v, np.ndarray) else v
                           for k, v in ensemble_stats.items()},
                'risk_assessment': convert_to_native_types(risk_assessment),
                'model_results': model_results,
                'walk_forward': convert_to_native_types(walk_forward_results)
            },
            'monte_carlo': {
                'percentile_stats': convert_to_native_types(mc_results['percentile_stats']),
                'mean': convert_to_native_types(mc_results['mean']),
                'std': convert_to_native_types(mc_results['std']),
                'input_stats': convert_to_native_types(mc_results.get('input_stats'))
            },
            'charts': {
                'ml_forecast': chart_ml,
                'monte_carlo': chart_mc,
                'comparison': chart_comparison,
                'walk_forward': walk_forward_charts
            }
        }
        return jsonify(convert_to_native_types(response_data))

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/deadline-analysis')
def deadline_analysis_page():
    """Render the deadline analysis page."""
    return render_template('deadline_analysis.html')


@app.route('/api/deadline-analysis', methods=['POST'])
@login_required
def api_deadline_analysis():
    """
    Execute deadline analysis using both Monte Carlo and Machine Learning.

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "backlog": int,
        "deadlineDate": str (DD/MM/YYYY),
        "startDate": str (DD/MM/YYYY),
        "teamSize": int (optional, default: 1),
        "minContributors": int (optional),
        "maxContributors": int (optional),
        "sCurveSize": int (optional, default: 0),
        "ltSamples": list[float] (optional),
        "splitRateSamples": list[float] (optional),
        "nSimulations": int (optional, default: 10000),
        "costPerPersonWeek": float (optional, default: 5000, custo por pessoa-semana)
    }

    Returns:
        JSON with deadline analysis results from both methods, including cost estimates
    """
    try:
        print("=" * 60, flush=True)
        print("API DEADLINE ANALYSIS CALLED", flush=True)
        print("=" * 60, flush=True)

        data = request.json
        print(f"Received data keys: {list(data.keys()) if data else 'None'}", flush=True)

        tp_samples = data.get('tpSamples', [])
        backlog = data.get('backlog', 0)
        deadline_date = data.get('deadlineDate')
        start_date = data.get('startDate')
        team_size = data.get('teamSize', 1)
        min_contributors = data.get('minContributors')
        max_contributors = data.get('maxContributors')
        s_curve_size = data.get('sCurveSize', 0)
        lt_samples = data.get('ltSamples', [])
        split_rate_samples = data.get('splitRateSamples', [])
        n_simulations = data.get('nSimulations', 10000)
        cost_per_person_week = data.get('costPerPersonWeek', 5000)  # Default: R$ 5,000/week
        simulation_payload = data.get('simulationData')

        team_focus_raw = data.get('teamFocus')
        try:
            team_focus_value = float(team_focus_raw) if team_focus_raw is not None else 1.0
        except (TypeError, ValueError):
            team_focus_value = 1.0
        team_focus_value = max(0.0, min(1.0, team_focus_value))

        simulation_data = None

        if simulation_payload:
            simulation_data = simulation_payload.copy()
            tp_samples = simulation_data.get('tpSamples', tp_samples)
            backlog = simulation_data.get('numberOfTasks', backlog)
            team_size = simulation_data.get('totalContributors', team_size)
            min_contributors = simulation_data.get('minContributors') or team_size
            max_contributors = simulation_data.get('maxContributors') or team_size
            s_curve_size = simulation_data.get('sCurveSize', s_curve_size)
            lt_samples = simulation_data.get('ltSamples', lt_samples) or []
            split_rate_samples = simulation_data.get('splitRateSamples', split_rate_samples) or []
            n_simulations = data.get('nSimulations', simulation_data.get('numberOfSimulations', n_simulations))
            start_date = data.get('startDate') or simulation_data.get('startDate') or start_date
            deadline_date = data.get('deadlineDate') or simulation_data.get('deadlineDate') or deadline_date

            simulation_data.update({
                'tpSamples': tp_samples,
                'ltSamples': lt_samples,
                'splitRateSamples': split_rate_samples,
                'risks': simulation_data.get('risks', []),
                'numberOfTasks': backlog,
                'totalContributors': team_size,
                'minContributors': min_contributors,
                'maxContributors': max_contributors,
                'sCurveSize': s_curve_size,
                'numberOfSimulations': n_simulations
            })
            sim_focus_raw = simulation_data.get('teamFocus', team_focus_value)
            try:
                team_focus_value = float(sim_focus_raw)
            except (TypeError, ValueError):
                team_focus_value = 1.0
            team_focus_value = max(0.0, min(1.0, team_focus_value))
            simulation_data['teamFocus'] = team_focus_value
            simulation_data.setdefault('teamFocusPercent', round(team_focus_value * 100, 2))

        if not tp_samples:
            return jsonify({'error': 'Need throughput samples'}), 400
        if not deadline_date or not start_date:
            return jsonify({'error': 'Need start date and deadline date'}), 400
        if backlog <= 0:
            return jsonify({'error': 'Backlog must be greater than zero'}), 400

        try:
            start_dt = parse_flexible_date(start_date)
            deadline_dt = parse_flexible_date(deadline_date)
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400

        weeks_to_deadline = (deadline_dt - start_dt).days / 7.0

        input_stats = None
        if simulation_data:
            mc_simulation = run_monte_carlo_simulation(simulation_data)
            percentile_stats = mc_simulation.get('percentile_stats', {})
            projected_weeks_p85 = float(percentile_stats.get('p85', 0))
            projected_weeks_p50 = float(percentile_stats.get('p50', 0))
            projected_weeks_p95 = float(percentile_stats.get('p95', projected_weeks_p85))
            input_stats = mc_simulation.get('input_stats')
        else:
            mc_basic = analyze_deadline(
                tp_samples=tp_samples,
                backlog=backlog,
                deadline_date=deadline_date,
                start_date=start_date,
                n_simulations=n_simulations,
                focus_factor=team_focus_value
            )
            percentile_stats = mc_basic.get('percentile_stats', {})
            projected_weeks_p85 = float(percentile_stats.get('p85', 0))
            projected_weeks_p50 = float(percentile_stats.get('p50', 0))
            projected_weeks_p95 = float(percentile_stats.get('p95', projected_weeks_p85))
            input_stats = mc_basic.get('input_stats')

        can_meet_deadline = weeks_to_deadline >= projected_weeks_p85

        # "Quantos?" - How many items can be completed in the deadline period?
        # This answers: "If I have this much time, how many items can I complete?"
        # Calculate using the same complex simulation to ensure consistency
        # If it takes projected_weeks_pXX to complete backlog items, then in weeks_to_deadline we can complete:
        # (weeks_to_deadline / projected_weeks_pXX) * backlog
        items_possible_p95 = int(round((weeks_to_deadline / projected_weeks_p95) * backlog)) if projected_weeks_p95 > 0 else 0
        items_possible_p85 = int(round((weeks_to_deadline / projected_weeks_p85) * backlog)) if projected_weeks_p85 > 0 else 0
        items_possible_p50 = int(round((weeks_to_deadline / projected_weeks_p50) * backlog)) if projected_weeks_p50 > 0 else 0

        # Additional 30-day forecast to power probability report
        items_forecast_30_days = None
        try:
            horizon_30_dt = start_dt + timedelta(days=30)
            horizon_30_str = horizon_30_dt.strftime('%d/%m/%Y')
            forecast_30_days = forecast_how_many(
                tp_samples=tp_samples,
                start_date=start_date,
                end_date=horizon_30_str,
                n_simulations=n_simulations,
                focus_factor=team_focus_value
            )
            distribution_30 = forecast_30_days.get('distribution') or []
            probability_rows_30 = []
            if distribution_30:
                seen_probs = set()
                for prob in range(100, 0, -5):
                    # FIX: Probability interpretation
                    # 100% probability = percentile 0 (minimum value that occurs in 100% of cases)
                    # 1% probability = percentile 99 (value that only 1% of cases exceed)
                    percentile_value = mc_percentile(distribution_30, (100 - prob) / 100)
                    probability_rows_30.append({
                        'probability': prob,
                        'items': int(round(percentile_value))
                    })
                    seen_probs.add(prob)
                if 1 not in seen_probs:
                    percentile_value = mc_percentile(distribution_30, 0.99)
                    probability_rows_30.append({
                        'probability': 1,
                        'items': int(round(percentile_value))
                    })

            items_forecast_30_days = {
                'start_date': forecast_30_days.get('start_date', start_dt.strftime('%d/%m/%Y')),
                'end_date': forecast_30_days.get('end_date', horizon_30_str),
                'days': forecast_30_days.get('days', 30),
                'weeks': forecast_30_days.get('weeks'),
                'items_mean': forecast_30_days.get('items_mean'),
                'probability_table': probability_rows_30
            }
        except Exception:
            items_forecast_30_days = None

        # For scope completion: how many items from the backlog will be completed by the deadline?
        # This is the MINIMUM between what's possible and what's in the backlog
        projected_work_p95 = min(items_possible_p95, backlog)
        projected_work_p85 = min(items_possible_p85, backlog)
        projected_work_p50 = min(items_possible_p50, backlog)

        # Get completion dates for each percentile ("Quando?")
        # Calculate dates directly from projected weeks to ensure consistency with deadline analysis
        completion_date_p95 = (start_dt + timedelta(weeks=projected_weeks_p95)).strftime('%d/%m/%Y')
        completion_date_p85 = (start_dt + timedelta(weeks=projected_weeks_p85)).strftime('%d/%m/%Y')
        completion_date_p50 = (start_dt + timedelta(weeks=projected_weeks_p50)).strftime('%d/%m/%Y')

        # Calculate percentages - DON'T limit to 100% to show real values
        # scope_completion_pct = how much of the BACKLOG will be completed by the deadline
        scope_completion_pct_raw = (projected_work_p85 / backlog * 100) if backlog > 0 else 100
        # deadline_completion_pct = how much of the DEADLINE TIME will be used
        deadline_completion_pct_raw = (projected_weeks_p85 / weeks_to_deadline * 100) if weeks_to_deadline > 0 else 100

        mc_result = {
            'deadline_date': deadline_dt.strftime('%d/%m/%Y'),
            'start_date': start_dt.strftime('%d/%m/%Y'),
            'weeks_to_deadline': round(weeks_to_deadline, 1),
            'projected_weeks_p85': round(projected_weeks_p85, 1),
            'projected_weeks_p50': round(projected_weeks_p50, 1),
            'projected_weeks_p95': round(projected_weeks_p95, 1),
            'projected_work_p95': int(projected_work_p95),
            'projected_work_p85': int(projected_work_p85),
            'projected_work_p50': int(projected_work_p50),
            'items_possible_p95': int(items_possible_p95),
            'items_possible_p85': int(items_possible_p85),
            'items_possible_p50': int(items_possible_p50),
            'completion_date_p95': completion_date_p95,
            'completion_date_p85': completion_date_p85,
            'completion_date_p50': completion_date_p50,
            'backlog': backlog,
            'can_meet_deadline': can_meet_deadline,
            'scope_completion_pct': round(min(100, scope_completion_pct_raw)),
            'scope_completion_pct_raw': round(scope_completion_pct_raw, 1),
            'deadline_completion_pct': round(min(100, deadline_completion_pct_raw)),
            'deadline_completion_pct_raw': round(deadline_completion_pct_raw, 1),
            'percentile_stats': percentile_stats,
            'deadline_date_raw': deadline_dt.strftime('%Y-%m-%d'),
            'start_date_raw': start_dt.strftime('%Y-%m-%d'),
            'input_stats': input_stats,
            'items_forecast_30_days': items_forecast_30_days
        }

        # Estimated effort (person-weeks) using average contributors
        avg_contributors: Optional[float] = None
        base_contributors = None
        if simulation_data:
            base_contributors = simulation_data.get('totalContributors')
        if base_contributors is None or base_contributors == 0:
            base_contributors = team_size or 1

        min_contrib_val = None
        max_contrib_val = None
        if simulation_data:
            min_contrib_val = simulation_data.get('minContributors')
            max_contrib_val = simulation_data.get('maxContributors')
        if min_contrib_val is None:
            min_contrib_val = min_contributors
        if max_contrib_val is None:
            max_contrib_val = max_contributors

        if min_contrib_val and max_contrib_val:
            avg_contributors = (min_contrib_val + max_contrib_val) / 2
        else:
            avg_contributors = base_contributors or 1

        def effort_for_weeks(weeks_value: float) -> Optional[int]:
            if weeks_value is None:
                return None
            try:
                weeks = float(weeks_value)
            except (TypeError, ValueError):
                return None
            if weeks <= 0 or not avg_contributors:
                return None
            return int(round(weeks * avg_contributors))

        mc_result['projected_effort_p50'] = effort_for_weeks(projected_weeks_p50)
        mc_result['projected_effort_p85'] = effort_for_weeks(projected_weeks_p85)
        mc_result['projected_effort_p95'] = effort_for_weeks(projected_weeks_p95)

        # Machine Learning Analysis (if enough data)
        ml_result = None
        if len(tp_samples) >= 8:
            try:
                # Extract dependencies from simulation_data if available
                dependencies = None
                if simulation_data:
                    dependencies = simulation_data.get('dependencies')

                ml_result = ml_analyze_deadline(
                    tp_samples=tp_samples,
                    backlog=backlog,
                    deadline_date=deadline_date,
                    start_date=start_date,
                    team_size=team_size,
                    min_contributors=min_contributors,
                    max_contributors=max_contributors,
                    s_curve_size=s_curve_size,
                    lt_samples=lt_samples,
                    split_rate_samples=split_rate_samples,
                    n_simulations=min(n_simulations, 1000),
                    dependencies=dependencies
                )
            except Exception as e:
                ml_result = {'error': str(e)}

        mc_result_native = convert_to_native_types(mc_result)
        ml_result_native = convert_to_native_types(ml_result) if ml_result else None

        # Calculate effort-based costs
        cost_analysis = None

        # Calculate costs from Monte Carlo results (always available)
        mc_projected_weeks_p50 = mc_result_native.get('projected_weeks_p50', 0)
        mc_projected_weeks_p85 = mc_result_native.get('projected_weeks_p85', 0)
        mc_projected_weeks_p95 = mc_result_native.get('projected_weeks_p95', 0)

        # Estimate effort for Monte Carlo using team size
        # Effort = average contributors × weeks
        avg_contributors_cost = avg_contributors or (team_size or 1)

        mc_effort_p50 = mc_projected_weeks_p50 * avg_contributors_cost
        mc_effort_p85 = mc_projected_weeks_p85 * avg_contributors_cost
        mc_effort_p95 = mc_projected_weeks_p95 * avg_contributors_cost

        # Calculate costs for Monte Carlo percentiles
        mc_cost_percentiles = calculate_effort_based_cost_with_percentiles(
            effort_percentiles={
                'p50': mc_effort_p50,
                'p85': mc_effort_p85,
                'p95': mc_effort_p95
            },
            cost_per_person_week=cost_per_person_week,
            currency="R$"
        )

        # Calculate main cost for P85
        mc_cost_p85 = calculate_effort_based_cost(
            effort_person_weeks=mc_effort_p85,
            cost_per_person_week=cost_per_person_week,
            currency="R$"
        )

        cost_analysis = {
            'monte_carlo': {
                'cost_p50': calculate_effort_based_cost(mc_effort_p50, cost_per_person_week, "R$"),
                'cost_p85': mc_cost_p85,
                'cost_p95': calculate_effort_based_cost(mc_effort_p95, cost_per_person_week, "R$"),
                'cost_percentiles': mc_cost_percentiles,
                'effort_p50': mc_effort_p50,
                'effort_p85': mc_effort_p85,
                'effort_p95': mc_effort_p95
            },
            'formula': 'Custo = Esforço (pessoa-semanas) × Custo por Pessoa-Semana',
            'explanation': f'Monte Carlo: Com esforço de {mc_effort_p85:.1f} pessoa-semanas e custo de {mc_cost_p85["formatted_per_week"]} por semana, o custo total estimado (P85) é {mc_cost_p85["formatted_total"]}',
            'team_info': {
                'team_size': team_size,
                'avg_contributors': avg_contributors_cost,
                'cost_per_week': cost_per_person_week
            }
        }

        # Add ML costs if available
        if ml_result_native and isinstance(ml_result_native, dict) and 'error' not in ml_result_native:
            # Get effort from ML result (P85 confidence level)
            projected_effort_p85 = ml_result_native.get('projected_effort_p85')

            if projected_effort_p85:
                # Also get effort from percentile stats if available
                percentile_stats = ml_result_native.get('percentile_stats', {})
                projected_weeks_p50 = ml_result_native.get('projected_weeks_p50', 0)
                projected_weeks_p85 = ml_result_native.get('projected_weeks_p85', 0)
                projected_weeks_p95 = percentile_stats.get('p95', 0)

                # Estimate effort for different percentiles using team size
                ml_effort_p50 = projected_weeks_p50 * avg_contributors_cost
                ml_effort_p95 = projected_weeks_p95 * avg_contributors_cost

                # Calculate costs for all percentiles
                ml_cost_percentiles = calculate_effort_based_cost_with_percentiles(
                    effort_percentiles={
                        'p50': ml_effort_p50,
                        'p85': projected_effort_p85,
                        'p95': ml_effort_p95
                    },
                    cost_per_person_week=cost_per_person_week,
                    currency="R$"
                )

                ml_cost_p85 = calculate_effort_based_cost(
                    effort_person_weeks=projected_effort_p85,
                    cost_per_person_week=cost_per_person_week,
                    currency="R$"
                )

                cost_analysis['machine_learning'] = {
                    'cost_p50': calculate_effort_based_cost(ml_effort_p50, cost_per_person_week, "R$"),
                    'cost_p85': ml_cost_p85,
                    'cost_p95': calculate_effort_based_cost(ml_effort_p95, cost_per_person_week, "R$"),
                    'cost_percentiles': ml_cost_percentiles,
                    'effort_p50': ml_effort_p50,
                    'effort_p85': projected_effort_p85,
                    'effort_p95': ml_effort_p95
                }

                cost_analysis['explanation'] += f'\nMachine Learning: Com esforço de {projected_effort_p85:.1f} pessoa-semanas, o custo total estimado (P85) é {ml_cost_p85["formatted_total"]}'

        response_data = {
            'monte_carlo': mc_result_native,
            'machine_learning': ml_result_native,
            'cost_analysis': cost_analysis,
            'consensus': None
        }

        if ml_result_native and isinstance(ml_result_native, dict) and 'error' not in ml_result_native:
            mc_can_meet = mc_result_native.get('can_meet_deadline')
            ml_can_meet = ml_result_native.get('can_meet_deadline')
            mc_weeks = mc_result_native.get('projected_weeks_p85')
            ml_weeks = ml_result_native.get('projected_weeks_p85')

            # Calculate difference in weeks
            weeks_diff = abs((mc_weeks or 0) - (ml_weeks or 0))

            # Calculate percentage difference (use average as base to avoid division by zero)
            avg_weeks = (mc_weeks + ml_weeks) / 2 if (mc_weeks and ml_weeks) else 1
            pct_diff = (weeks_diff / avg_weeks * 100) if avg_weeks > 0 else 0

            # Determine if methods agree based on multiple criteria:
            # 1. Both must agree on deadline outcome (can/cannot meet)
            # 2. Week difference must be less than 20% of average (or less than 4 weeks for small projects)
            deadline_outcome_match = mc_can_meet == ml_can_meet
            weeks_close = weeks_diff < 4 or pct_diff < 20
            both_agree = deadline_outcome_match and weeks_close

            # Generate contextual recommendation
            if both_agree:
                recommendation = 'Ambos os métodos concordam. Alta confiabilidade na previsão.'
            elif not deadline_outcome_match:
                recommendation = 'Divergência crítica: Um método indica sucesso e outro indica risco. Revise os dados e considere coletar mais amostras.'
            elif weeks_diff >= 10:
                recommendation = f'Grande divergência temporal ({weeks_diff:.1f} semanas, {pct_diff:.0f}%). Monte Carlo tende a ser mais conservador com incertezas. Considere usar MC como referência principal.'
            elif weeks_diff >= 4:
                recommendation = f'Divergência moderada ({weeks_diff:.1f} semanas, {pct_diff:.0f}%). Use a previsão mais conservadora (maior) como referência.'
            else:
                recommendation = f'Pequena divergência ({weeks_diff:.1f} semanas). Ambos os métodos fornecem previsões similares.'

            # Explain why they might differ
            explanation = []
            if weeks_diff > 2:
                explanation.append('🔍 <strong>Por que há diferença?</strong>')
                if mc_weeks > ml_weeks:
                    explanation.append('• <strong>Monte Carlo é mais conservador:</strong> Considera toda a variabilidade histórica e incertezas dos dados')
                    explanation.append('• <strong>Machine Learning é mais otimista:</strong> Identifica padrões e tendências nos dados históricos')
                else:
                    explanation.append('• <strong>Machine Learning é mais conservador:</strong> Pode ter detectado tendência de queda no throughput')
                    explanation.append('• <strong>Monte Carlo é mais otimista:</strong> Baseia-se na distribuição histórica completa')

                if pct_diff > 50:
                    explanation.append('• ⚠️ <strong>Divergência muito alta sugere:</strong> Dados insuficientes, alta volatilidade ou mudanças recentes no processo')

            response_data['consensus'] = {
                'both_agree': both_agree,
                'deadline_outcome_match': deadline_outcome_match,
                'weeks_close': weeks_close,
                'difference_weeks': round(weeks_diff, 1),
                'percentage_difference': round(pct_diff, 1),
                'recommendation': recommendation,
                'explanation': '<br>'.join(explanation) if explanation else None,
                'mc_more_conservative': mc_weeks > ml_weeks if (mc_weeks and ml_weeks) else None
            }

        print("=" * 60, flush=True)
        print("DEADLINE ANALYSIS COMPLETED SUCCESSFULLY", flush=True)
        print("=" * 60, flush=True)
        return jsonify(convert_to_native_types(response_data))

    except ValueError as e:
        import traceback
        error_msg = str(e)
        trace_msg = traceback.format_exc()
        print("=" * 60, flush=True)
        print(f"DEADLINE ANALYSIS ERROR (ValueError): {error_msg}", flush=True)
        print(trace_msg, flush=True)
        print("=" * 60, flush=True)
        return jsonify({'error': error_msg, 'trace': trace_msg, 'error_type': 'ValueError'}), 400
    except Exception as e:
        import traceback
        error_msg = str(e)
        trace_msg = traceback.format_exc()
        print("=" * 60, flush=True)
        print(f"DEADLINE ANALYSIS ERROR (Exception): {error_msg}", flush=True)
        print(trace_msg, flush=True)
        print("=" * 60, flush=True)
        return jsonify({'error': error_msg, 'trace': trace_msg, 'error_type': type(e).__name__}), 500


@app.route('/api/forecast-how-many', methods=['POST'])
@login_required
def api_forecast_how_many():
    """
    Forecast how many items in a time period (both MC and ML).

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "startDate": str (DD/MM/YYYY),
        "endDate": str (DD/MM/YYYY),
        "teamSize": int (optional),
        "minContributors": int (optional),
        "maxContributors": int (optional),
        "sCurveSize": int (optional),
        "ltSamples": list[float] (optional),
        "nSimulations": int (optional)
    }
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        team_size = data.get('teamSize', 1)
        min_contributors = data.get('minContributors')
        max_contributors = data.get('maxContributors')
        s_curve_size = data.get('sCurveSize', 0)
        lt_samples = data.get('ltSamples', [])
        n_simulations = data.get('nSimulations', 10000)
        team_focus_raw = data.get('teamFocus')
        try:
            team_focus_value = float(team_focus_raw) if team_focus_raw is not None else 1.0
        except (TypeError, ValueError):
            team_focus_value = 1.0
        team_focus_value = max(0.0, min(1.0, team_focus_value))

        if not tp_samples:
            return jsonify({'error': 'Need throughput samples'}), 400
        if not start_date or not end_date:
            return jsonify({'error': 'Need start date and end date'}), 400

        # Monte Carlo
        mc_result = forecast_how_many(
            tp_samples=tp_samples,
            start_date=start_date,
            end_date=end_date,
            n_simulations=n_simulations,
            focus_factor=team_focus_value
        )

        # Machine Learning
        ml_result = None
        if len(tp_samples) >= 8:
            try:
                scaled_tp_samples = [max(0.0, sample * team_focus_value) for sample in tp_samples]
                ml_result = ml_forecast_how_many(
                    tp_samples=scaled_tp_samples,
                    start_date=start_date,
                    end_date=end_date,
                    team_size=team_size,
                    min_contributors=min_contributors,
                    max_contributors=max_contributors,
                    s_curve_size=s_curve_size,
                    lt_samples=lt_samples,
                    n_simulations=min(n_simulations, 1000)
                )
            except Exception as e:
                ml_result = {'error': str(e)}

        return jsonify({
            'monte_carlo': convert_to_native_types(mc_result),
            'machine_learning': convert_to_native_types(ml_result) if ml_result else None
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/forecast-when', methods=['POST'])
@login_required
def api_forecast_when():
    """
    Forecast when backlog will be completed (both MC and ML).

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "backlog": int,
        "startDate": str (DD/MM/YYYY),
        "teamSize": int (optional),
        "minContributors": int (optional),
        "maxContributors": int (optional),
        "sCurveSize": int (optional),
        "ltSamples": list[float] (optional),
        "splitRateSamples": list[float] (optional),
        "nSimulations": int (optional)
    }
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        backlog = data.get('backlog', 0)
        start_date = data.get('startDate')
        team_size = data.get('teamSize', 1)
        min_contributors = data.get('minContributors')
        max_contributors = data.get('maxContributors')
        s_curve_size = data.get('sCurveSize', 0)
        lt_samples = data.get('ltSamples', [])
        split_rate_samples = data.get('splitRateSamples', [])
        n_simulations = data.get('nSimulations', 10000)
        team_focus_raw = data.get('teamFocus')
        try:
            team_focus_value = float(team_focus_raw) if team_focus_raw is not None else 1.0
        except (TypeError, ValueError):
            team_focus_value = 1.0
        team_focus_value = max(0.0, min(1.0, team_focus_value))

        # Monte Carlo
        mc_result = forecast_when(
            tp_samples=tp_samples,
            backlog=backlog,
            start_date=start_date,
            n_simulations=n_simulations,
            focus_factor=team_focus_value
        )

        # Machine Learning
        ml_result = None
        if len(tp_samples) >= 8:
            try:
                ml_result = ml_forecast_when(
                    tp_samples=[max(0.0, sample * team_focus_value) for sample in tp_samples],
                    backlog=backlog,
                    start_date=start_date,
                    team_size=team_size,
                    min_contributors=min_contributors,
                    max_contributors=max_contributors,
                    s_curve_size=s_curve_size,
                    lt_samples=lt_samples,
                    split_rate_samples=split_rate_samples,
                    n_simulations=min(n_simulations, 1000)
                )
            except Exception as e:
                ml_result = {'error': str(e)}

        return jsonify({
            'monte_carlo': convert_to_native_types(mc_result),
            'machine_learning': convert_to_native_types(ml_result) if ml_result else None
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/cost-analysis', methods=['POST'])
@login_required
def api_cost_analysis():
    """
    Execute cost analysis using PERT-Beta distribution.

    Expected JSON payload:
    {
        "optimistic": float (custo otimista por item),
        "mostLikely": float (custo mais provável por item),
        "pessimistic": float (custo pessimista por item),
        "backlog": int (número de itens),
        "nSimulations": int (optional, default: 10000),
        "avgCostPerItem": float (optional, custo médio histórico),
        "teamSize": int (optional, tamanho da equipe),
        "minContributors": int (optional, contribuidores mínimos),
        "maxContributors": int (optional, contribuidores máximos),
        "tpSamples": str or list (optional, amostras de throughput)
    }

    Returns:
        JSON with cost analysis results
    """
    try:
        data = request.json

        optimistic = data.get('optimistic')
        most_likely = data.get('mostLikely')
        pessimistic = data.get('pessimistic')
        backlog = data.get('backlog')
        n_simulations = data.get('nSimulations', 10000)
        avg_cost_per_item = data.get('avgCostPerItem')
        team_size = data.get('teamSize', 1)
        min_contributors = data.get('minContributors')
        max_contributors = data.get('maxContributors')
        tp_samples_raw = data.get('tpSamples')

        # Parse throughput samples
        throughput_samples = None
        if tp_samples_raw:
            if isinstance(tp_samples_raw, str):
                # Parse string format "5, 6, 7, 4, 8"
                try:
                    throughput_samples = [float(x.strip()) for x in tp_samples_raw.split(',') if x.strip()]
                except ValueError:
                    return jsonify({'error': 'Invalid throughput samples format'}), 400
            elif isinstance(tp_samples_raw, list):
                throughput_samples = [float(x) for x in tp_samples_raw]

        # Validation
        if not all([optimistic, most_likely, pessimistic, backlog]):
            return jsonify({
                'error': 'Optimistic, most likely, pessimistic costs and backlog are required'
            }), 400

        if optimistic < 0 or most_likely < 0 or pessimistic < 0:
            return jsonify({'error': 'Cost values must be non-negative'}), 400

        if not (optimistic < most_likely < pessimistic):
            return jsonify({
                'error': 'Must have: Optimistic < Most Likely < Pessimistic'
            }), 400

        if backlog <= 0:
            return jsonify({'error': 'Backlog must be greater than zero'}), 400

        if n_simulations < 10000:
            return jsonify({'error': 'Minimum 10,000 simulations required'}), 400

        # Run PERT-Beta simulation with team parameters
        results = simulate_pert_beta_cost(
            optimistic=float(optimistic),
            most_likely=float(most_likely),
            pessimistic=float(pessimistic),
            backlog=int(backlog),
            n_simulations=int(n_simulations),
            avg_cost_per_item=float(avg_cost_per_item) if avg_cost_per_item else None,
            team_size=int(team_size),
            throughput_samples=throughput_samples
        )

        # Calculate risk metrics
        risk_metrics = calculate_risk_metrics(results)

        # Combine results
        response_data = {
            'simulation_results': results,
            'risk_metrics': risk_metrics
        }

        return jsonify(convert_to_native_types(response_data))

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# Print registered routes for debugging
print("="*60, flush=True)
print(f"Total routes registered: {len(list(app.url_map.iter_rules()))}", flush=True)
@app.route('/api/dependency-analysis', methods=['POST'])
@login_required
def dependency_analysis():
    """
    Analyze dependencies and their impact on project delivery.

    Expected JSON payload:
    {
        "dependencies": [
            {
                "id": "DEP-001",
                "name": "API Service",
                "source_project": "Mobile App",
                "target_project": "Backend Team",
                "on_time_probability": 0.7,
                "delay_impact_days": 10,
                "criticality": "HIGH"
            }
        ],
        "num_simulations": 10000 (optional)
    }

    Returns:
        JSON with dependency analysis results
    """
    try:
        from dependency_analyzer import DependencyAnalyzer, create_dependencies_from_dict

        data = request.json
        dependencies_data = data.get('dependencies', [])

        if not dependencies_data:
            return jsonify({
                'error': 'No dependencies provided'
            }), 400

        # Validate dependency structure
        for dep in dependencies_data:
            required_fields = ['id', 'name', 'source_project', 'target_project']
            for field in required_fields:
                if field not in dep:
                    return jsonify({
                        'error': f'Dependency missing required field: {field}'
                    }), 400

        # Create dependency objects
        dependencies = create_dependencies_from_dict(dependencies_data)

        # Create analyzer
        analyzer = DependencyAnalyzer(dependencies)

        # Run analysis
        num_simulations = data.get('num_simulations', 10000)
        result = analyzer.analyze(num_simulations=num_simulations)

        # Convert to JSON-serializable format
        return jsonify(convert_to_native_types(result.to_dict()))

    except ImportError:
        return jsonify({
            'error': 'Dependency analysis module not available'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Error analyzing dependencies: {str(e)}'
        }), 500


@app.route('/api/visualize-dependencies', methods=['POST'])
@login_required
def visualize_dependencies():
    """
    Generate visualization for dependency analysis results.

    Expected JSON payload: The result dictionary from dependency analysis

    Returns:
        JSON with base64 encoded image
    """
    try:
        data = request.json or {}
        dep_analysis = data.get('dependency_analysis')

        if not dep_analysis:
            return jsonify({
                'error': 'Missing dependency_analysis data'
            }), 400

        # Create visualizer
        visualizer = ForecastVisualizer()

        # Generate visualization
        image_data_url = visualizer.plot_dependency_impact(dep_analysis)

        # Strip possible data URL prefix so the frontend can add it consistently
        if isinstance(image_data_url, str) and image_data_url.startswith('data:image'):
            _, _, image_b64 = image_data_url.partition(',')
        else:
            image_b64 = image_data_url

        return jsonify({
            'image': image_b64
        })

    except Exception as e:
        return jsonify({
            'error': f'Error generating visualization: {str(e)}'
        }), 500


@app.route('/api/risk-summary', methods=['POST'])
@login_required
def api_risk_summary():
    """
    Calculate risk summary with expected impact and ranking.

    Expected JSON payload:
    {
        "risks": [
            {
                "likelihood": float (0-1 or 0-100),
                "lowImpact": float,
                "mediumImpact": float,
                "highImpact": float,
                "description": str (optional)
            }
        ],
        "tpSamples": list[float] (optional),
        "baselineDurationWeeks": float (optional)
    }

    Returns:
        JSON with risk analysis including:
        - risk_summaries: List of risks with expected impact and ranking
        - total_expected_impact: Total expected impact
        - high_priority_count: Count of high-priority risks
        - recommendations: List of recommended actions
    """
    try:
        data = request.json
        risks = data.get('risks', [])
        tp_samples = data.get('tpSamples')
        baseline_duration_weeks = data.get('baselineDurationWeeks')

        if not risks:
            return jsonify({
                'error': 'No risks provided'
            }), 400

        # Calculate risk summary
        result = calculate_risk_summary(
            risks=risks,
            tp_samples=tp_samples,
            baseline_duration_weeks=baseline_duration_weeks
        )

        return jsonify(convert_to_native_types(result))

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


@app.route('/api/trend-analysis', methods=['POST'])
@login_required
def api_trend_analysis():
    """
    Execute automatic trend analysis for throughput and optional lead time data.

    Expected JSON payload:
    {
        "tpSamples": list[float] or str (comma-separated),
        "ltSamples": list[float] or str (comma-separated, optional),
        "metricName": str (optional, default: "throughput")
    }
    """
    try:
        data = request.json or {}
        tp_samples_raw = data.get('tpSamples')
        lt_samples_raw = data.get('ltSamples', data.get('leadTimeSamples'))
        metric_name = data.get('metricName', 'throughput')

        if tp_samples_raw is None and lt_samples_raw is None:
            return jsonify({'error': 'Provide throughput (tpSamples) or lead time (ltSamples) samples for trend analysis'}), 400

        def parse_samples(raw, label):
            if raw is None:
                return []
            if isinstance(raw, str):
                tokens = [chunk.strip() for chunk in re.split(r'[\s,;\\n]+', raw)]
                values = []
                for token in tokens:
                    if not token:
                        continue
                    try:
                        values.append(float(token.replace(',', '.')))
                    except ValueError:
                        raise ValueError(f'Invalid {label} samples format')
            elif isinstance(raw, list):
                values = []
                for item in raw:
                    try:
                        values.append(float(item))
                    except (TypeError, ValueError):
                        raise ValueError(f'{label} samples must contain numeric values')
            else:
                raise ValueError(f'{label} samples must be provided as list or text')

            return [value for value in values if np.isfinite(value)]

        try:
            throughput_samples = parse_samples(tp_samples_raw, 'Throughput')
            lead_time_samples = parse_samples(lt_samples_raw, 'Lead time')
        except ValueError as parse_error:
            return jsonify({'error': str(parse_error)}), 400

        metrics_results = []
        warnings = []

        if throughput_samples:
            if len(throughput_samples) < 3:
                warnings.append('Pelo menos 3 amostras de throughput são necessárias para analisar tendências.')
            else:
                throughput_result = comprehensive_trend_analysis(
                    throughput_samples,
                    metric_name=metric_name or 'throughput',
                    higher_is_better=True
                )
                throughput_result['metric_key'] = 'throughput'
                throughput_result['display_name'] = 'Throughput'
                metrics_results.append(throughput_result)
        elif tp_samples_raw is not None:
            warnings.append('Pelo menos 3 amostras de throughput são necessárias para analisar tendências.')

        if lead_time_samples:
            if len(lead_time_samples) < 3:
                warnings.append('Pelo menos 3 amostras de lead time são necessárias para analisar tendências.')
            else:
                lead_time_result = comprehensive_trend_analysis(
                    lead_time_samples,
                    metric_name='lead_time',
                    higher_is_better=False
                )
                lead_time_result['metric_key'] = 'lead_time'
                lead_time_result['display_name'] = 'Lead Time'
                metrics_results.append(lead_time_result)
        elif lt_samples_raw not in (None, []):
            warnings.append('Pelo menos 3 amostras de lead time são necessárias para analisar tendências.')

        if not metrics_results:
            message = 'Forneça pelo menos 3 amostras de throughput ou lead time para calcular tendências.'
            return jsonify({'error': message, 'warnings': warnings}), 400

        response_payload = {
            'metrics': metrics_results
        }

        if warnings:
            response_payload['warnings'] = warnings

        primary_metric = None
        for metric in metrics_results:
            if metric.get('metric_key') == 'throughput':
                primary_metric = metric
                break
        if primary_metric is None:
            primary_metric = metrics_results[0]

        # Provide backward-compatible keys for existing consumers
        if primary_metric:
            response_payload.update({
                'metric_name': primary_metric.get('metric_name'),
                'data_points': primary_metric.get('data_points'),
                'trend': primary_metric.get('trend'),
                'seasonality': primary_metric.get('seasonality'),
                'anomalies': primary_metric.get('anomalies'),
                'projections': primary_metric.get('projections'),
                'alerts': primary_metric.get('alerts'),
                'summary': primary_metric.get('summary'),
                'higher_is_better': primary_metric.get('higher_is_better')
            })

        return jsonify(convert_to_native_types(response_payload))

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


# ============================================================================
# FORECAST PERSISTENCE API ENDPOINTS
# ============================================================================

@app.route('/api/projects', methods=['GET', 'POST'])
@login_required
def handle_projects():
    """List all projects or create a new one"""
    session = get_session()
    try:
        if request.method == 'GET':
            projects = scoped_project_query(session).order_by(Project.created_at.desc()).all()
            return jsonify([p.to_dict() for p in projects])

        elif request.method == 'POST':
            data = request.json or {}
            name = data.get('name')
            if not name:
                return jsonify({'error': 'Project name is required'}), 400

            owner_id = current_user.id
            if current_user_is_admin() and data.get('user_id'):
                owner_user = session.get(User, data['user_id'])
                if not owner_user:
                    return jsonify({'error': 'Referenced user not found'}), 404
                owner_id = owner_user.id

            project = Project(
                name=name,
                description=data.get('description'),
                team_size=data.get('team_size', 1),
                user_id=owner_id
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return jsonify(project.to_dict()), 201

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def handle_project(project_id):
    """Get, update, or delete a specific project"""
    session = get_session()
    try:
        project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        if request.method == 'GET':
            return jsonify(project.to_dict())

        elif request.method == 'PUT':
            data = request.json or {}
            if 'name' in data:
                project.name = data['name']
            if 'description' in data:
                project.description = data['description']
            if 'team_size' in data:
                project.team_size = data['team_size']
            if 'status' in data:
                project.status = data['status']
            if 'priority' in data:
                project.priority = data['priority']
            if 'business_value' in data:
                project.business_value = data['business_value']
            if 'risk_level' in data:
                project.risk_level = data['risk_level']
            if 'capacity_allocated' in data:
                project.capacity_allocated = data['capacity_allocated']
            if 'strategic_importance' in data:
                project.strategic_importance = data['strategic_importance']
            if 'start_date' in data:
                project.start_date = data['start_date']
            if 'target_end_date' in data:
                project.target_end_date = data['target_end_date']
            if 'owner' in data:
                project.owner = data['owner']
            if 'stakeholder' in data:
                project.stakeholder = data['stakeholder']
            if 'tags' in data:
                project.tags = json.dumps(data['tags']) if isinstance(data['tags'], list) else data['tags']
            project.updated_at = datetime.utcnow()
            session.commit()
            return jsonify(project.to_dict())

        elif request.method == 'DELETE':
            session.delete(project)
            session.commit()
            return '', 204

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/forecasts', methods=['GET', 'POST'])
@login_required
def handle_forecasts():
    """List forecasts or save a new forecast"""
    session = get_session()
    try:
        if request.method == 'GET':
            # Optional filter by project_id
            project_id = request.args.get('project_id', type=int)
            query = scoped_forecast_query(session).order_by(Forecast.created_at.desc())
            if project_id:
                query = query.filter(Forecast.project_id == project_id)

            forecasts = query.all()
            return jsonify([f.to_summary() for f in forecasts])

        elif request.method == 'POST':
            data = request.json or {}

            # Create or get project
            project_id = data.get('project_id')

            project = None
            if project_id:
                project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()
                if not project:
                    return jsonify({'error': 'Project not found'}), 404
            else:
                owner_id = current_user.id
                if current_user_is_admin() and data.get('user_id'):
                    owner_user = session.get(User, data['user_id'])
                    if not owner_user:
                        return jsonify({'error': 'Referenced user not found'}), 404
                    owner_id = owner_user.id

                project = Project(
                    name=data.get('project_name', 'Unnamed Project'),
                    description=data.get('project_description'),
                    team_size=data.get('team_size', 1),
                    user_id=owner_id
                )
                session.add(project)
                session.flush()
                project_id = project.id

            # Create forecast
            forecast = Forecast(
                project_id=project_id,
                name=data['name'],
                description=data.get('description'),
                forecast_type=data.get('forecast_type', 'deadline'),
                forecast_data=json.dumps(data['forecast_data']),
                input_data=json.dumps(data['input_data']),
                backlog=data.get('backlog'),
                deadline_date=data.get('deadline_date'),
                start_date=data.get('start_date'),
                weeks_to_deadline=data.get('weeks_to_deadline'),
                projected_weeks_p85=data.get('projected_weeks_p85'),
                can_meet_deadline=data.get('can_meet_deadline'),
                scope_completion_pct=data.get('scope_completion_pct'),
                created_by=current_user.email if getattr(current_user, 'email', None) else data.get('created_by'),
                user_id=project.user_id if project else current_user.id
            )

            session.add(forecast)
            session.commit()
            session.refresh(forecast)
            return jsonify(forecast.to_dict()), 201

    except Exception as e:
        session.rollback()
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


@app.route('/api/forecasts/<int:forecast_id>', methods=['GET', 'DELETE'])
@login_required
def handle_forecast(forecast_id):
    """Get or delete a specific forecast"""
    session = get_session()
    try:
        forecast = scoped_forecast_query(session).filter(Forecast.id == forecast_id).one_or_none()
        if not forecast:
            return jsonify({'error': 'Forecast not found'}), 404

        if request.method == 'GET':
            return jsonify(forecast.to_dict())

        elif request.method == 'DELETE':
            session.delete(forecast)
            session.commit()
            return '', 204

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/forecasts/<int:forecast_id>/export', methods=['GET'])
@login_required
def export_forecast(forecast_id):
    """Export a forecast as JSON file"""
    session = get_session()
    try:
        forecast = scoped_forecast_query(session).filter(Forecast.id == forecast_id).one_or_none()
        if not forecast:
            return jsonify({'error': 'Forecast not found'}), 404

        # Return full forecast data as downloadable JSON
        from flask import make_response
        response = make_response(json.dumps(forecast.to_dict(), indent=2))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=forecast_{forecast_id}.json'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/forecasts/import', methods=['POST'])
@login_required
def import_forecast():
    """Import a forecast from JSON"""
    session = get_session()
    try:
        data = request.json or {}

        # Create or get project
        project_id = data.get('project_id')
        project = None
        if project_id:
            project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()
            if not project:
                return jsonify({'error': 'Project not found'}), 404
        else:
            owner_id = current_user.id
            if current_user_is_admin() and data.get('user_id'):
                owner_user = session.get(User, data['user_id'])
                if not owner_user:
                    return jsonify({'error': 'Referenced user not found'}), 404
                owner_id = owner_user.id

            project = Project(
                name=data.get('project_name', 'Imported Project'),
                description=data.get('project_description'),
                team_size=data.get('team_size', 1),
                user_id=owner_id
            )
            session.add(project)
            session.flush()
            project_id = project.id

        # Create forecast from imported data
        forecast = Forecast(
            project_id=project_id,
            name=data.get('name', 'Imported Forecast'),
            description=data.get('description'),
            forecast_type=data.get('forecast_type', 'deadline'),
            forecast_data=json.dumps(data.get('forecast_data', {})),
            input_data=json.dumps(data.get('input_data', {})),
            backlog=data.get('backlog'),
            deadline_date=data.get('deadline_date'),
            start_date=data.get('start_date'),
            weeks_to_deadline=data.get('weeks_to_deadline'),
            projected_weeks_p85=data.get('projected_weeks_p85'),
            can_meet_deadline=data.get('can_meet_deadline'),
            scope_completion_pct=data.get('scope_completion_pct'),
            created_by=current_user.email if getattr(current_user, 'email', None) else data.get('created_by'),
            user_id=project.user_id if project else current_user.id
        )

        session.add(forecast)
        session.commit()
        session.refresh(forecast)
        return jsonify(forecast.to_dict()), 201

    except Exception as e:
        session.rollback()
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


# ============================================================================
# FORECAST VS ACTUAL TRACKING API ENDPOINTS
# ============================================================================

@app.route('/forecast-vs-actual')
@login_required
def forecast_vs_actual_page():
    """Render the Forecast vs Actual dashboard page"""
    try:
        return render_template('forecast_vs_actual.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Forecast vs Actual - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error loading Forecast vs Actual template: {str(e)}</p>
        </body>
        </html>
        """, 500


@app.route('/api/actuals', methods=['GET', 'POST'])
@login_required
def handle_actuals():
    """List actuals or create a new actual record"""
    session = get_session()
    try:
        if request.method == 'GET':
            # Optional filter by forecast_id
            forecast_id = request.args.get('forecast_id', type=int)
            query = scoped_actual_query(session).order_by(Actual.recorded_at.desc())

            if forecast_id:
                query = query.filter(Actual.forecast_id == forecast_id)

            actuals = query.all()
            return jsonify([a.to_dict() for a in actuals])

        elif request.method == 'POST':
            data = request.json or {}

            # Validate forecast exists
            forecast_id = data.get('forecast_id')
            if not forecast_id:
                return jsonify({'error': 'forecast_id is required'}), 400

            forecast = scoped_forecast_query(session).filter(Forecast.id == forecast_id).one_or_none()
            if not forecast:
                return jsonify({'error': 'Forecast not found'}), 404

            # Parse dates
            actual_completion_date = data.get('actual_completion_date')

            # Calculate actual weeks taken if dates provided
            actual_weeks_taken = data.get('actual_weeks_taken')
            if not actual_weeks_taken and actual_completion_date and forecast.start_date:
                try:
                    start_dt = parse_flexible_date(forecast.start_date)
                    end_dt = parse_flexible_date(actual_completion_date)
                    actual_weeks_taken = (end_dt - start_dt).days / 7.0
                except Exception:
                    actual_weeks_taken = None

            # Calculate errors
            weeks_error = None
            weeks_error_pct = None
            if actual_weeks_taken and forecast.projected_weeks_p85:
                weeks_error = actual_weeks_taken - forecast.projected_weeks_p85
                weeks_error_pct = (weeks_error / forecast.projected_weeks_p85) * 100

            scope_error_pct = None
            actual_items_completed = data.get('actual_items_completed')
            if actual_items_completed and forecast.backlog:
                actual_scope_pct = (actual_items_completed / forecast.backlog) * 100
                expected_scope_pct = forecast.scope_completion_pct or 100
                scope_error_pct = actual_scope_pct - expected_scope_pct

            # Create actual record
            actual = Actual(
                forecast_id=forecast_id,
                actual_completion_date=actual_completion_date,
                actual_weeks_taken=actual_weeks_taken,
                actual_items_completed=actual_items_completed,
                actual_scope_delivered_pct=data.get('actual_scope_delivered_pct'),
                weeks_error=weeks_error,
                weeks_error_pct=weeks_error_pct,
                scope_error_pct=scope_error_pct,
                notes=data.get('notes'),
                recorded_by=data.get('recorded_by') or getattr(current_user, 'name', None)
            )

            session.add(actual)
            session.commit()
            session.refresh(actual)
            return jsonify(actual.to_dict()), 201

    except Exception as e:
        session.rollback()
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


@app.route('/api/actuals/<int:actual_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def handle_actual(actual_id):
    """Get, update, or delete a specific actual record"""
    session = get_session()
    try:
        actual = scoped_actual_query(session).filter(Actual.id == actual_id).one_or_none()
        if not actual:
            return jsonify({'error': 'Actual not found'}), 404

        if request.method == 'GET':
            return jsonify(actual.to_dict())

        elif request.method == 'PUT':
            data = request.json

            # Update fields
            if 'actual_completion_date' in data:
                actual.actual_completion_date = data['actual_completion_date']
            if 'actual_weeks_taken' in data:
                actual.actual_weeks_taken = data['actual_weeks_taken']
            if 'actual_items_completed' in data:
                actual.actual_items_completed = data['actual_items_completed']
            if 'actual_scope_delivered_pct' in data:
                actual.actual_scope_delivered_pct = data['actual_scope_delivered_pct']
            if 'notes' in data:
                actual.notes = data['notes']

            # Recalculate errors
            forecast = actual.forecast
            if actual.actual_weeks_taken and forecast.projected_weeks_p85:
                actual.weeks_error = actual.actual_weeks_taken - forecast.projected_weeks_p85
                actual.weeks_error_pct = (actual.weeks_error / forecast.projected_weeks_p85) * 100

            actual.recorded_at = datetime.utcnow()
            session.commit()
            return jsonify(actual.to_dict())

        elif request.method == 'DELETE':
            session.delete(actual)
            session.commit()
            return '', 204

    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/accuracy-analysis', methods=['GET'])
@login_required
def accuracy_analysis():
    """
    Calculate accuracy metrics for forecasts vs actuals.

    Query parameters:
        - forecast_id: Optional, analyze specific forecast
        - project_id: Optional, analyze all forecasts for a project
        - limit: Optional, limit number of records (default: 100)
    """
    session = get_session()
    try:
        forecast_id = request.args.get('forecast_id', type=int)
        project_id = request.args.get('project_id', type=int)
        limit = request.args.get('limit', type=int, default=100)

        # Build query
        query = session.query(Forecast, Actual).join(
            Actual, Forecast.id == Actual.forecast_id
        )

        if not current_user_is_admin():
            query = query.filter(Forecast.user_id == current_user.id)

        if forecast_id:
            query = query.filter(Forecast.id == forecast_id)
        elif project_id:
            query = query.filter(Forecast.project_id == project_id)

        records = query.order_by(Forecast.created_at.desc()).limit(limit).all()

        if not records:
            return jsonify({
                'error': 'No forecast-actual pairs found',
                'metrics': None
            }), 404

        # Extract forecasts and actuals
        forecasts_p85 = []
        actuals_weeks = []
        dates = []
        tp_samples_list = []

        for forecast, actual in records:
            if forecast.projected_weeks_p85 and actual.actual_weeks_taken:
                forecasts_p85.append(forecast.projected_weeks_p85)
                actuals_weeks.append(actual.actual_weeks_taken)
                dates.append(forecast.created_at)

                # Try to extract throughput samples from input_data
                try:
                    input_data = json.loads(forecast.input_data)
                    tp_samples = input_data.get('tpSamples', [])
                    if tp_samples:
                        tp_samples_list.append(tp_samples)
                except:
                    pass

        if len(forecasts_p85) < 2:
            return jsonify({
                'error': 'Need at least 2 forecast-actual pairs for meaningful analysis',
                'count': len(forecasts_p85)
            }), 400

        # Calculate accuracy metrics
        metrics = calculate_accuracy_metrics(forecasts_p85, actuals_weeks)

        # Calculate time-series metrics
        ts_metrics = calculate_time_series_metrics(
            forecasts_p85,
            actuals_weeks,
            dates
        )

        # Detect data quality issues
        avg_tp_samples = tp_samples_list[0] if tp_samples_list else None
        issues = detect_data_quality_issues(
            forecasts_p85,
            actuals_weeks,
            avg_tp_samples
        )

        # Generate recommendations
        recommendations = generate_recommendations(metrics, issues)

        # Get quality ratings
        quality_ratings = metrics.get_quality_rating()

        # Prepare detailed comparison data
        comparisons = []
        for forecast, actual in records:
            if forecast.projected_weeks_p85 and actual.actual_weeks_taken:
                comparisons.append({
                    'forecast_id': forecast.id,
                    'forecast_name': forecast.name,
                    'project_name': forecast.project.name if forecast.project else None,
                    'created_at': forecast.created_at.isoformat(),
                    'forecasted_weeks': round(forecast.projected_weeks_p85, 2),
                    'actual_weeks': round(actual.actual_weeks_taken, 2),
                    'error_weeks': round(actual.weeks_error, 2) if actual.weeks_error else None,
                    'error_pct': round(actual.weeks_error_pct, 2) if actual.weeks_error_pct else None,
                    'backlog': forecast.backlog,
                    'notes': actual.notes
                })

        return jsonify({
            'metrics': metrics.to_dict(),
            'time_series_metrics': ts_metrics,
            'quality_ratings': quality_ratings,
            'issues': issues,
            'recommendations': recommendations,
            'comparisons': comparisons,
            'summary': {
                'total_comparisons': len(comparisons),
                'date_range': {
                    'first': dates[-1].isoformat() if dates else None,
                    'last': dates[0].isoformat() if dates else None
                }
            }
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


@app.route('/api/forecast-vs-actual/dashboard', methods=['GET'])
@login_required
def forecast_vs_actual_dashboard_data():
    """
    Get comprehensive dashboard data for forecast vs actual analysis.
    Includes summary statistics, recent comparisons, and trends.
    """
    session = get_session()
    try:
        # Get all forecast-actual pairs
        query = session.query(Forecast, Actual).join(
            Actual, Forecast.id == Actual.forecast_id
        )

        if not current_user_is_admin():
            query = query.filter(Forecast.user_id == current_user.id)

        records = query.order_by(Forecast.created_at.desc()).limit(100).all()

        if not records:
            return jsonify({
                'has_data': False,
                'message': 'Nenhum dado de forecast vs actual disponível. Registre resultados reais para começar.'
            })

        # Calculate overall metrics
        forecasts_p85 = []
        actuals_weeks = []

        for forecast, actual in records:
            if forecast.projected_weeks_p85 and actual.actual_weeks_taken:
                forecasts_p85.append(forecast.projected_weeks_p85)
                actuals_weeks.append(actual.actual_weeks_taken)

        if len(forecasts_p85) < 2:
            return jsonify({
                'has_data': False,
                'message': f'Apenas {len(forecasts_p85)} comparações disponíveis. Mínimo: 2.'
            })

        metrics = calculate_accuracy_metrics(forecasts_p85, actuals_weeks)
        quality_ratings = metrics.get_quality_rating()

        # Get project-wise breakdown
        project_stats = {}
        for forecast, actual in records:
            if not forecast.project or not forecast.projected_weeks_p85 or not actual.actual_weeks_taken:
                continue

            project_name = forecast.project.name
            if project_name not in project_stats:
                project_stats[project_name] = {
                    'forecasts': [],
                    'actuals': [],
                    'count': 0
                }

            project_stats[project_name]['forecasts'].append(forecast.projected_weeks_p85)
            project_stats[project_name]['actuals'].append(actual.actual_weeks_taken)
            project_stats[project_name]['count'] += 1

        # Calculate metrics per project
        project_metrics = {}
        for project_name, data in project_stats.items():
            if len(data['forecasts']) >= 2:
                try:
                    proj_metrics = calculate_accuracy_metrics(data['forecasts'], data['actuals'])
                    project_metrics[project_name] = {
                        'mape': proj_metrics.mape,
                        'accuracy_rate': proj_metrics.accuracy_rate,
                        'count': data['count'],
                        'bias': proj_metrics.bias_direction
                    }
                except:
                    pass

        # Recent comparisons (last 10)
        recent_comparisons = []
        for forecast, actual in records[:10]:
            if forecast.projected_weeks_p85 and actual.actual_weeks_taken:
                recent_comparisons.append({
                    'forecast_id': forecast.id,
                    'forecast_name': forecast.name,
                    'project_name': forecast.project.name if forecast.project else None,
                    'created_at': forecast.created_at.isoformat(),
                    'forecasted_weeks': round(forecast.projected_weeks_p85, 2),
                    'actual_weeks': round(actual.actual_weeks_taken, 2),
                    'error_pct': round(actual.weeks_error_pct, 2) if actual.weeks_error_pct else None
                })

        return jsonify({
            'has_data': True,
            'overall_metrics': metrics.to_dict(),
            'quality_ratings': quality_ratings,
            'project_metrics': project_metrics,
            'recent_comparisons': recent_comparisons,
            'summary': {
                'total_comparisons': len(forecasts_p85),
                'total_projects': len(project_metrics),
                'overall_quality': quality_ratings['overall']
            }
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


@app.route('/api/backtest', methods=['POST'])
@login_required
def api_backtest():
    """
    Run backtesting on historical throughput data.

    Expected JSON payload:
    {
        "tpSamples": list[float],
        "backlog": int,
        "method": "walk_forward" or "expanding_window" (default: walk_forward),
        "minTrainSize": int (default: 5),
        "testSize": int (default: 1) - Number of periods to forecast,
        "foldStride": int (default: 1) - Number of periods to advance between forecasts,
        "confidenceLevel": "P50", "P85", or "P95" (default: P85),
        "nSimulations": int (default: 10000),
        "compareConfidenceLevels": bool (default: false)
    }

    Examples:
        Standard walk-forward (every period):
            {"foldStride": 1, "testSize": 1}

        Weekly updates with 30-day horizon (daily data):
            {"foldStride": 7, "testSize": 30}

        Bi-weekly updates with 60-day horizon:
            {"foldStride": 14, "testSize": 60}

    Returns:
        JSON with backtest results
    """
    try:
        data = request.json
        tp_samples = data.get('tpSamples', [])
        backlog = data.get('backlog', 0)
        method = data.get('method', 'walk_forward')
        min_train_size = data.get('minTrainSize', 5)
        test_size = data.get('testSize', 1)
        fold_stride = data.get('foldStride', 1)
        confidence_level = data.get('confidenceLevel', 'P85')
        n_simulations = data.get('nSimulations', 10000)
        compare_levels = data.get('compareConfidenceLevels', False)

        # Validation
        if not tp_samples or len(tp_samples) < min_train_size + 1:
            return jsonify({
                'error': f'Need at least {min_train_size + 1} throughput samples for backtesting. Got {len(tp_samples)}.'
            }), 400

        if backlog <= 0:
            return jsonify({'error': 'Backlog must be greater than zero'}), 400

        if method not in ['walk_forward', 'expanding_window']:
            return jsonify({'error': 'Method must be "walk_forward" or "expanding_window"'}), 400

        # Run backtesting
        if compare_levels:
            # Compare across confidence levels
            results_by_level = compare_confidence_levels(
                tp_samples,
                backlog,
                min_train_size=min_train_size,
                test_size=test_size,
                fold_stride=fold_stride,
                n_simulations=n_simulations
            )

            response = {
                'method': 'comparison',
                'test_size': test_size,
                'fold_stride': fold_stride,
                'results_by_level': {}
            }

            for level, summary in results_by_level.items():
                if summary:
                    response['results_by_level'][level] = summary.to_dict()
                    response['results_by_level'][level]['report'] = generate_backtest_report(summary)
                else:
                    response['results_by_level'][level] = None

        else:
            # Single backtest
            if method == 'walk_forward':
                summary = run_walk_forward_backtest(
                    tp_samples,
                    backlog,
                    min_train_size=min_train_size,
                    test_size=test_size,
                    fold_stride=fold_stride,
                    confidence_level=confidence_level,
                    n_simulations=n_simulations
                )
            else:  # expanding_window
                summary = run_expanding_window_backtest(
                    tp_samples,
                    backlog,
                    initial_train_size=min_train_size,
                    confidence_level=confidence_level,
                    n_simulations=n_simulations
                )

            response = {
                'method': method,
                'test_size': test_size,
                'fold_stride': fold_stride if method == 'walk_forward' else None,
                'summary': summary.to_dict(),
                'report': generate_backtest_report(summary)
            }

        return jsonify(convert_to_native_types(response))

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


# ============================================================================
# PORTFOLIO MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/portfolio/dashboard', methods=['GET'])
@login_required
def portfolio_dashboard():
    """
    Get comprehensive portfolio dashboard data.
    Includes health scores, capacity analysis, prioritization matrix, and alerts.
    """
    session = get_session()
    try:
        # Get all projects
        projects = scoped_project_query(session).all()

        if not projects:
            return jsonify({
                'has_data': False,
                'message': 'Nenhum projeto cadastrado. Crie projetos para visualizar o portfolio.'
            })

        # Get forecasts for each project
        all_forecasts = scoped_forecast_query(session).all()
        forecasts_by_project = {}
        for forecast in all_forecasts:
            if forecast.project_id not in forecasts_by_project:
                forecasts_by_project[forecast.project_id] = []
            forecasts_by_project[forecast.project_id].append(forecast)

        # Get actuals mapped by forecast_id
        all_actuals = scoped_actual_query(session).all()
        actuals_map = {}
        for actual in all_actuals:
            if actual.forecast_id not in actuals_map:
                actuals_map[actual.forecast_id] = []
            actuals_map[actual.forecast_id].append(actual)

        # Calculate health scores for each project
        health_scores = []
        for project in projects:
            project_forecasts = forecasts_by_project.get(project.id, [])
            health_score = calculate_project_health_score(
                project,
                project_forecasts,
                actuals_map
            )
            health_scores.append(health_score)

        # Analyze capacity
        capacity_analysis = analyze_portfolio_capacity(projects)

        # Create prioritization matrix
        prioritization_matrix = create_prioritization_matrix(projects)

        # Generate alerts
        alerts = generate_portfolio_alerts(projects, health_scores, capacity_analysis)

        # Portfolio summary
        active_projects = [p for p in projects if p.status == 'active']
        total_business_value = sum(p.business_value for p in active_projects)
        avg_health_score = np.mean([hs.overall_score for hs in health_scores]) if health_scores else 0

        return jsonify({
            'has_data': True,
            'summary': {
                'total_projects': len(projects),
                'active_projects': len(active_projects),
                'completed_projects': len([p for p in projects if p.status == 'completed']),
                'on_hold_projects': len([p for p in projects if p.status == 'on_hold']),
                'total_business_value': total_business_value,
                'avg_health_score': round(avg_health_score, 2)
            },
            'health_scores': [hs.to_dict() for hs in health_scores],
            'capacity_analysis': capacity_analysis.to_dict(),
            'prioritization_matrix': prioritization_matrix.to_dict(),
            'alerts': alerts,
            'projects': [p.to_dict() for p in projects]
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500
    finally:
        session.close()


@app.route('/api/portfolio/health/<int:project_id>', methods=['GET'])
@login_required
def project_health_details(project_id):
    """Get detailed health analysis for a specific project."""
    session = get_session()
    try:
        project = scoped_project_query(session).filter(Project.id == project_id).one_or_none()
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Get forecasts and actuals
        forecasts = scoped_forecast_query(session).filter(Forecast.project_id == project_id).all()

        actuals_map = {}
        forecast_ids = [f.id for f in forecasts]
        if forecast_ids:
            actuals = scoped_actual_query(session).filter(Actual.forecast_id.in_(forecast_ids)).all()
            for actual in actuals:
                actuals_map.setdefault(actual.forecast_id, []).append(actual)

        # Calculate health score
        health_score = calculate_project_health_score(project, forecasts, actuals_map)

        return jsonify({
            'project': project.to_dict(),
            'health_score': health_score.to_dict(),
            'forecasts': [f.to_summary() for f in forecasts],
            'actuals_count': sum(len(a) for a in actuals_map.values())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/portfolio/capacity', methods=['GET'])
@login_required
def portfolio_capacity():
    """Get portfolio capacity analysis."""
    session = get_session()
    try:
        projects = scoped_project_query(session).all()

        # Get total capacity from query params (optional)
        total_capacity = request.args.get('total_capacity', type=float)

        capacity_analysis = analyze_portfolio_capacity(projects, total_capacity)

        return jsonify(capacity_analysis.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/portfolio/prioritization', methods=['GET'])
@login_required
def portfolio_prioritization():
    """Get prioritization matrix for portfolio."""
    session = get_session()
    try:
        projects = scoped_project_query(session).all()
        prioritization_matrix = create_prioritization_matrix(projects)

        return jsonify(prioritization_matrix.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ============================================================================
# Cost of Delay (CoD) API Endpoints
# ============================================================================

# Global CoD forecaster caches
_default_cod_forecaster = None
_cod_forecasters_by_user = {}


def _load_default_cod_forecaster():
    """Load the shared default CoD forecaster (trained with synthetic data)."""
    global _default_cod_forecaster
    if _default_cod_forecaster is None:
        _default_cod_forecaster = CoDForecaster()
        try:
            sample_data = generate_sample_cod_data(n_samples=100)
            _default_cod_forecaster.train_models(sample_data, use_hyperparam_search=False)
            print("CoD Forecaster initialized with sample data", flush=True)
        except Exception as exc:
            print(f"Warning: Could not initialize default CoD forecaster: {exc}", flush=True)
    return _default_cod_forecaster


def _load_user_cod_forecaster(user_id: int):
    """Load a user-specific CoD forecaster from cache or database."""
    if user_id in _cod_forecasters_by_user:
        return _cod_forecasters_by_user[user_id]

    session = get_session()
    try:
        cod_model = (
            session.query(CoDModel)
            .filter(CoDModel.user_id == user_id)
            .one_or_none()
        )
        if cod_model and cod_model.model_blob:
            try:
                forecaster = pickle.loads(cod_model.model_blob)
                _cod_forecasters_by_user[user_id] = forecaster
                return forecaster
            except Exception as exc:
                print(f"Warning: Could not unpickle CoD model for user {user_id}: {exc}", flush=True)
    finally:
        session.close()

    return None


def invalidate_user_cod_cache(user_id: int):
    """Remove a user-specific forecaster from the in-memory cache."""
    _cod_forecasters_by_user.pop(user_id, None)


def get_cod_forecaster():
    """Return the appropriate CoD forecaster for the current context."""
    user_id = getattr(current_user, 'id', None) if getattr(current_user, 'is_authenticated', False) else None

    if user_id:
        user_forecaster = _load_user_cod_forecaster(user_id)
        if user_forecaster:
            return user_forecaster

    return _load_default_cod_forecaster()


def get_user_cod_assets(user_id: int):
    """Fetch persisted CoD dataset and model for a user."""
    session = get_session()
    try:
        dataset = (
            session.query(CoDTrainingDataset)
            .filter(CoDTrainingDataset.user_id == user_id)
            .order_by(CoDTrainingDataset.created_at.desc())
            .first()
        )
        model = (
            session.query(CoDModel)
            .filter(CoDModel.user_id == user_id)
            .one_or_none()
        )
        return dataset, model
    finally:
        session.close()


def _normalize_cod_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names for CoD datasets."""
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    rename_map = {}
    lower_map = {col.lower(): col for col in df.columns}
    for expected in COD_REQUIRED_COLUMNS.union(COD_OPTIONAL_COLUMNS):
        lower_expected = expected.lower()
        original = lower_map.get(lower_expected)
        if original and original != expected:
            rename_map[original] = expected
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def load_cod_dataframe(file_storage) -> pd.DataFrame:
    """Load and validate a CSV file containing CoD training data."""
    try:
        df = pd.read_csv(file_storage)
    except Exception as exc:
        raise ValueError(f'Não foi possível ler o CSV: {exc}')

    df = _normalize_cod_dataframe(df)
    missing = COD_REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f'Colunas obrigatórias ausentes: {", ".join(sorted(missing))}')

    numeric_columns = [col for col in COD_REQUIRED_COLUMNS if col not in {'project_type'}]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    df = df.dropna(subset=numeric_columns)
    df = df[df['team_size'] > 0]
    df = df[df['duration_weeks'] > 0]
    df = df[df['cod_weekly'] > 0]
    df = df[df['num_stakeholders'] >= 0]

    if 'project_type' in df.columns:
        df['project_type'] = df['project_type'].fillna('Unknown').astype(str)

    if 'risk_level' in df.columns:
        df['risk_level'] = pd.to_numeric(df['risk_level'], errors='coerce')
        df = df.dropna(subset=['risk_level'])

    df = df.reset_index(drop=True)

    if len(df) < 10:
        raise ValueError('É necessário pelo menos 10 linhas válidas para treinar o modelo.')

    return df


@app.route('/downloads/cod-sample', methods=['GET'])
@login_required
def download_cod_sample():
    """Provide the sample CoD CSV for users."""
    if not COD_SAMPLE_PATH.exists():
        return jsonify({'error': 'Sample dataset indisponível no servidor.'}), 404
    return send_file(
        str(COD_SAMPLE_PATH),
        mimetype='text/csv',
        as_attachment=True,
        download_name='cod_training_sample.csv'
    )


@app.route('/api/cod/dataset', methods=['GET'])
@login_required
def cod_dataset_status():
    """Return metadata about the user's CoD training dataset and model."""
    user_id = current_user.id
    dataset, model = get_user_cod_assets(user_id)

    dataset_payload = dataset.to_dict() if dataset else None

    has_model = bool(model and model.model_blob)
    model_payload = None
    if has_model:
        model_payload = {
            'id': model.id,
            'trained_at': model.trained_at.isoformat() if model.trained_at else None,
            'sample_count': model.sample_count,
            'metrics': model.get_metrics(),
            'feature_names': json.loads(model.feature_names) if model.feature_names else None,
            'project_types': json.loads(model.project_types) if model.project_types else None,
        }

    retrain_required = False
    if dataset and (not has_model or not model.trained_at or (dataset.created_at and dataset.created_at > model.trained_at)):
        retrain_required = True

    return jsonify({
        'has_dataset': bool(dataset),
        'dataset': dataset_payload,
        'has_model': has_model,
        'model': model_payload,
        'retrain_required': retrain_required,
        'active_model_source': 'custom' if has_model else 'default'
    })


@app.route('/api/cod/dataset', methods=['POST'])
@login_required
def upload_cod_dataset():
    """Upload and persist a CoD training dataset for the logged-in user."""
    if 'file' not in request.files:
        return jsonify({'error': 'Envie um arquivo CSV com os dados.'}), 400

    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'Envie um arquivo CSV com os dados.'}), 400

    dataset_name = request.form.get('name', '').strip()
    if not dataset_name:
        dataset_name = os.path.splitext(file.filename)[0]

    try:
        df = load_cod_dataframe(file)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    records = json.loads(df.to_json(orient='records'))
    column_names = df.columns.tolist()

    session = get_session()
    dataset_payload = None
    try:
        dataset = (
            session.query(CoDTrainingDataset)
            .filter(CoDTrainingDataset.user_id == current_user.id)
            .one_or_none()
        )
        if dataset is None:
            dataset = CoDTrainingDataset(user_id=current_user.id)

        dataset.name = dataset_name
        dataset.original_filename = file.filename
        dataset.data = json.dumps(records)
        dataset.column_names = json.dumps(column_names)
        dataset.row_count = len(records)
        dataset.created_at = datetime.utcnow()

        session.add(dataset)
        session.commit()
        dataset_payload = dataset.to_dict()
    except Exception as exc:
        session.rollback()
        return jsonify({'error': f'Falha ao salvar dataset: {exc}'}), 500
    finally:
        session.close()

    return jsonify({
        'message': 'Dataset carregado com sucesso.',
        'dataset': dataset_payload,
        'retrain_required': True
    })


@app.route('/api/cod/train', methods=['POST'])
@login_required
def train_cod_model():
    """Train and persist a user-specific CoD model."""
    user_id = current_user.id
    dataset, _ = get_user_cod_assets(user_id)

    if not dataset:
        return jsonify({'error': 'Nenhum dataset encontrado. Faça upload de um CSV antes de treinar.'}), 400

    try:
        records = json.loads(dataset.data)
        df = pd.DataFrame(records)
        df = _normalize_cod_dataframe(df)
        numeric_columns = [col for col in COD_REQUIRED_COLUMNS if col not in {'project_type'}]
        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        df = df.dropna(subset=numeric_columns)
        forecaster = CoDForecaster()
        options = request.get_json(silent=True)
        full_search = isinstance(options, dict) and options.get('full_search')
        search_iterations = 30 if full_search else 12
        forecaster.train_models(
            df,
            use_hyperparam_search=True,
            search_iterations=search_iterations
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        return jsonify({'error': f'Falha ao treinar o modelo: {exc}'}), 500

    metrics_summary = {}
    for model_name, model_data in forecaster.models.items():
        metrics_summary[model_name] = {
            'mae': float(model_data['mae']),
            'rmse': float(model_data['rmse']),
            'r2': float(model_data['r2']),
            'mape': float(model_data['mape']),
            'best_params': model_data.get('best_params'),
        }

    feature_names_json = json.dumps(forecaster.feature_names)
    project_types_json = json.dumps(forecaster.project_types)
    model_blob = pickle.dumps(forecaster)

    session = get_session()
    try:
        cod_model = (
            session.query(CoDModel)
            .filter(CoDModel.user_id == user_id)
            .one_or_none()
        )
        if cod_model is None:
            cod_model = CoDModel(user_id=user_id)

        cod_model.model_blob = model_blob
        cod_model.metrics = json.dumps(metrics_summary)
        cod_model.sample_count = len(df)
        cod_model.feature_names = feature_names_json
        cod_model.project_types = project_types_json
        cod_model.trained_at = datetime.utcnow()

        session.add(cod_model)
        session.commit()

        model_payload = {
            'trained_at': cod_model.trained_at.isoformat() if cod_model.trained_at else None,
            'sample_count': cod_model.sample_count,
            'metrics': metrics_summary,
            'feature_names': forecaster.feature_names,
            'project_types': forecaster.project_types,
        }
    except Exception as exc:
        session.rollback()
        return jsonify({'error': f'Falha ao salvar o modelo treinado: {exc}'}), 500
    finally:
        session.close()

    _cod_forecasters_by_user[user_id] = forecaster

    return jsonify({
        'message': 'Modelo de CoD treinado com sucesso.',
        'model': model_payload
    })


@app.route('/api/cod/predict', methods=['POST'])
@login_required
def predict_cod():
    """Predict Cost of Delay for a project."""
    try:
        data = request.json

        # Validate required fields
        required = ['budget_millions', 'duration_weeks', 'team_size',
                   'num_stakeholders', 'business_value', 'complexity']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if getattr(current_user, 'is_authenticated', False):
            dataset, model = get_user_cod_assets(current_user.id)
            if dataset and (not model or not model.model_blob):
                return jsonify({
                    'error': 'Carregue e treine seu modelo de CoD antes de realizar previsões.',
                    'retrain_required': True
                }), 409
            if dataset and model and model.trained_at and dataset.created_at and dataset.created_at > model.trained_at:
                return jsonify({
                    'error': 'Seu dataset foi atualizado. Re-treine o modelo para usar as previsões.',
                    'retrain_required': True
                }), 409

        # Get forecaster
        forecaster = get_cod_forecaster()

        if not forecaster.trained:
            return jsonify({'error': 'CoD model not trained yet'}), 503

        # Predict
        result = forecaster.predict_cod(data)

        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/cod/calculate_total', methods=['POST'])
@login_required
def calculate_total_cod():
    """Calculate total CoD for a given delay."""
    try:
        data = request.json

        cod_weekly = float(data['cod_weekly'])
        delay_weeks = float(data['delay_weeks'])

        forecaster = get_cod_forecaster()
        result = forecaster.calculate_total_cod(cod_weekly, delay_weeks)

        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/cod/feature_importance', methods=['GET'])
@login_required
def cod_feature_importance():
    """Get feature importance for CoD model."""
    try:
        if getattr(current_user, 'is_authenticated', False):
            dataset, model = get_user_cod_assets(current_user.id)
            if dataset and (not model or not model.model_blob):
                return jsonify({'error': 'Modelo ainda não treinado com o dataset atual.', 'retrain_required': True}), 409
            if dataset and model and model.trained_at and dataset.created_at and dataset.created_at > model.trained_at:
                return jsonify({'error': 'Re-treine o modelo após atualizar o dataset.', 'retrain_required': True}), 409

        forecaster = get_cod_forecaster()

        if not forecaster.trained:
            return jsonify({'error': 'CoD model not trained yet'}), 503

        importance_df = forecaster.get_feature_importance()

        if importance_df is None:
            return jsonify({'error': 'Feature importance not available'}), 404

        return jsonify({
            'features': importance_df.to_dict('records')
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/cod/model_info', methods=['GET'])
@login_required
def cod_model_info():
    """Get information about the trained CoD model."""
    try:
        dataset = None
        model_record = None

        if getattr(current_user, 'is_authenticated', False):
            dataset, model_record = get_user_cod_assets(current_user.id)
            if dataset and (not model_record or not model_record.model_blob):
                return jsonify({
                    'trained': False,
                    'error': 'Modelo ainda não treinado com o dataset atual.',
                    'retrain_required': True,
                    'dataset': dataset.to_dict() if dataset else None
                }), 200
            if dataset and model_record and model_record.trained_at and dataset.created_at and dataset.created_at > model_record.trained_at:
                return jsonify({
                    'trained': False,
                    'error': 'O dataset foi atualizado após o último treinamento. Re-treine o modelo.',
                    'retrain_required': True,
                    'dataset': dataset.to_dict()
                }), 200

        forecaster = get_cod_forecaster()

        if not forecaster.trained:
            return jsonify({'trained': False, 'error': 'Model not trained yet'}), 200

        models_info = {}
        for name, data in forecaster.models.items():
            models_info[name] = {
                'mae': float(data['mae']),
                'rmse': float(data['rmse']),
                'r2': float(data['r2']),
                'mape': float(data['mape']),
                'best_params': data.get('best_params'),
            }

        source = 'custom' if model_record and model_record.model_blob else 'default'

        response = {
            'trained': True,
            'models': models_info,
            'features': forecaster.feature_names,
            'project_types': getattr(forecaster, 'project_types', []),
            'source': source
        }

        if model_record:
            response['trained_at'] = model_record.trained_at.isoformat() if model_record.trained_at else None
            response['sample_count'] = model_record.sample_count
            response['metrics_snapshot'] = model_record.get_metrics()

        if dataset:
            response['dataset'] = dataset.to_dict()

        return jsonify(response)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# ============================================================================
# Register Async Endpoints (Celery Background Tasks)
# ============================================================================
try:
    from app_async_endpoints import register_async_endpoints
    register_async_endpoints(app)
    print("[INFO] Async endpoints registered successfully", flush=True)
except ImportError as e:
    print(f"[WARNING] Celery/Async endpoints not available: {e}", flush=True)
    print("[WARNING] Application will run in synchronous mode only", flush=True)

# ============================================================================
# Print all registered routes
# ============================================================================
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint:30s} {rule.rule}", flush=True)
print("="*60, flush=True)
sys.stdout.flush()


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
