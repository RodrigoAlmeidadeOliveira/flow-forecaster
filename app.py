"""
Project Forecaster - Flask Application
Monte Carlo simulation for project forecasting
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import base64
import numpy as np
from datetime import datetime
from monte_carlo import run_monte_carlo_simulation, simulate_throughput_forecast
from monte_carlo_unified import analyze_deadline, forecast_how_many, forecast_when
from ml_forecaster import MLForecaster
from ml_deadline_forecaster import ml_analyze_deadline, ml_forecast_how_many, ml_forecast_when
from visualization import ForecastVisualizer
from cost_pert_beta import simulate_pert_beta_cost, calculate_risk_metrics

app = Flask(__name__)

# Debugging: Print routes at startup
print("="*60)
print("Flask app created successfully!")
print(f"App name: {app.name}")
print("="*60)


def convert_to_native_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj


@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok", "routes": len(list(app.url_map.iter_rules()))}


@app.route('/')
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
def advanced():
    """Redirect to the unified advanced forecasting section."""
    return redirect(url_for('index') + '#advanced-forecast')


@app.route('/api/simulate', methods=['POST'])
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

        # Run the simulation
        result = run_monte_carlo_simulation(simulation_data)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/encode', methods=['POST'])
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

        if not tp_samples or len(tp_samples) < 8:
            return jsonify({
                'error': 'Need at least 8 historical throughput samples for ML forecasting'
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


@app.route('/api/mc-throughput', methods=['POST'])
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

        if not tp_samples or len(tp_samples) < 8:
            return jsonify({
                'error': 'Need at least 8 historical throughput samples'
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
        return jsonify(response_data)

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/deadline-analysis')
def deadline_analysis_page():
    """Render the deadline analysis page."""
    return render_template('deadline_analysis.html')


@app.route('/api/deadline-analysis', methods=['POST'])
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
        "nSimulations": int (optional, default: 10000)
    }

    Returns:
        JSON with deadline analysis results from both methods
    """
    try:
        data = request.json

        def parse_date(date_str: str) -> datetime:
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
        simulation_payload = data.get('simulationData')

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

        if not tp_samples:
            return jsonify({'error': 'Need throughput samples'}), 400
        if not deadline_date or not start_date:
            return jsonify({'error': 'Need start date and deadline date'}), 400
        if backlog <= 0:
            return jsonify({'error': 'Backlog must be greater than zero'}), 400

        try:
            start_dt = parse_date(start_date)
            deadline_dt = parse_date(deadline_date)
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
                n_simulations=n_simulations
            )
            percentile_stats = mc_basic.get('percentile_stats', {})
            projected_weeks_p85 = float(percentile_stats.get('p85', 0))
            projected_weeks_p50 = float(percentile_stats.get('p50', 0))
            projected_weeks_p95 = float(percentile_stats.get('p95', projected_weeks_p85))
            input_stats = mc_basic.get('input_stats')

        can_meet_deadline = weeks_to_deadline >= projected_weeks_p85

        # "Quantos?" - How many items can be completed in the deadline period?
        # This answers: "If I have this much time, how many items can I complete?"
        work_by_deadline = forecast_how_many(tp_samples, start_date, deadline_date, n_simulations)
        items_possible_p95 = work_by_deadline.get('items_p95', 0)
        items_possible_p85 = work_by_deadline.get('items_p85', 0)
        items_possible_p50 = work_by_deadline.get('items_p50', 0)

        # For scope completion: how many items from the backlog will be completed by the deadline?
        # This is the MINIMUM between what's possible and what's in the backlog
        projected_work_p95 = min(items_possible_p95, backlog)
        projected_work_p85 = min(items_possible_p85, backlog)
        projected_work_p50 = min(items_possible_p50, backlog)

        # Get completion dates for each percentile ("Quando?")
        completion_forecast = forecast_when(tp_samples, backlog, start_date, n_simulations)
        completion_date_p95 = completion_forecast.get('date_p95', '')
        completion_date_p85 = completion_forecast.get('date_p85', '')
        completion_date_p50 = completion_forecast.get('date_p50', '')

        # Calculate percentages - DON'T limit to 100% to show real values
        scope_completion_pct_raw = (weeks_to_deadline / projected_weeks_p85 * 100) if projected_weeks_p85 > 0 else 100
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
            'input_stats': input_stats
        }

        # Machine Learning Analysis (if enough data)
        ml_result = None
        if len(tp_samples) >= 8:
            try:
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
                    n_simulations=min(n_simulations, 1000)
                )
            except Exception as e:
                ml_result = {'error': str(e)}

        mc_result_native = convert_to_native_types(mc_result)
        ml_result_native = convert_to_native_types(ml_result) if ml_result else None

        response_data = {
            'monte_carlo': mc_result_native,
            'machine_learning': ml_result_native,
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

        return jsonify(convert_to_native_types(response_data))

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/forecast-how-many', methods=['POST'])
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

        if not tp_samples:
            return jsonify({'error': 'Need throughput samples'}), 400
        if not start_date or not end_date:
            return jsonify({'error': 'Need start date and end date'}), 400

        # Monte Carlo
        mc_result = forecast_how_many(
            tp_samples=tp_samples,
            start_date=start_date,
            end_date=end_date,
            n_simulations=n_simulations
        )

        # Machine Learning
        ml_result = None
        if len(tp_samples) >= 8:
            try:
                ml_result = ml_forecast_how_many(
                    tp_samples=tp_samples,
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

        # Monte Carlo
        mc_result = forecast_when(
            tp_samples=tp_samples,
            backlog=backlog,
            start_date=start_date,
            n_simulations=n_simulations
        )

        # Machine Learning
        ml_result = None
        if len(tp_samples) >= 8:
            try:
                ml_result = ml_forecast_when(
                    tp_samples=tp_samples,
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
print("="*60)
print(f"Total routes registered: {len(list(app.url_map.iter_rules()))}")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint:30s} {rule.rule}")
print("="*60)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
