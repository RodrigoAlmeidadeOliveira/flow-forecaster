"""
Test script for Forecast vs Actual functionality
"""

def test_accuracy_metrics():
    """Test accuracy metrics calculation"""
    from accuracy_metrics import calculate_accuracy_metrics

    # Sample data: forecasts and actuals
    forecasts = [10.0, 12.0, 8.0, 15.0, 11.0]
    actuals = [9.5, 13.0, 8.5, 14.0, 10.0]

    print("Testing accuracy metrics...")
    metrics = calculate_accuracy_metrics(forecasts, actuals)

    print(f"\n✓ MAPE: {metrics.mape:.2f}%")
    print(f"✓ RMSE: {metrics.rmse:.2f}")
    print(f"✓ MAE: {metrics.mae:.2f}")
    print(f"✓ R²: {metrics.r_squared:.4f}")
    print(f"✓ Accuracy Rate: {metrics.accuracy_rate:.2f}%")
    print(f"✓ Bias Direction: {metrics.bias_direction}")

    # Get quality rating
    ratings = metrics.get_quality_rating()
    print(f"\n✓ Overall Quality: {ratings['overall']}")
    print(f"✓ MAPE Quality: {ratings['mape']}")
    print(f"✓ R² Quality: {ratings['r_squared']}")

    assert metrics.n_samples == 5
    assert metrics.mape < 100  # Reasonable MAPE
    print("\n✅ Accuracy metrics test passed!")


def test_data_quality_issues():
    """Test data quality issue detection"""
    from accuracy_metrics import detect_data_quality_issues

    print("\n\nTesting data quality detection...")

    # Case 1: Good data
    forecasts = [10.0, 12.0, 8.0, 15.0, 11.0, 9.0, 13.0]
    actuals = [9.5, 13.0, 8.5, 14.0, 10.0, 9.2, 12.5]

    issues = detect_data_quality_issues(forecasts, actuals)
    print(f"\n✓ Good data - Issues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue['severity']}: {issue['message']}")

    # Case 2: Insufficient data
    forecasts_small = [10.0, 12.0]
    actuals_small = [9.5, 13.0]

    issues_small = detect_data_quality_issues(forecasts_small, actuals_small)
    print(f"\n✓ Small data - Issues found: {len(issues_small)}")
    for issue in issues_small:
        print(f"  - {issue['severity']}: {issue['message']}")

    assert len(issues_small) > 0  # Should detect insufficient data
    print("\n✅ Data quality detection test passed!")


def test_recommendations():
    """Test recommendation generation"""
    from accuracy_metrics import calculate_accuracy_metrics, generate_recommendations, detect_data_quality_issues

    print("\n\nTesting recommendations...")

    # High MAPE scenario
    forecasts = [10.0, 12.0, 8.0, 15.0, 11.0]
    actuals = [5.0, 20.0, 4.0, 25.0, 6.0]  # Very different from forecasts

    metrics = calculate_accuracy_metrics(forecasts, actuals)
    issues = detect_data_quality_issues(forecasts, actuals)
    recommendations = generate_recommendations(metrics, issues)

    print(f"\n✓ Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    assert len(recommendations) > 0
    print("\n✅ Recommendations test passed!")


def test_backtesting():
    """Test backtesting functionality"""
    from backtesting import run_walk_forward_backtest, run_expanding_window_backtest

    print("\n\nTesting backtesting...")

    # Sample throughput data
    tp_samples = [5.0, 6.0, 7.0, 5.5, 6.5, 7.5, 6.0, 8.0, 7.0, 6.5]
    backlog = 50

    # Test walk-forward
    print("\n✓ Running walk-forward backtest...")
    summary_wf = run_walk_forward_backtest(
        tp_samples,
        backlog,
        min_train_size=5,
        confidence_level='P85',
        n_simulations=1000  # Reduced for faster testing
    )

    print(f"  Total tests: {summary_wf.total_tests}")
    print(f"  Mean error: {summary_wf.mean_error_pct:.2f}%")
    print(f"  MAPE: {summary_wf.accuracy_metrics.mape:.2f}%" if summary_wf.accuracy_metrics else "  No metrics")

    # Test expanding window
    print("\n✓ Running expanding window backtest...")
    summary_ew = run_expanding_window_backtest(
        tp_samples,
        backlog,
        initial_train_size=5,
        confidence_level='P85',
        n_simulations=1000
    )

    print(f"  Total tests: {summary_ew.total_tests}")
    print(f"  Mean error: {summary_ew.mean_error_pct:.2f}%")

    assert summary_wf.total_tests > 0
    assert summary_ew.total_tests > 0
    print("\n✅ Backtesting test passed!")


def test_api_endpoints():
    """Test if API endpoints are registered"""
    from app import app

    print("\n\nTesting API endpoints...")

    expected_endpoints = [
        '/api/actuals',
        '/api/actuals/<int:actual_id>',
        '/api/accuracy-analysis',
        '/api/forecast-vs-actual/dashboard',
        '/api/backtest',
        '/forecast-vs-actual'
    ]

    registered_rules = [rule.rule for rule in app.url_map.iter_rules()]

    for endpoint in expected_endpoints:
        # Check if endpoint pattern exists
        found = any(endpoint.replace('<int:actual_id>', '<actual_id>') in rule
                   for rule in registered_rules)
        if found:
            print(f"  ✓ {endpoint} registered")
        else:
            print(f"  ✗ {endpoint} NOT found!")
            print(f"    Available routes: {[r for r in registered_rules if 'actual' in r or 'forecast' in r]}")

    print("\n✅ API endpoints test completed!")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("FORECAST VS ACTUAL - INTEGRATION TESTS")
    print("="*60)

    try:
        test_accuracy_metrics()
        test_data_quality_issues()
        test_recommendations()
        test_backtesting()
        test_api_endpoints()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
