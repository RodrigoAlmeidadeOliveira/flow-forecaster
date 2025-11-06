#!/usr/bin/env python3
"""
Test script for fold_stride functionality in backtesting module.

This script validates the new fold_stride parameter that allows:
- Long-horizon forecasts (e.g., 30 days)
- With periodic updates (e.g., weekly)
"""

import numpy as np
from backtesting import run_walk_forward_backtest, BacktestSummary
import sys


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_standard_walk_forward():
    """Test standard walk-forward (fold_stride=1)"""
    print_section("TEST 1: Standard Walk-Forward (fold_stride=1)")

    # Generate 20 weeks of throughput data
    np.random.seed(42)
    throughput = np.random.poisson(lam=6, size=20) + np.random.normal(0, 1, 20)
    throughput = np.maximum(throughput, 1).tolist()

    print(f"Throughput data: {len(throughput)} weeks")
    print(f"Values: {[round(x, 1) for x in throughput]}")

    # Run backtest with fold_stride=1 (every week)
    summary = run_walk_forward_backtest(
        tp_samples=throughput,
        backlog=50,
        min_train_size=8,
        test_size=1,
        fold_stride=1,  # Test every week
        confidence_level='P85',
        n_simulations=5000
    )

    print(f"\nResults:")
    print(f"  Total tests: {summary.total_tests}")
    print(f"  Expected: ~{len(throughput) - 8} tests (20 weeks - 8 min_train)")
    print(f"  Mean error: {summary.mean_error_pct:.2f}%")
    print(f"  Median error: {summary.median_error_pct:.2f}%")

    assert summary.total_tests == len(throughput) - 8, \
        f"Expected {len(throughput) - 8} tests, got {summary.total_tests}"

    print("✅ TEST PASSED: Standard walk-forward works correctly")
    return summary


def test_weekly_stride():
    """Test weekly stride (fold_stride=7) for long-horizon forecasts"""
    print_section("TEST 2: Weekly Updates with Long Horizon (fold_stride=7)")

    # Generate 60 days of daily throughput data
    np.random.seed(123)
    daily_throughput = np.random.poisson(lam=5, size=60) + np.random.normal(0, 0.5, 60)
    daily_throughput = np.maximum(daily_throughput, 1).tolist()

    print(f"Daily throughput data: {len(daily_throughput)} days")
    print(f"Sample values (first 14 days): {[round(x, 1) for x in daily_throughput[:14]]}")

    # Run backtest with 30-day horizon, updating every 7 days
    summary = run_walk_forward_backtest(
        tp_samples=daily_throughput,
        backlog=150,
        min_train_size=14,     # Need at least 2 weeks of history
        test_size=30,          # 30-day forecast horizon
        fold_stride=7,         # Update every 7 days (weekly)
        confidence_level='P85',
        n_simulations=5000
    )

    print(f"\nConfiguration:")
    print(f"  Forecast horizon: 30 days")
    print(f"  Update cadence: Every 7 days")
    print(f"  Min training: 14 days")

    print(f"\nResults:")
    print(f"  Total tests: {summary.total_tests}")

    # Calculate expected number of tests
    # From day 14 to day (60-30), stepping by 7
    expected_tests = len(range(14, len(daily_throughput) - 30 + 1, 7))
    print(f"  Expected: ~{expected_tests} tests")
    print(f"  Mean error: {summary.mean_error_pct:.2f}%")
    print(f"  Median error: {summary.median_error_pct:.2f}%")

    # Verify we have fewer tests than standard walk-forward
    # (because we skip periods)
    assert summary.total_tests < (len(daily_throughput) - 14 - 30), \
        "fold_stride should reduce number of tests"

    assert summary.total_tests == expected_tests, \
        f"Expected {expected_tests} tests, got {summary.total_tests}"

    print("✅ TEST PASSED: Weekly stride works correctly")
    return summary


def test_biweekly_stride():
    """Test bi-weekly stride (fold_stride=14)"""
    print_section("TEST 3: Bi-weekly Updates (fold_stride=14)")

    # Generate 90 days of data
    np.random.seed(456)
    daily_throughput = np.random.poisson(lam=7, size=90) + np.random.normal(0, 1, 90)
    daily_throughput = np.maximum(daily_throughput, 1).tolist()

    print(f"Daily throughput data: {len(daily_throughput)} days")

    # Run backtest with 60-day horizon, updating every 14 days
    summary = run_walk_forward_backtest(
        tp_samples=daily_throughput,
        backlog=400,
        min_train_size=21,     # 3 weeks minimum
        test_size=60,          # 60-day (2 month) forecast
        fold_stride=14,        # Update every 2 weeks
        confidence_level='P85',
        n_simulations=5000
    )

    print(f"\nConfiguration:")
    print(f"  Forecast horizon: 60 days (2 months)")
    print(f"  Update cadence: Every 14 days (bi-weekly)")
    print(f"  Min training: 21 days")

    print(f"\nResults:")
    print(f"  Total tests: {summary.total_tests}")

    expected_tests = len(range(21, len(daily_throughput) - 60 + 1, 14))
    print(f"  Expected: ~{expected_tests} tests")
    print(f"  Mean error: {summary.mean_error_pct:.2f}%")

    assert summary.total_tests == expected_tests, \
        f"Expected {expected_tests} tests, got {summary.total_tests}"

    print("✅ TEST PASSED: Bi-weekly stride works correctly")
    return summary


def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("TEST 4: Edge Cases and Error Handling")

    np.random.seed(789)
    throughput = np.random.poisson(lam=5, size=30).tolist()

    # Test 1: fold_stride = 0 (invalid)
    print("\nTest 4.1: Invalid fold_stride (0)")
    try:
        run_walk_forward_backtest(
            tp_samples=throughput,
            backlog=50,
            fold_stride=0
        )
        print("❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # Test 2: fold_stride > data length
    print("\nTest 4.2: fold_stride larger than data")
    try:
        run_walk_forward_backtest(
            tp_samples=throughput,
            backlog=50,
            fold_stride=100
        )
        print("❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # Test 3: Large stride that results in only 1 test
    print("\nTest 4.3: Very large stride (minimal tests)")
    summary = run_walk_forward_backtest(
        tp_samples=throughput,
        backlog=50,
        min_train_size=5,
        test_size=1,
        fold_stride=20,  # Very large stride
        n_simulations=1000
    )
    print(f"  Total tests with stride=20: {summary.total_tests}")
    assert summary.total_tests >= 1, "Should have at least 1 test"
    print("✅ Large stride handled correctly")

    print("\n✅ ALL EDGE CASES PASSED")
    return True


def test_comparison_with_standard():
    """Compare fold_stride vs standard walk-forward"""
    print_section("TEST 5: Performance Comparison")

    np.random.seed(999)
    throughput = np.random.poisson(lam=6, size=50).tolist()

    # Standard walk-forward
    print("\nRunning standard walk-forward (fold_stride=1)...")
    summary_standard = run_walk_forward_backtest(
        tp_samples=throughput,
        backlog=100,
        min_train_size=10,
        test_size=5,
        fold_stride=1,
        n_simulations=3000
    )

    # With stride
    print("Running with fold_stride=5...")
    summary_stride = run_walk_forward_backtest(
        tp_samples=throughput,
        backlog=100,
        min_train_size=10,
        test_size=5,
        fold_stride=5,
        n_simulations=3000
    )

    print(f"\nComparison:")
    print(f"  Standard (stride=1):")
    print(f"    Tests: {summary_standard.total_tests}")
    print(f"    Mean error: {summary_standard.mean_error_pct:.2f}%")

    print(f"  With stride=5:")
    print(f"    Tests: {summary_stride.total_tests}")
    print(f"    Mean error: {summary_stride.mean_error_pct:.2f}%")

    print(f"\n  Efficiency gain: {summary_stride.total_tests / summary_standard.total_tests:.1%} of tests")
    print(f"    (Running {summary_stride.total_tests} tests instead of {summary_standard.total_tests})")

    assert summary_stride.total_tests < summary_standard.total_tests, \
        "Stride should reduce number of tests"

    print("✅ TEST PASSED: fold_stride provides efficiency gains")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  FOLD_STRIDE BACKTESTING TEST SUITE")
    print("=" * 80)
    print("\nTesting the new fold_stride parameter for long-horizon forecasts")
    print("with periodic updates (e.g., 30-day horizon with weekly updates)")

    try:
        # Run all tests
        test_standard_walk_forward()
        test_weekly_stride()
        test_biweekly_stride()
        test_edge_cases()
        test_comparison_with_standard()

        # Final summary
        print_section("ALL TESTS PASSED ✅")
        print("\nfold_stride functionality is working correctly!")
        print("\nUse cases:")
        print("  - fold_stride=1:  Standard walk-forward (every period)")
        print("  - fold_stride=7:  Weekly updates for daily data")
        print("  - fold_stride=14: Bi-weekly updates")
        print("  - fold_stride=30: Monthly updates")
        print("\nBenefits:")
        print("  ✅ Long-horizon forecasts (e.g., 30-60 days)")
        print("  ✅ Fewer simulations = faster execution")
        print("  ✅ Realistic cadence (match real-world update frequency)")
        print("  ✅ Better resource utilization")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
