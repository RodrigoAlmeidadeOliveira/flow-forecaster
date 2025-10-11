"""
Cost Analysis using PERT-Beta Distribution
Implements Monte Carlo simulation for cost forecasting based on PERT estimates
"""

import numpy as np
import scipy.stats as stats
from typing import Dict, Any, List, Tuple


def calculate_pert_beta_parameters(a: float, m: float, b: float) -> Tuple[float, float]:
    """
    Calculate PERT-Beta distribution parameters (alpha and beta) from three-point estimates.

    Based on the formulas:
    α = (2(b + 4m - 5a)/3(b-a)) × [1 + 4((m-a)(b-m)/(b-a)²)]
    β = (2(5b - 4m - a)/3(b-a)) × [1 + 4((m-a)(b-m)/(b-a)²)]

    Args:
        a: Optimistic estimate (minimum)
        m: Most likely estimate (mode)
        b: Pessimistic estimate (maximum)

    Returns:
        Tuple of (alpha, beta) parameters for Beta distribution
    """
    if not (a < m < b):
        raise ValueError("Must have a < m < b for valid PERT distribution")

    if a == b:
        raise ValueError("Optimistic and pessimistic estimates cannot be equal")

    # Calculate the weight factor
    range_val = b - a
    product = (m - a) * (b - m)
    weight = 1 + 4 * (product / (range_val ** 2))

    # Calculate alpha and beta using PERT formulas
    alpha = ((2 * (b + 4*m - 5*a)) / (3 * range_val)) * weight
    beta = ((2 * (5*b - 4*m - a)) / (3 * range_val)) * weight

    # Ensure positive parameters
    alpha = max(alpha, 0.5)
    beta = max(beta, 0.5)

    return alpha, beta


def pert_beta_mean_std(a: float, m: float, b: float, alpha: float, beta: float) -> Tuple[float, float]:
    """
    Calculate mean and standard deviation of PERT-Beta distribution.

    Args:
        a: Optimistic estimate
        m: Most likely estimate
        b: Pessimistic estimate
        alpha: Beta distribution alpha parameter
        beta: Beta distribution beta parameter

    Returns:
        Tuple of (mean, std) for the PERT distribution
    """
    # Mean calculation
    mean = a + (alpha / (alpha + beta)) * (b - a)

    # Standard deviation calculation
    variance = ((alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))) * ((b - a)**2)
    std = np.sqrt(variance)

    return mean, std


def simulate_pert_beta_cost(
    optimistic: float,
    most_likely: float,
    pessimistic: float,
    backlog: int,
    n_simulations: int = 10000,
    avg_cost_per_item: float = None
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for cost estimation using PERT-Beta distribution.

    Args:
        optimistic: Optimistic cost estimate per item
        most_likely: Most likely cost estimate per item
        pessimistic: Pessimistic cost estimate per item
        backlog: Number of items in backlog
        n_simulations: Number of Monte Carlo simulations (default: 10000)
        avg_cost_per_item: Average historical cost per item (optional)

    Returns:
        Dictionary with simulation results including:
        - total_costs: Array of simulated total costs
        - percentiles: Dict with P10, P25, P50, P75, P85, P90, P95 costs
        - mean: Mean total cost
        - std: Standard deviation of total cost
        - alpha: PERT-Beta alpha parameter
        - beta: PERT-Beta beta parameter
        - pert_mean: PERT distribution mean per item
        - pert_std: PERT distribution std per item
    """
    if n_simulations < 10000:
        raise ValueError("Minimum 10,000 simulations required for accurate results")

    # Calculate PERT-Beta parameters
    alpha, beta = calculate_pert_beta_parameters(optimistic, most_likely, pessimistic)

    # Calculate PERT mean and std
    pert_mean, pert_std = pert_beta_mean_std(optimistic, most_likely, pessimistic, alpha, beta)

    # Run Monte Carlo simulation
    # Generate random samples from Beta(alpha, beta) and scale to [a, b]
    beta_samples = stats.beta.rvs(alpha, beta, size=n_simulations * backlog)
    cost_per_item_samples = optimistic + beta_samples * (pessimistic - optimistic)

    # Reshape to (n_simulations, backlog) and sum across items
    cost_matrix = cost_per_item_samples.reshape(n_simulations, backlog)
    total_costs = np.sum(cost_matrix, axis=1)

    # Calculate percentiles
    percentiles = {
        'p10': np.percentile(total_costs, 10),
        'p25': np.percentile(total_costs, 25),
        'p50': np.percentile(total_costs, 50),  # Median
        'p75': np.percentile(total_costs, 75),
        'p85': np.percentile(total_costs, 85),
        'p90': np.percentile(total_costs, 90),
        'p95': np.percentile(total_costs, 95)
    }

    # Calculate statistics
    mean_total = np.mean(total_costs)
    std_total = np.std(total_costs)
    min_total = np.min(total_costs)
    max_total = np.max(total_costs)

    # Calculate histogram data
    hist, bin_edges = np.histogram(total_costs, bins=50)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Calculate cumulative probability
    sorted_costs = np.sort(total_costs)
    cumulative_prob = np.arange(1, len(sorted_costs) + 1) / len(sorted_costs)

    # Calculate probability of meeting average cost (if provided)
    prob_below_avg = None
    if avg_cost_per_item:
        avg_total = avg_cost_per_item * backlog
        prob_below_avg = np.sum(total_costs <= avg_total) / n_simulations

    return {
        'total_costs': total_costs.tolist(),
        'percentiles': percentiles,
        'mean': float(mean_total),
        'std': float(std_total),
        'min': float(min_total),
        'max': float(max_total),
        'alpha': float(alpha),
        'beta': float(beta),
        'pert_mean_per_item': float(pert_mean),
        'pert_std_per_item': float(pert_std),
        'histogram': {
            'counts': hist.tolist(),
            'bin_centers': bin_centers.tolist(),
            'bin_edges': bin_edges.tolist()
        },
        'cumulative': {
            'costs': sorted_costs[::max(1, len(sorted_costs)//100)].tolist(),  # Sample 100 points
            'probabilities': cumulative_prob[::max(1, len(cumulative_prob)//100)].tolist()
        },
        'prob_below_avg': prob_below_avg,
        'n_simulations': n_simulations,
        'backlog': backlog,
        'optimistic': optimistic,
        'most_likely': most_likely,
        'pessimistic': pessimistic
    }


def calculate_risk_metrics(results: Dict[str, Any], budget: float = None) -> Dict[str, Any]:
    """
    Calculate risk metrics based on simulation results.

    Args:
        results: Output from simulate_pert_beta_cost
        budget: Optional budget constraint

    Returns:
        Dictionary with risk metrics
    """
    metrics = {}

    # Risk of cost overrun
    if budget:
        total_costs = np.array(results['total_costs'])
        prob_over_budget = np.sum(total_costs > budget) / len(total_costs)
        expected_overrun = np.mean(np.maximum(total_costs - budget, 0))

        metrics['prob_over_budget'] = float(prob_over_budget)
        metrics['expected_overrun'] = float(expected_overrun)
        metrics['budget'] = float(budget)

    # Coefficient of variation (volatility measure)
    cv = (results['std'] / results['mean']) * 100 if results['mean'] > 0 else 0
    metrics['coefficient_of_variation'] = float(cv)

    # Range and IQR
    metrics['range'] = results['max'] - results['min']
    metrics['iqr'] = results['percentiles']['p75'] - results['percentiles']['p25']

    # Skewness indicator
    median = results['percentiles']['p50']
    mean = results['mean']
    metrics['skewness_indicator'] = 'Right-skewed' if mean > median else 'Left-skewed' if mean < median else 'Symmetric'

    return metrics


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("PERT-Beta Cost Analysis Simulation")
    print("=" * 80)

    # Example parameters
    optimistic = 3000  # Best case: R$ 3,000 per item
    most_likely = 5000  # Most likely: R$ 5,000 per item
    pessimistic = 10000  # Worst case: R$ 10,000 per item
    backlog = 50

    print(f"\nEstimates per item:")
    print(f"  Optimistic (a): R$ {optimistic:,.2f}")
    print(f"  Most Likely (m): R$ {most_likely:,.2f}")
    print(f"  Pessimistic (b): R$ {pessimistic:,.2f}")
    print(f"  Backlog: {backlog} items")

    # Run simulation
    results = simulate_pert_beta_cost(optimistic, most_likely, pessimistic, backlog, 10000)

    print(f"\nPERT-Beta Parameters:")
    print(f"  Alpha (α): {results['alpha']:.4f}")
    print(f"  Beta (β): {results['beta']:.4f}")
    print(f"  Mean per item: R$ {results['pert_mean_per_item']:,.2f}")
    print(f"  Std per item: R$ {results['pert_std_per_item']:,.2f}")

    print(f"\nSimulation Results (Total Cost):")
    print(f"  Mean: R$ {results['mean']:,.2f}")
    print(f"  Std Dev: R$ {results['std']:,.2f}")
    print(f"  Min: R$ {results['min']:,.2f}")
    print(f"  Max: R$ {results['max']:,.2f}")

    print(f"\nPercentiles:")
    for p, value in results['percentiles'].items():
        print(f"  {p.upper()}: R$ {value:,.2f}")

    # Risk metrics
    risk_metrics = calculate_risk_metrics(results)
    print(f"\nRisk Metrics:")
    print(f"  Coefficient of Variation: {risk_metrics['coefficient_of_variation']:.2f}%")
    print(f"  Range: R$ {risk_metrics['range']:,.2f}")
    print(f"  IQR: R$ {risk_metrics['iqr']:,.2f}")
    print(f"  Distribution: {risk_metrics['skewness_indicator']}")
