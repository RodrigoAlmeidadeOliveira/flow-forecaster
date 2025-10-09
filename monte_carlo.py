"""
Monte Carlo simulation engine for project forecasting.
Migrated from JavaScript to Python.
"""

import random
import math
from typing import List, Dict, Any, Optional


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


def calculate_contributors_distribution(simulation_data: Dict[str, Any]) -> List[int]:
    """
    Calculates the S-curve distribution of individual contributors.

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
            contributors_distribution.append(get_contributors(i / curve_size))
        elif i < curve_tail_start:
            contributors_distribution.append(max_contributors)
        else:
            contributors_distribution.append(get_contributors((100 - i) / curve_size))

    return contributors_distribution


def simulate_burn_down(simulation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single round of Monte Carlo burn down simulation.

    Args:
        simulation_data: Simulation data dictionary

    Returns:
        Simulation result for this round
    """
    # Cache the S-curve distribution in the first run
    if 'contributorsDistribution' not in simulation_data:
        simulation_data['contributorsDistribution'] = calculate_contributors_distribution(simulation_data)

    tp_samples = simulation_data['tpSamples']
    lt_samples = simulation_data['ltSamples']
    split_rate_samples = simulation_data['splitRateSamples']
    risks = simulation_data['risks']
    number_of_tasks = simulation_data['numberOfTasks']
    total_contributors = simulation_data['totalContributors']
    contributors_distribution = simulation_data['contributorsDistribution']

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
        random_tp = random_element(tp_samples)
        percent_complete = max(0, min(99, round((total_tasks - remaining_tasks) / total_tasks * 100)))
        contributors_this_week = contributors_distribution[percent_complete]
        adjusted_tp = random_tp * (contributors_this_week / total_contributors)
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

    Args:
        simulation_data: Simulation data dictionary

    Returns:
        Result of the simulation
    """
    # Create a copy to avoid modifying the original
    simulation_data = simulation_data.copy()

    # Convert likelihood percentages to decimals
    for risk in simulation_data['risks']:
        if risk['likelihood'] >= 1:
            risk['likelihood'] /= 100

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
    lt_error_rate = error_rate(simulation_data['ltSamples']) if simulation_data['ltSamples'] else 0

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

    return {
        'simulations': simulations,
        'burnDowns': burn_downs,
        'completion_times': completion_times,
        'percentile_stats': percentile_stats,
        'tpErrorRate': tp_error_rate,
        'ltErrorRate': lt_error_rate,
        'resultsTable': results_table,
    }


def simulate_throughput_forecast(tp_samples: List[float],
                                 backlog: int,
                                 n_simulations: int = 10000) -> Dict[str, Any]:
    """
    Simplified Monte Carlo simulation for throughput-based forecasting.
    Used for ML comparison and what-if analysis.

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of tasks to complete
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Dictionary with simulation results
    """
    completion_times = []
    burn_downs = []

    for i in range(n_simulations):
        remaining = backlog
        weeks = 0
        burn_down = [remaining]

        while remaining > 0:
            tp = random_element(tp_samples)
            remaining -= tp
            weeks += 1
            if i < 100:  # Store first 100 burn-downs
                burn_down.append(max(0, remaining))

        completion_times.append(weeks)
        if i < 100:
            burn_downs.append(burn_down)

    # Calculate statistics
    completion_times_sorted = sort_numbers(completion_times)

    percentile_stats = {
        'p10': round(percentile(completion_times_sorted, 0.10), 1),
        'p25': round(percentile(completion_times_sorted, 0.25), 1),
        'p50': round(percentile(completion_times_sorted, 0.50), 1),
        'p75': round(percentile(completion_times_sorted, 0.75), 1),
        'p85': round(percentile(completion_times_sorted, 0.85), 1),
        'p90': round(percentile(completion_times_sorted, 0.90), 1),
        'p95': round(percentile(completion_times_sorted, 0.95), 1)
    }

    return {
        'completion_times': completion_times,
        'burn_downs': burn_downs,
        'percentile_stats': percentile_stats,
        'mean': round(sum(completion_times) / len(completion_times), 1),
        'std': round((sum((x - sum(completion_times)/len(completion_times))**2
                         for x in completion_times) / len(completion_times)) ** 0.5, 1)
    }
