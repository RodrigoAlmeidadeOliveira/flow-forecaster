"""
Unified Monte Carlo Simulation Engine for Project Forecasting
Combines the complete JavaScript implementation with Python enhancements
Migrated and enhanced from JavaScript to Python with additional features from Forecasting_MCS_ML_v4_full_ml.py
"""

import random
import math
import statistics
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.special import gammaln
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# UTILITY FUNCTIONS (from monte_carlo.js)
# ============================================================================

def percentile(arr: List[float], p: float, sort: bool = False) -> float:
    """
    Returns the value at a given percentile in a numeric array.
    Linear interpolation between closest ranks method.

    Args:
        arr: Numeric array
        p: Percentile number between 0 (p0) and 1 (p100)
        sort: If True, the array will be sorted

    Returns:
        The value at a given percentile
    """
    if len(arr) == 0:
        return 0.0

    if not isinstance(p, (int, float)):
        raise TypeError('p must be a number')

    if sort:
        arr = sorted(arr)

    if p <= 0:
        return arr[0]
    if p >= 1:
        return arr[-1]

    index = (len(arr) - 1) * p
    lower = math.floor(index)
    upper = lower + 1
    weight = index % 1

    if upper >= len(arr):
        return arr[lower]

    return arr[lower] * (1 - weight) + arr[upper] * weight


def sort_numbers(array: List[float]) -> List[float]:
    """Sorts a numeric array."""
    return sorted(array)


def random_integer(min_val: int, max_val: int) -> int:
    """
    Generates a random integer between min and max.

    Args:
        min_val: Minimum number (inclusive)
        max_val: Maximum number (inclusive)

    Returns:
        Random integer
    """
    return random.randint(min_val, max_val)


def random_element(array: List[Any]) -> Any:
    """Retrieves a random element from an array."""
    return array[random_integer(0, len(array) - 1)]


def random_sample_average(array: List[float],
                          min_number_of_items: int,
                          max_number_of_items: int) -> float:
    """
    Generates an average of random sample elements from a numeric array.

    Args:
        array: Numeric array
        min_number_of_items: Minimum number of random samples to average
        max_number_of_items: Maximum number of random samples to average

    Returns:
        The average for the random samples selected
    """
    if len(array) == 0:
        return 0.0

    number_of_items = random_integer(min_number_of_items, max_number_of_items)
    total = sum(random_element(array) for _ in range(number_of_items))

    return total / number_of_items


def error_rate(array: List[float]) -> int:
    """
    Calculates the estimated error rate/range for the given numeric array.

    Args:
        array: Numeric array

    Returns:
        Estimated error rate/range between 0 and 100
    """
    if len(array) <= 1:
        return 0

    sorted_array = sorted(array[:])
    min_val = min(sorted_array)
    max_val = max(sorted_array)

    group1 = [val for idx, val in enumerate(sorted_array) if idx % 2 != 0]
    g1avg = sum(group1) / len(group1) if group1 else 0

    group2 = [val for idx, val in enumerate(sorted_array) if idx % 2 == 0]
    g2avg = sum(group2) / len(group2) if group2 else 0

    avg_error = abs(g1avg - g2avg)

    if max_val == min_val:
        return 0

    return round(100 * avg_error / (max_val - min_val))


# ============================================================================
# DESCRIPTIVE STATISTICS HELPERS
# ============================================================================


def _safe_mode(values: np.ndarray) -> Optional[float]:
    if values.size == 0:
        return None
    try:
        modes = statistics.multimode(values.tolist())
        if not modes:
            return None
        return float(modes[0])
    except Exception:
        return None


def describe_throughput_samples(samples: List[float]) -> Optional[Dict[str, Any]]:
    if not samples:
        return None

    arr = np.asarray(samples, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None

    sorted_arr = np.sort(arr)
    count = int(sorted_arr.size)
    mean = float(np.mean(sorted_arr))
    median = float(np.median(sorted_arr))
    std = float(np.std(sorted_arr, ddof=0))
    mad = float(np.mean(np.abs(sorted_arr - mean)))
    mode_value = _safe_mode(sorted_arr)
    min_val = float(sorted_arr.min())
    max_val = float(sorted_arr.max())
    cv = float((std / mean) * 100) if mean else None

    percentile_map = {}
    for p in [10, 25, 50, 75, 85, 90, 95]:
        percentile_map[f'p{int(p)}'] = float(np.percentile(sorted_arr, p))

    return {
        'count': count,
        'mean': mean,
        'median': median,
        'mode': mode_value,
        'std': std,
        'mad': mad,
        'cv': cv,
        'min': min_val,
        'max': max_val,
        'range': max_val - min_val,
        'percentiles': percentile_map
    }


def _weibull_linear_fit(values: np.ndarray) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    positive = values[values > 0]
    if positive.size < 2:
        return None, None, None

    sorted_vals = np.sort(positive)
    ranks = np.arange(1, sorted_vals.size + 1)
    probs = (ranks - 0.3) / (sorted_vals.size + 0.4)

    x = np.log(sorted_vals)
    y = np.log(-np.log(1 - probs))

    slope, intercept = np.polyfit(x, y, 1)
    y_pred = intercept + slope * x

    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return float(slope), float(intercept), float(r_squared)


def describe_lead_time_samples(samples: List[float]) -> Optional[Dict[str, Any]]:
    if not samples:
        return None

    arr = np.asarray(samples, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None

    sorted_arr = np.sort(arr)
    count = int(sorted_arr.size)
    mean = float(np.mean(sorted_arr))
    median = float(np.median(sorted_arr))
    std = float(np.std(sorted_arr, ddof=0))
    mad = float(np.mean(np.abs(sorted_arr - mean)))
    mode_value = _safe_mode(sorted_arr)
    min_val = float(sorted_arr.min())
    max_val = float(sorted_arr.max())
    data_range = max_val - min_val
    cv = float((std / mean) * 100) if mean else None

    percentiles = {
        'p100': max_val,
        'p98': float(np.percentile(sorted_arr, 98)),
        'p95': float(np.percentile(sorted_arr, 95)),
        'p90': float(np.percentile(sorted_arr, 90)),
        'p85': float(np.percentile(sorted_arr, 85)),
        'p75': float(np.percentile(sorted_arr, 75)),
        'p50': float(np.percentile(sorted_arr, 50)),
        'p25': float(np.percentile(sorted_arr, 25)),
        'p15': float(np.percentile(sorted_arr, 15))
    }

    ratio_p98_p50 = percentiles['p98'] / percentiles['p50'] if percentiles['p50'] else None

    q1 = percentiles['p25']
    q3 = percentiles['p75']
    iqr = q3 - q1
    outlier_threshold = q3 + 1.5 * iqr

    risk_metrics = {
        'six_mean_threshold': mean * 6 if mean else None,
        'count_above_six_mean': int(np.sum(sorted_arr > mean * 6)) if mean else 0,
        'ten_median_threshold': median * 10 if median else None,
        'count_above_ten_median': int(np.sum(sorted_arr > median * 10)) if median else 0,
        'outlier_threshold': outlier_threshold,
        'count_above_outlier': int(np.sum(sorted_arr > outlier_threshold))
    }

    shape, intercept, r_squared = _weibull_linear_fit(sorted_arr)
    weibull_fit = None
    if shape and shape > 0:
        scale = math.exp(-intercept / shape)
        predicted_mean = scale * math.exp(gammaln(1 + 1 / shape))
        weibull_fit = {
            'shape': float(shape),
            'intercept': float(intercept),
            'scale': float(scale),
            'p63': float(scale),
            'predicted_mean': float(predicted_mean),
            'r_squared': float(r_squared)
        }

    return {
        'count': count,
        'mean': mean,
        'median': median,
        'mode': mode_value,
        'std': std,
        'mad': mad,
        'cv': cv,
        'min': min_val,
        'max': max_val,
        'range': data_range,
        'percentiles': percentiles,
        'ratio_p98_p50': ratio_p98_p50,
        'iqr': iqr,
        'risk_metrics': risk_metrics,
        'weibull_fit': weibull_fit
    }


# ============================================================================
# S-CURVE DISTRIBUTION (from monte_carlo.js)
# ============================================================================

def calculate_contributors_distribution(simulation_data: Dict[str, Any]) -> List[int]:
    """
    Calculates the S-curve distribution of individual contributors.
    This models team ramp-up and ramp-down in a project.

    Args:
        simulation_data: Simulation data dictionary

    Returns:
        List with exactly 100 elements, each representing the number of
        individual contributors for that percentage of completion
    """
    min_contributors = simulation_data['minContributors']
    max_contributors = simulation_data['maxContributors']
    s_curve_size = simulation_data['sCurveSize']

    curve_size = max(0, min(50, s_curve_size))
    curve_tail_start = 100 - curve_size

    contributors_range = list(range(min_contributors, max_contributors))
    contributors_distribution = []

    def get_contributors(p: float) -> int:
        return min(max_contributors, max(min_contributors,
                   round(percentile(contributors_range, p))))

    for i in range(100):
        if i < curve_size:
            # Ramp-up phase
            contributors_distribution.append(get_contributors(i / curve_size))
        elif i < curve_tail_start:
            # Full capacity phase
            contributors_distribution.append(max_contributors)
        else:
            # Ramp-down phase
            contributors_distribution.append(get_contributors((100 - i) / curve_size))

    return contributors_distribution


# ============================================================================
# COMPLETE MONTE CARLO SIMULATION (from monte_carlo.js)
# ============================================================================

def simulate_burn_down(simulation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single round of Monte Carlo burn down simulation.
    NOW USES WEIBULL DISTRIBUTION for throughput sampling.

    Args:
        simulation_data: Simulation data dictionary

    Returns:
        Simulation result for this round including:
        - totalTasks: Total number of tasks (with risks and split rates)
        - durationInCalendarWeeks: Project duration in weeks
        - leadTime: Lead time overhead
        - effortWeeks: Total effort in person-weeks
        - burnDown: Week-by-week remaining tasks
    """
    # Get pre-calculated distributions (created in run_monte_carlo_simulation)
    weibull_fitter = simulation_data['weibull_fitter']
    contributors_distribution = simulation_data['contributorsDistribution']
    lt_samples = simulation_data['ltSamples']
    split_rate_samples = simulation_data['splitRateSamples']
    risks = simulation_data['risks']
    number_of_tasks = simulation_data['numberOfTasks']
    total_contributors = simulation_data['totalContributors']

    # Retrieve a random split rate for this round
    random_split_rate = (random_sample_average(split_rate_samples, 1, len(split_rate_samples) * 3)
                        if split_rate_samples else 1.0)

    # Calculate random impacts for this round
    impact_tasks = 0
    for risk in risks:
        if random.random() <= risk['likelihood']:
            impact_tasks += random_integer(risk['lowImpact'], risk['highImpact'])

    # Calculate the number of tasks for this round
    total_tasks = round((number_of_tasks + impact_tasks) * random_split_rate)

    # Extend the duration by a random sample average of lead times
    lead_time = (random_sample_average(lt_samples,
                                       round(len(lt_samples) * 0.1),
                                       round(len(lt_samples) * 0.9))
                if lt_samples else 0.0)
    duration_in_calendar_weeks = round(lead_time / 7)

    week_number = 0
    effort_weeks = 0
    burn_down = []
    remaining_tasks = total_tasks

    # Run the simulation
    while remaining_tasks > 0:
        burn_down.append(math.ceil(remaining_tasks))

        # CHANGED: Use Weibull distribution instead of random_element
        random_tp = max(0, round(weibull_fitter.generate_sample()))

        # FIXED: Prevent division by zero when total_tasks is 0
        if total_tasks > 0:
            percent_complete = max(0, min(99, round((total_tasks - remaining_tasks) / total_tasks * 100)))
        else:
            percent_complete = 0
        contributors_this_week = contributors_distribution[percent_complete]

        # FIXED: Adjust throughput based on active contributors
        # IMPORTANT: Historical throughput is assumed to be from a baseline team
        # We get the baseline from simulation data, default to 1 if not specified
        baseline_team_size = simulation_data.get('historical_team_size', 1)

        # Scale throughput: if historical data is from 1 person doing X items/week,
        # and we now have N contributors active, they should do N * X items/week
        throughput_per_contributor = random_tp / baseline_team_size
        adjusted_tp = throughput_per_contributor * contributors_this_week

        remaining_tasks -= adjusted_tp
        duration_in_calendar_weeks += 1
        week_number += 1
        effort_weeks += contributors_this_week

    burn_down.append(0)

    return {
        'totalTasks': total_tasks,
        'durationInCalendarWeeks': duration_in_calendar_weeks,
        'leadTime': lead_time,
        'effortWeeks': effort_weeks,
        'burnDown': burn_down,
    }


def run_monte_carlo_simulation(simulation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a full Monte Carlo simulation for the given data.
    COMPLETE implementation matching monte_carlo.js functionality.

    Args:
        simulation_data: Simulation data dictionary with keys:
            - numberOfSimulations: Number of Monte Carlo runs
            - tpSamples: Weekly throughput samples
            - ltSamples: Task lead-time samples (optional)
            - splitRateSamples: Project split rate samples (optional)
            - risks: List of risk dictionaries (optional)
            - numberOfTasks: Base number of tasks
            - totalContributors: Total team size
            - minContributors: Minimum active contributors
            - maxContributors: Maximum active contributors
            - sCurveSize: S-curve size percentage (0-50)

    Returns:
        Result of the simulation with:
        - simulations: List of all simulation results
        - burnDowns: First 100 burn-down charts
        - completion_times: List of completion times
        - percentile_stats: Statistical percentiles
        - tpErrorRate: Throughput error rate
        - ltErrorRate: Lead-time error rate
        - resultsTable: Full probability table
    """
    # Create a copy to avoid modifying the original
    simulation_data = simulation_data.copy()

    # Convert likelihood percentages to decimals
    for risk in simulation_data.get('risks', []):
        if risk['likelihood'] >= 1:
            risk['likelihood'] /= 100

    # Pre-calculate S-curve distribution (once for all simulations)
    simulation_data['contributorsDistribution'] = calculate_contributors_distribution(simulation_data)

    # Pre-create Weibull fitter (once for all simulations) - PERFORMANCE OPTIMIZATION
    tp_samples = simulation_data['tpSamples']
    simulation_data['weibull_fitter'] = WeibullFitter(np.array(tp_samples))

    number_of_simulations = simulation_data['numberOfSimulations']
    burn_downs = []
    simulations = []

    for i in range(number_of_simulations):
        res = simulate_burn_down(simulation_data)
        simulations.append({
            'durationInCalendarWeeks': res['durationInCalendarWeeks'],
            'totalTasks': res['totalTasks'],
            'leadTime': res['leadTime'],
            'effortWeeks': res['effortWeeks'],
        })
        if i < 100:
            burn_downs.append(res['burnDown'])

    duration_histogram = sort_numbers([s['durationInCalendarWeeks'] for s in simulations])
    tasks_histogram = sort_numbers([s['totalTasks'] for s in simulations])
    lt_histogram = sort_numbers([s['leadTime'] for s in simulations])
    effort_histogram = sort_numbers([s['effortWeeks'] for s in simulations])

    results_table = []
    p = 100
    while p >= 0:
        duration = percentile(duration_histogram, p / 100)
        tasks = percentile(tasks_histogram, p / 100)
        lead_time = percentile(lt_histogram, p / 100)
        effort = percentile(effort_histogram, p / 100)
        results_table.append({
            'Likelihood': p,
            'Duration': round(duration),
            'TotalTasks': round(tasks),
            'Effort': round(effort),
            'LT': round(lead_time)
        })
        p -= 5

    tp_error_rate = error_rate(simulation_data['tpSamples'])
    lt_error_rate = error_rate(simulation_data['ltSamples']) if simulation_data.get('ltSamples') else 0

    # Calculate percentile statistics for completion times
    completion_times = [s['durationInCalendarWeeks'] for s in simulations]
    percentile_stats = {
        'p10': percentile(duration_histogram, 0.10),
        'p25': percentile(duration_histogram, 0.25),
        'p50': percentile(duration_histogram, 0.50),
        'p75': percentile(duration_histogram, 0.75),
        'p85': percentile(duration_histogram, 0.85),
        'p90': percentile(duration_histogram, 0.90),
        'p95': percentile(duration_histogram, 0.95)
    }

    throughput_stats = describe_throughput_samples(simulation_data.get('tpSamples', []))
    lead_time_stats = describe_lead_time_samples(simulation_data.get('ltSamples', []))

    return {
        'simulations': simulations,
        'burnDowns': burn_downs,
        'completion_times': completion_times,
        'percentile_stats': percentile_stats,
        'tpErrorRate': tp_error_rate,
        'ltErrorRate': lt_error_rate,
        'resultsTable': results_table,
        'input_stats': {
            'throughput': throughput_stats,
            'lead_time': lead_time_stats
        }
    }


# ============================================================================
# SIMPLIFIED THROUGHPUT FORECAST (now uses Weibull internally)
# ============================================================================

def simulate_throughput_forecast(tp_samples: List[float],
                                 backlog: int,
                                 n_simulations: int = 10000) -> Dict[str, Any]:
    """
    SIMPLIFIED Monte Carlo simulation for throughput-based forecasting.
    NOW USES WEIBULL DISTRIBUTION for all random sampling.

    This version assumes constant team size (1 contributor) and no complexity.
    Perfect for quick forecasts without team dynamics.

    Use run_monte_carlo_simulation() for complete project forecasting with:
    - Variable team sizes
    - S-curve modeling
    - Risk assessment
    - Lead times
    - Split rates

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of tasks to complete
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Dictionary with simulation results

    Note:
        This function now uses Weibull distribution internally for better
        statistical accuracy, matching the 'complete' mode behavior.
    """
    if not tp_samples:
        raise ValueError('Throughput samples are required for Monte Carlo simulation')
    if backlog <= 0:
        raise ValueError('Backlog must be greater than zero')

    simulation_data = {
        'projectName': 'Throughput Forecast',
        'numberOfSimulations': n_simulations,
        'tpSamples': tp_samples,
        'ltSamples': [],
        'splitRateSamples': [],
        'risks': [],
        'numberOfTasks': backlog,
        'totalContributors': 1,
        'minContributors': 1,
        'maxContributors': 1,
        'sCurveSize': 0
    }

    # This now uses Weibull internally via simulate_burn_down
    mc_result = run_monte_carlo_simulation(simulation_data)
    completion_times = mc_result.get('completion_times', [])

    mean_duration = round(statistics.mean(completion_times), 1) if completion_times else 0.0
    std_duration = round(statistics.pstdev(completion_times), 1) if len(completion_times) > 1 else 0.0

    percentile_stats = {
        key: round(value, 1)
        for key, value in mc_result.get('percentile_stats', {}).items()
    }

    return {
        'completion_times': completion_times,
        'burn_downs': mc_result.get('burnDowns', []),
        'percentile_stats': percentile_stats,
        'mean': mean_duration,
        'std': std_duration,
        'input_stats': mc_result.get('input_stats', {
            'throughput': describe_throughput_samples(tp_samples)
        })
    }


# ============================================================================
# WEIBULL-BASED SIMULATION (from Forecasting_MCS_ML_v4_full_ml.py)
# ============================================================================

@dataclass
class WeibullParameters:
    """Container for Weibull distribution parameters"""
    shape: float
    scale: float
    mean: float
    std: float


class WeibullFitter:
    """Fits Weibull distribution to throughput data with optimized sampling"""

    def __init__(self, throughput_data: np.ndarray):
        """
        Initialize and fit Weibull distribution to data

        Args:
            throughput_data: Array of historical throughput values
        """
        self.data = throughput_data
        self.shape, self.loc, self.scale = stats.weibull_min.fit(throughput_data, floc=0)

        # Calculate distribution statistics
        self.mean = stats.weibull_min.mean(self.shape, scale=self.scale)
        self.std = stats.weibull_min.std(self.shape, scale=self.scale)

        # Pre-generate a pool of samples for fast access (PERFORMANCE OPTIMIZATION)
        self._sample_pool = None
        self._pool_index = 0
        self._pool_size = 10000  # Generate 10k samples at once
        self._refill_pool()

    def _refill_pool(self):
        """Refill the sample pool with new random samples"""
        self._sample_pool = stats.weibull_min.rvs(
            self.shape, scale=self.scale, size=self._pool_size
        )
        self._pool_index = 0

    def get_parameters(self) -> WeibullParameters:
        """Get fitted Weibull parameters"""
        return WeibullParameters(
            shape=self.shape,
            scale=self.scale,
            mean=self.mean,
            std=self.std
        )

    def generate_sample(self) -> float:
        """Generate a single random sample from the fitted distribution (optimized)"""
        # Get sample from pre-generated pool
        if self._pool_index >= self._pool_size:
            self._refill_pool()

        sample = self._sample_pool[self._pool_index]
        self._pool_index += 1
        return sample

    def generate_samples(self, n: int) -> np.ndarray:
        """Generate multiple random samples from the fitted distribution"""
        return stats.weibull_min.rvs(self.shape, scale=self.scale, size=n)


class WeibullMonteCarloSimulator:
    """
    Advanced Monte Carlo simulator using Weibull distribution.
    From Forecasting_MCS_ML_v4_full_ml.py
    """

    def __init__(self, throughput_data: np.ndarray):
        """
        Initialize simulator with throughput data

        Args:
            throughput_data: Historical throughput samples
        """
        self.weibull = WeibullFitter(throughput_data)

    def simulate_completion_time(self, backlog: int, n_runs: int = 100000) -> pd.DataFrame:
        """
        Simulates time to complete backlog using Weibull distribution

        Args:
            backlog: Number of items to complete
            n_runs: Number of simulation runs

        Returns:
            DataFrame with detailed simulation results
        """
        records = []

        for run in range(n_runs):
            remaining = backlog
            week = 1
            cumulative = 0

            while remaining > 0:
                # Generate weekly throughput using Weibull
                weekly_th = max(0, round(self.weibull.generate_sample()))
                delivered = min(weekly_th, remaining)
                cumulative += delivered

                records.append({
                    'run': run,
                    'week': week,
                    'delivered': delivered,
                    'cumulative': cumulative,
                    'remaining': remaining - delivered
                })

                remaining -= delivered
                week += 1

        return pd.DataFrame(records)

    def aggregate_results(self, df: pd.DataFrame, backlog: int, total_runs: int) -> pd.DataFrame:
        """
        Aggregate simulation results by week

        Args:
            df: Simulation results DataFrame
            backlog: Total backlog size
            total_runs: Total number of simulation runs

        Returns:
            DataFrame with aggregated weekly statistics
        """
        weeks = sorted(df['week'].unique())

        # First completion week per run
        completion_weeks = (
            df[df['cumulative'] >= backlog]
            .groupby('run')['week']
            .min()
        )

        results = []
        for week in weeks:
            week_data = df[df['week'] == week]

            # Weekly throughput percentiles
            delivered_vals = week_data['delivered'].values
            p95_th = np.percentile(delivered_vals, 5)
            p85_th = np.percentile(delivered_vals, 15)
            p50_th = np.percentile(delivered_vals, 50)

            # Cumulative percentiles
            cum_vals = week_data['cumulative'].values
            p95_cum = np.percentile(cum_vals, 5)
            p85_cum = np.percentile(cum_vals, 15)
            p50_cum = np.percentile(cum_vals, 50)

            # Completion probability by this week
            p_completion = (completion_weeks <= week).sum() / total_runs

            results.append({
                'week': week,
                'P95_weekly': p95_th,
                'P85_weekly': p85_th,
                'P50_weekly': p50_th,
                'P95_cumulative': p95_cum,
                'P85_cumulative': p85_cum,
                'P50_cumulative': p50_cum,
                'completion_probability': p_completion
            })

        return pd.DataFrame(results)

    def run_simulation(self, backlog: int, n_runs: int = 100000) -> Dict[str, Any]:
        """
        Run complete Weibull-based Monte Carlo simulation

        Args:
            backlog: Number of items to complete
            n_runs: Number of simulation runs

        Returns:
            Dictionary with comprehensive simulation results
        """
        # Run simulation
        df = self.simulate_completion_time(backlog, n_runs)

        # Aggregate results
        aggregated = self.aggregate_results(df, backlog, n_runs)

        # Calculate completion time statistics
        completion_weeks = (
            df[df['cumulative'] >= backlog]
            .groupby('run')['week']
            .min()
        )

        percentile_stats = {
            'p10': np.percentile(completion_weeks, 10),
            'p25': np.percentile(completion_weeks, 25),
            'p50': np.percentile(completion_weeks, 50),
            'p75': np.percentile(completion_weeks, 75),
            'p85': np.percentile(completion_weeks, 85),
            'p90': np.percentile(completion_weeks, 90),
            'p95': np.percentile(completion_weeks, 95)
        }

        return {
            'detailed_results': df,
            'aggregated_results': aggregated,
            'completion_times': completion_weeks.tolist(),
            'percentile_stats': percentile_stats,
            'mean': float(completion_weeks.mean()),
            'std': float(completion_weeks.std()),
            'weibull_params': self.weibull.get_parameters()
        }


# ============================================================================
# UNIFIED API - Choose the right simulation for your needs
# ============================================================================

def run_unified_simulation(
    tp_samples: List[float],
    backlog: int,
    n_simulations: int = 10000,
    mode: str = 'complete',
    team_size: Optional[int] = None,
    min_contributors: Optional[int] = None,
    max_contributors: Optional[int] = None,
    s_curve_size: int = 20,
    lt_samples: Optional[List[float]] = None,
    split_rate_samples: Optional[List[float]] = None,
    risks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Unified simulation API that chooses the appropriate method based on parameters.
    ALL MODES NOW USE WEIBULL DISTRIBUTION for random sampling.

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of tasks to complete
        n_simulations: Number of Monte Carlo runs
        mode: Simulation mode:
            - 'simple': Simple throughput-based (1 contributor, no S-curve, Weibull sampling)
            - 'weibull': Alias for 'simple' (kept for backward compatibility)
            - 'complete': Full project simulation (team dynamics, S-curve, risks, Weibull sampling)
        team_size: Total team size (required for 'complete' mode)
        min_contributors: Minimum active contributors (for 'complete' mode)
        max_contributors: Maximum active contributors (for 'complete' mode)
        s_curve_size: S-curve size percentage 0-50 (for 'complete' mode)
        lt_samples: Task lead-time samples (optional, for 'complete' mode)
        split_rate_samples: Project split rates (optional, for 'complete' mode)
        risks: List of project risks (optional, for 'complete' mode)

    Returns:
        Simulation results dictionary

    Note:
        As of version 2.1, ALL modes use Weibull distribution for throughput sampling.
        The only difference is in team dynamics:
        - 'simple'/'weibull': Single contributor, no S-curve
        - 'complete': Variable team size with S-curve modeling
    """
    if mode == 'simple' or mode == 'weibull':
        # Both 'simple' and 'weibull' now use the same unified approach
        # This internally uses Weibull via simulate_burn_down
        return simulate_throughput_forecast(tp_samples, backlog, n_simulations)

    elif mode == 'complete':
        if team_size is None:
            raise ValueError("team_size is required for complete mode")

        simulation_data = {
            'numberOfSimulations': n_simulations,
            'tpSamples': tp_samples,
            'ltSamples': lt_samples or [],
            'splitRateSamples': split_rate_samples or [],
            'risks': risks or [],
            'numberOfTasks': backlog,
            'totalContributors': team_size,
            'minContributors': min_contributors or team_size,
            'maxContributors': max_contributors or team_size,
            'sCurveSize': s_curve_size
        }

        # Uses Weibull via simulate_burn_down
        return run_monte_carlo_simulation(simulation_data)

    else:
        raise ValueError(f"Invalid mode: {mode}. Choose 'simple', 'weibull', or 'complete'")


# ============================================================================
# DEADLINE ANALYSIS AND PROJECTIONS
# ============================================================================

from datetime import datetime, timedelta

def analyze_deadline(
    tp_samples: List[float],
    backlog: int,
    deadline_date: str,
    start_date: str,
    n_simulations: int = 10000
) -> Dict[str, Any]:
    """
    Analyzes if a deadline can be met and provides detailed metrics.

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of tasks to complete
        deadline_date: Deadline date (format: 'DD/MM/YY' or 'DD/MM/YYYY')
        start_date: Start date (format: 'DD/MM/YY' or 'DD/MM/YYYY')
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Dictionary with deadline analysis including:
        - deadline_date: Deadline date
        - weeks_to_deadline: Weeks until deadline
        - projected_weeks_p85: Projected weeks needed (85% confidence)
        - projected_work_p85: Projected work that can be done by deadline (85% confidence)
        - can_meet_deadline: Boolean indicating if deadline can be met
        - scope_completion_pct: % of scope that will be completed
        - deadline_completion_pct: % of time that will be used
    """
    # Parse dates
    def parse_date(date_str):
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        date_str = date_str.strip()
        if not date_str:
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        for fmt in ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Date {date_str} doesn't match expected day-month-year formats")

    deadline = parse_date(deadline_date)
    start = parse_date(start_date)

    # Calculate weeks to deadline
    days_to_deadline = (deadline - start).days
    weeks_to_deadline = days_to_deadline / 7.0

    # Run simulation to get projected completion time
    result = simulate_throughput_forecast(tp_samples, backlog, n_simulations)

    projected_weeks_p85 = result['percentile_stats']['p85']
    projected_weeks_p50 = result['percentile_stats']['p50']

    # Can meet deadline?
    can_meet_deadline = weeks_to_deadline >= projected_weeks_p85

    # Calculate how much work can be done by deadline
    # Run reverse simulation: how much work in N weeks?
    work_by_deadline_result = forecast_how_many(tp_samples, start_date, deadline_date, n_simulations)
    projected_work_p85 = work_by_deadline_result['items_p85']

    # Calculate percentages - DON'T limit to 100% to show real values
    scope_completion_pct_raw = (weeks_to_deadline / projected_weeks_p85 * 100) if projected_weeks_p85 > 0 else 100
    deadline_completion_pct_raw = (projected_weeks_p85 / weeks_to_deadline * 100) if weeks_to_deadline > 0 else 100

    return {
        'deadline_date': deadline.strftime('%d/%m/%Y'),
        'start_date': start.strftime('%d/%m/%Y'),
        'weeks_to_deadline': round(weeks_to_deadline, 1),
        'projected_weeks_p85': round(projected_weeks_p85, 1),
        'projected_weeks_p50': round(projected_weeks_p50, 1),
        'projected_work_p85': int(projected_work_p85),
        'backlog': backlog,
        'can_meet_deadline': can_meet_deadline,
        'scope_completion_pct': round(min(100, scope_completion_pct_raw)),
        'scope_completion_pct_raw': round(scope_completion_pct_raw, 1),
        'deadline_completion_pct': round(min(100, deadline_completion_pct_raw)),
        'deadline_completion_pct_raw': round(deadline_completion_pct_raw, 1),
        'percentile_stats': result['percentile_stats']
    }


def forecast_how_many(
    tp_samples: List[float],
    start_date: str,
    end_date: str,
    n_simulations: int = 10000
) -> Dict[str, Any]:
    """
    Forecasts how many items can be completed in a given time period.
    "Quantos?" - Given a time period, how many work items will likely be completed?

    Args:
        tp_samples: Historical throughput samples
        start_date: Start date (format: 'DD/MM/YY' or 'DD/MM/YYYY')
        end_date: End date (format: 'DD/MM/YY' or 'DD/MM/YYYY')
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Dictionary with forecast including:
        - start_date: Start date
        - end_date: End date
        - days: Number of days in period
        - weeks: Number of weeks in period
        - items_p95: Items at 95% confidence
        - items_p85: Items at 85% confidence
        - items_p50: Items at 50% confidence (median)
        - items_mean: Mean items
    """
    # Parse dates
    def parse_date(date_str):
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        date_str = date_str.strip()
        if not date_str:
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        for fmt in ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Date {date_str} doesn't match expected day-month-year formats")

    start = parse_date(start_date)
    end = parse_date(end_date)

    # Calculate time period
    days = (end - start).days
    weeks = math.ceil(days / 7.0)

    # Run Monte Carlo simulation: simulate throughput for N weeks
    weibull_fitter = WeibullFitter(np.array(tp_samples))

    items_completed = []
    for _ in range(n_simulations):
        total_items = 0
        for week in range(weeks):
            weekly_throughput = max(0, round(weibull_fitter.generate_sample()))
            total_items += weekly_throughput
        items_completed.append(total_items)

    # Calculate percentiles
    items_completed_sorted = sorted(items_completed)

    return {
        'start_date': start.strftime('%d/%m/%Y'),
        'end_date': end.strftime('%d/%m/%Y'),
        'days': days,
        'weeks': weeks,
        'items_p95': int(percentile(items_completed_sorted, 0.95)),
        'items_p85': int(percentile(items_completed_sorted, 0.85)),
        'items_p50': int(percentile(items_completed_sorted, 0.50)),
        'items_mean': round(statistics.mean(items_completed), 1),
        'distribution': items_completed_sorted
    }


def forecast_when(
    tp_samples: List[float],
    backlog: int,
    start_date: str,
    n_simulations: int = 10000
) -> Dict[str, Any]:
    """
    Forecasts when a backlog will be completed.
    "Quando?" - Given a batch of work, when will it likely be done?

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of items to complete
        start_date: Start date (format: 'DD/MM/YY' or 'DD/MM/YYYY')
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Dictionary with forecast including:
        - backlog: Number of items
        - start_date: Start date
        - date_p95: Completion date at 95% confidence
        - date_p85: Completion date at 85% confidence
        - date_p50: Completion date at 50% confidence (median)
        - weeks_p95: Weeks needed at 95% confidence
        - weeks_p85: Weeks needed at 85% confidence
        - weeks_p50: Weeks needed at 50% confidence
    """
    # Parse start date
    def parse_date(date_str):
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        date_str = date_str.strip()
        if not date_str:
            raise ValueError("Date must be provided in DD/MM/YY, DD/MM/YYYY, YYYY-MM-DD, or similar day-month-year format")
        for fmt in ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Date {date_str} doesn't match expected day-month-year formats")

    start = parse_date(start_date)

    # Run simulation to get completion weeks
    result = simulate_throughput_forecast(tp_samples, backlog, n_simulations)

    percentile_stats = result['percentile_stats']

    # Calculate completion dates
    def add_weeks_to_date(date, weeks):
        return date + timedelta(weeks=weeks)

    weeks_p95 = percentile_stats['p95']
    weeks_p85 = percentile_stats['p85']
    weeks_p50 = percentile_stats['p50']

    date_p95 = add_weeks_to_date(start, weeks_p95)
    date_p85 = add_weeks_to_date(start, weeks_p85)
    date_p50 = add_weeks_to_date(start, weeks_p50)

    return {
        'backlog': backlog,
        'start_date': start.strftime('%d/%m/%Y'),
        'date_p95': date_p95.strftime('%d/%m/%Y'),
        'date_p85': date_p85.strftime('%d/%m/%Y'),
        'date_p50': date_p50.strftime('%d/%m/%Y'),
        'weeks_p95': round(weeks_p95, 1),
        'weeks_p85': round(weeks_p85, 1),
        'weeks_p50': round(weeks_p50, 1),
        'percentile_stats': percentile_stats
    }


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("Unified Monte Carlo Simulation Engine - ALL MODES USE WEIBULL")
    print("=" * 80)

    # Sample data
    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]
    backlog = 50

    # Test 1: Simple simulation (uses Weibull)
    print("\n1. SIMPLE MODE (1 contributor, no S-curve, Weibull distribution)")
    result_simple = run_unified_simulation(
        tp_samples=tp_samples,
        backlog=backlog,
        n_simulations=10000,
        mode='simple'
    )
    print(f"   P50: {result_simple['percentile_stats']['p50']:.1f} weeks")
    print(f"   P85: {result_simple['percentile_stats']['p85']:.1f} weeks")
    print(f"   Mean: {result_simple['mean']:.1f} weeks")
    print(f"   Algorithm: Weibull distribution")

    # Test 2: Complete simulation (uses Weibull)
    print("\n2. COMPLETE MODE (team dynamics, S-curve, Weibull distribution)")
    result_complete = run_unified_simulation(
        tp_samples=tp_samples,
        backlog=backlog,
        n_simulations=10000,
        mode='complete',
        team_size=10,
        min_contributors=2,
        max_contributors=5,
        s_curve_size=20
    )

    # Get P85 from results table
    p85_entry = [r for r in result_complete['resultsTable'] if r['Likelihood'] == 85][0]
    print(f"   P85 Duration: {p85_entry['Duration']} weeks")
    print(f"   P85 Effort: {p85_entry['Effort']} person-weeks")
    print(f"   Algorithm: Weibull distribution + S-curve")

    print("\n" + "=" * 80)
    print("KEY CHANGE: All modes now use Weibull distribution for sampling!")
    print("The difference is only in team dynamics (S-curve vs constant).")
    print("=" * 80)
