"""Debug script to test all imports"""
import sys
import traceback

print("=" * 60)
print("TESTING IMPORTS")
print("=" * 60)

imports_to_test = [
    ("flask", "from flask import Flask, render_template, request, jsonify, redirect, url_for"),
    ("json", "import json"),
    ("base64", "import base64"),
    ("numpy", "import numpy as np"),
    ("datetime", "from datetime import datetime"),
    ("monte_carlo", "from monte_carlo import run_monte_carlo_simulation, simulate_throughput_forecast"),
    ("monte_carlo_unified", "from monte_carlo_unified import analyze_deadline, forecast_how_many, forecast_when"),
    ("ml_forecaster", "from ml_forecaster import MLForecaster"),
    ("ml_deadline_forecaster", "from ml_deadline_forecaster import ml_analyze_deadline, ml_forecast_how_many, ml_forecast_when"),
    ("visualization", "from visualization import ForecastVisualizer"),
    ("cost_pert_beta", "from cost_pert_beta import simulate_pert_beta_cost, calculate_risk_metrics"),
]

failed_imports = []

for name, import_stmt in imports_to_test:
    try:
        exec(import_stmt)
        print(f"✓ {name:25s} OK")
    except Exception as e:
        print(f"✗ {name:25s} FAILED: {str(e)[:50]}")
        failed_imports.append((name, e))
        traceback.print_exc()
        print()

print("=" * 60)
if failed_imports:
    print(f"FAILED: {len(failed_imports)} imports failed")
    for name, error in failed_imports:
        print(f"  - {name}: {error}")
    sys.exit(1)
else:
    print("SUCCESS: All imports working!")
    print("=" * 60)

    # Try to import app
    print("\nTesting app.py import...")
    try:
        from app import app
        print("✓ app.py imported successfully")
        print(f"✓ Flask app created: {app}")
        print(f"✓ Routes registered: {len(list(app.url_map.iter_rules()))}")
        for rule in app.url_map.iter_rules():
            print(f"  - {rule.endpoint:30s} {rule.rule}")
    except Exception as e:
        print(f"✗ app.py import FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
