"""
Backtesting Module for Flow Forecaster
Automatically simulates how forecasts would have performed using historical data
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from monte_carlo_unified import simulate_throughput_forecast, forecast_when
from accuracy_metrics import calculate_accuracy_metrics, AccuracyMetrics


@dataclass
class BacktestResult:
    """Result of a single backtest simulation"""
    test_name: str
    train_end_idx: int
    test_start_idx: int
    test_end_idx: int

    # Training data
    train_tp_samples: List[float]
    train_size: int

    # Test data (actual)
    test_tp_samples: List[float]
    test_size: int

    # Forecast results
    forecasted_weeks: float
    actual_weeks: float
    error_weeks: float
    error_pct: float

    # Additional metrics
    backlog: int
    confidence_level: str  # 'P50', 'P85', 'P95'

    def to_dict(self) -> Dict:
        return {
            'test_name': self.test_name,
            'train_size': self.train_size,
            'test_size': self.test_size,
            'forecasted_weeks': round(self.forecasted_weeks, 2),
            'actual_weeks': round(self.actual_weeks, 2),
            'error_weeks': round(self.error_weeks, 2),
            'error_pct': round(self.error_pct, 2),
            'backlog': self.backlog,
            'confidence_level': self.confidence_level
        }


@dataclass
class BacktestSummary:
    """Summary of multiple backtest simulations"""
    total_tests: int
    successful_tests: int
    failed_tests: int

    # Aggregated metrics
    mean_error_pct: float
    median_error_pct: float
    std_error_pct: float

    # Accuracy metrics
    accuracy_metrics: Optional[AccuracyMetrics]

    # Individual results
    results: List[BacktestResult]

    def to_dict(self) -> Dict:
        return {
            'total_tests': self.total_tests,
            'successful_tests': self.successful_tests,
            'failed_tests': self.failed_tests,
            'mean_error_pct': round(self.mean_error_pct, 2),
            'median_error_pct': round(self.median_error_pct, 2),
            'std_error_pct': round(self.std_error_pct, 2),
            'accuracy_metrics': self.accuracy_metrics.to_dict() if self.accuracy_metrics else None,
            'results': [r.to_dict() for r in self.results]
        }


def run_walk_forward_backtest(
    tp_samples: List[float],
    backlog: int,
    min_train_size: int = 5,
    test_size: int = 1,
    confidence_level: str = 'P85',
    n_simulations: int = 10000
) -> BacktestSummary:
    """
    Run walk-forward backtesting on throughput samples.

    This simulates how the forecast would have performed by:
    1. Training on historical data up to a point
    2. Making a forecast for the next period
    3. Comparing with actual data
    4. Moving the window forward and repeating

    Args:
        tp_samples: List of historical throughput samples
        backlog: Number of items to forecast
        min_train_size: Minimum number of samples for training (default: 5)
        test_size: Number of samples to use for testing (default: 1)
        confidence_level: 'P50', 'P85', or 'P95'
        n_simulations: Number of Monte Carlo simulations per forecast

    Returns:
        BacktestSummary with results

    Raises:
        ValueError: If insufficient data
    """
    if len(tp_samples) < min_train_size + test_size:
        raise ValueError(
            f"Need at least {min_train_size + test_size} samples for backtesting. "
            f"Got {len(tp_samples)}."
        )

    if confidence_level not in ['P50', 'P85', 'P95']:
        raise ValueError("confidence_level must be 'P50', 'P85', or 'P95'")

    tp_array = np.array(tp_samples, dtype=float)
    results = []

    # Walk forward through the data
    for i in range(min_train_size, len(tp_array) - test_size + 1):
        train_end_idx = i
        test_start_idx = i
        test_end_idx = min(i + test_size, len(tp_array))

        # Training data
        train_data = tp_array[:train_end_idx].tolist()

        # Test data (actual)
        test_data = tp_array[test_start_idx:test_end_idx].tolist()

        try:
            # Make forecast using training data
            mc_result = simulate_throughput_forecast(
                train_data,
                backlog,
                n_simulations
            )

            # Get forecasted value based on confidence level
            percentile_key = confidence_level.lower()
            forecasted_weeks = mc_result['percentile_stats'][percentile_key]

            # Calculate actual weeks using test data
            # Average throughput from test period
            avg_test_throughput = np.mean(test_data)
            actual_weeks = backlog / avg_test_throughput if avg_test_throughput > 0 else float('inf')

            # Calculate error
            error_weeks = forecasted_weeks - actual_weeks
            error_pct = (error_weeks / actual_weeks) * 100 if actual_weeks > 0 else 0

            result = BacktestResult(
                test_name=f"Test_{i}",
                train_end_idx=train_end_idx,
                test_start_idx=test_start_idx,
                test_end_idx=test_end_idx,
                train_tp_samples=train_data,
                train_size=len(train_data),
                test_tp_samples=test_data,
                test_size=len(test_data),
                forecasted_weeks=forecasted_weeks,
                actual_weeks=actual_weeks,
                error_weeks=error_weeks,
                error_pct=error_pct,
                backlog=backlog,
                confidence_level=confidence_level
            )

            results.append(result)

        except Exception as e:
            print(f"Warning: Backtest {i} failed: {e}")
            continue

    if not results:
        raise ValueError("All backtest simulations failed")

    # Calculate summary statistics
    error_pcts = [r.error_pct for r in results if not np.isinf(r.actual_weeks)]
    forecasts = [r.forecasted_weeks for r in results if not np.isinf(r.actual_weeks)]
    actuals = [r.actual_weeks for r in results if not np.isinf(r.actual_weeks)]

    # Calculate accuracy metrics if we have enough data
    accuracy_metrics = None
    if len(forecasts) >= 2:
        try:
            accuracy_metrics = calculate_accuracy_metrics(forecasts, actuals)
        except:
            pass

    summary = BacktestSummary(
        total_tests=len(results),
        successful_tests=len(error_pcts),
        failed_tests=len(results) - len(error_pcts),
        mean_error_pct=float(np.mean(error_pcts)) if error_pcts else 0,
        median_error_pct=float(np.median(error_pcts)) if error_pcts else 0,
        std_error_pct=float(np.std(error_pcts)) if error_pcts else 0,
        accuracy_metrics=accuracy_metrics,
        results=results
    )

    return summary


def run_expanding_window_backtest(
    tp_samples: List[float],
    backlog: int,
    initial_train_size: int = 5,
    confidence_level: str = 'P85',
    n_simulations: int = 10000
) -> BacktestSummary:
    """
    Run expanding window backtesting.

    Similar to walk-forward, but the training window expands (includes all previous data)
    instead of sliding forward with fixed size.

    Args:
        tp_samples: List of historical throughput samples
        backlog: Number of items to forecast
        initial_train_size: Initial number of samples for training (default: 5)
        confidence_level: 'P50', 'P85', or 'P95'
        n_simulations: Number of Monte Carlo simulations per forecast

    Returns:
        BacktestSummary with results
    """
    if len(tp_samples) < initial_train_size + 1:
        raise ValueError(
            f"Need at least {initial_train_size + 1} samples for backtesting. "
            f"Got {len(tp_samples)}."
        )

    tp_array = np.array(tp_samples, dtype=float)
    results = []

    # Start with initial_train_size and expand
    for i in range(initial_train_size, len(tp_array)):
        # Training data (expanding window - includes all previous data)
        train_data = tp_array[:i].tolist()

        # Test data (next single point)
        test_data = [tp_array[i]]

        try:
            # Make forecast
            mc_result = simulate_throughput_forecast(
                train_data,
                backlog,
                n_simulations
            )

            percentile_key = confidence_level.lower()
            forecasted_weeks = mc_result['percentile_stats'][percentile_key]

            # Actual weeks based on next sample
            actual_throughput = test_data[0]
            actual_weeks = backlog / actual_throughput if actual_throughput > 0 else float('inf')

            error_weeks = forecasted_weeks - actual_weeks
            error_pct = (error_weeks / actual_weeks) * 100 if actual_weeks > 0 else 0

            result = BacktestResult(
                test_name=f"Expanding_{i}",
                train_end_idx=i,
                test_start_idx=i,
                test_end_idx=i + 1,
                train_tp_samples=train_data,
                train_size=len(train_data),
                test_tp_samples=test_data,
                test_size=1,
                forecasted_weeks=forecasted_weeks,
                actual_weeks=actual_weeks,
                error_weeks=error_weeks,
                error_pct=error_pct,
                backlog=backlog,
                confidence_level=confidence_level
            )

            results.append(result)

        except Exception as e:
            print(f"Warning: Backtest {i} failed: {e}")
            continue

    if not results:
        raise ValueError("All backtest simulations failed")

    # Calculate summary
    error_pcts = [r.error_pct for r in results if not np.isinf(r.actual_weeks)]
    forecasts = [r.forecasted_weeks for r in results if not np.isinf(r.actual_weeks)]
    actuals = [r.actual_weeks for r in results if not np.isinf(r.actual_weeks)]

    accuracy_metrics = None
    if len(forecasts) >= 2:
        try:
            accuracy_metrics = calculate_accuracy_metrics(forecasts, actuals)
        except:
            pass

    summary = BacktestSummary(
        total_tests=len(results),
        successful_tests=len(error_pcts),
        failed_tests=len(results) - len(error_pcts),
        mean_error_pct=float(np.mean(error_pcts)) if error_pcts else 0,
        median_error_pct=float(np.median(error_pcts)) if error_pcts else 0,
        std_error_pct=float(np.std(error_pcts)) if error_pcts else 0,
        accuracy_metrics=accuracy_metrics,
        results=results
    )

    return summary


def compare_confidence_levels(
    tp_samples: List[float],
    backlog: int,
    min_train_size: int = 5,
    n_simulations: int = 10000
) -> Dict[str, BacktestSummary]:
    """
    Compare backtest performance across different confidence levels.

    Args:
        tp_samples: List of historical throughput samples
        backlog: Number of items to forecast
        min_train_size: Minimum training size
        n_simulations: Number of simulations

    Returns:
        Dictionary mapping confidence level to BacktestSummary
    """
    results = {}

    for level in ['P50', 'P85', 'P95']:
        try:
            summary = run_walk_forward_backtest(
                tp_samples,
                backlog,
                min_train_size=min_train_size,
                confidence_level=level,
                n_simulations=n_simulations
            )
            results[level] = summary
        except Exception as e:
            print(f"Warning: Backtest for {level} failed: {e}")
            results[level] = None

    return results


def generate_backtest_report(summary: BacktestSummary) -> str:
    """
    Generate human-readable backtest report.

    Args:
        summary: BacktestSummary object

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("BACKTESTING REPORT")
    report.append("=" * 60)
    report.append("")

    report.append(f"Total Tests: {summary.total_tests}")
    report.append(f"Successful: {summary.successful_tests}")
    report.append(f"Failed: {summary.failed_tests}")
    report.append("")

    report.append("ERROR STATISTICS:")
    report.append(f"  Mean Error: {summary.mean_error_pct:.2f}%")
    report.append(f"  Median Error: {summary.median_error_pct:.2f}%")
    report.append(f"  Std Deviation: {summary.std_error_pct:.2f}%")
    report.append("")

    if summary.accuracy_metrics:
        metrics = summary.accuracy_metrics
        report.append("ACCURACY METRICS:")
        report.append(f"  MAPE: {metrics.mape:.2f}%")
        report.append(f"  RMSE: {metrics.rmse:.2f}")
        report.append(f"  R²: {metrics.r_squared:.4f}")
        report.append(f"  Accuracy Rate: {metrics.accuracy_rate:.2f}%")
        report.append(f"  Bias: {metrics.bias_direction}")
        report.append("")

    report.append("DETAILED RESULTS:")
    for i, result in enumerate(summary.results[:10], 1):  # Show first 10
        report.append(f"  Test {i}:")
        report.append(f"    Forecasted: {result.forecasted_weeks:.2f} weeks")
        report.append(f"    Actual: {result.actual_weeks:.2f} weeks")
        report.append(f"    Error: {result.error_pct:+.2f}%")

    if len(summary.results) > 10:
        report.append(f"  ... and {len(summary.results) - 10} more tests")

    report.append("")
    report.append("=" * 60)

    return "\n".join(report)
