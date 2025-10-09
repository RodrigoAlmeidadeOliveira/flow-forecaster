"""
Project Forecaster - Flask Application
Monte Carlo simulation for project forecasting
"""

from flask import Flask, render_template, request, jsonify
import json
import base64
import numpy as np
from monte_carlo import run_monte_carlo_simulation, simulate_throughput_forecast
from ml_forecaster import MLForecaster
from visualization import ForecastVisualizer

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/advanced')
def advanced():
    """Render the advanced forecasting page."""
    return render_template('advanced_forecast.html')


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

        # Initialize ML forecaster
        forecaster = MLForecaster(max_lag=4, n_splits=3)

        # Train models
        forecaster.train_models(tp_data)

        # Generate forecasts
        forecasts = forecaster.forecast(tp_data, steps=forecast_steps, model_name=model_name)

        # Get ensemble statistics
        ensemble_stats = forecaster.get_ensemble_forecast(forecasts)

        # Get model results summary
        model_results = forecaster.get_results_summary()

        # Get risk assessment
        risk_assessment = forecaster.assess_forecast_risk(tp_data)

        # Generate visualization
        visualizer = ForecastVisualizer()
        chart_ml = visualizer.plot_ml_forecasts(tp_data, forecasts, ensemble_stats, start_date)
        chart_history = visualizer.plot_historical_analysis(tp_data, start_date)

        return jsonify({
            'forecasts': {k: v.tolist() for k, v in forecasts.items()},
            'ensemble_stats': {k: v.tolist() if isinstance(v, np.ndarray) else v
                             for k, v in ensemble_stats.items()},
            'model_results': model_results,
            'risk_assessment': risk_assessment,
            'charts': {
                'ml_forecast': chart_ml,
                'historical_analysis': chart_history
            }
        })

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

        return jsonify({
            'percentile_stats': mc_results['percentile_stats'],
            'mean': mc_results['mean'],
            'std': mc_results['std'],
            'charts': {
                'monte_carlo': chart_mc
            }
        })

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

        # ML Forecast
        forecaster = MLForecaster(max_lag=4, n_splits=3)
        forecaster.train_models(tp_data)
        forecasts = forecaster.forecast(tp_data, steps=forecast_steps, model_name='ensemble')
        ensemble_stats = forecaster.get_ensemble_forecast(forecasts)
        risk_assessment = forecaster.assess_forecast_risk(tp_data)

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

        return jsonify({
            'ml': {
                'forecasts': {k: v.tolist() for k, v in forecasts.items()},
                'ensemble': {k: v.tolist() if isinstance(v, np.ndarray) else v
                           for k, v in ensemble_stats.items()},
                'risk_assessment': risk_assessment
            },
            'monte_carlo': {
                'percentile_stats': mc_results['percentile_stats'],
                'mean': mc_results['mean'],
                'std': mc_results['std']
            },
            'charts': {
                'ml_forecast': chart_ml,
                'monte_carlo': chart_mc,
                'comparison': chart_comparison
            }
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
