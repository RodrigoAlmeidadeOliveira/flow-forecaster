"""
ML Deadline and Forecast Analysis
Machine Learning-based deadline analysis with team dynamics, S-curve, split rates, and lead times
"""

import numpy as np
import pandas as pd
import math
import statistics
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ml_forecaster import MLForecaster
from monte_carlo_unified import (
    calculate_contributors_distribution,
    random_sample_average,
    random_integer
)


class MLDeadlineForecaster:
    """
    Machine Learning forecaster with project complexity modeling.
    Incorporates team dynamics, S-curve, split rates, and lead times.
    """

    def __init__(self,
                 tp_samples: List[float],
                 team_size: int = 1,
                 min_contributors: Optional[int] = None,
                 max_contributors: Optional[int] = None,
                 s_curve_size: int = 0,
                 lt_samples: Optional[List[float]] = None,
                 split_rate_samples: Optional[List[float]] = None):
        """
        Initialize ML Deadline Forecaster with project parameters.

        Args:
            tp_samples: Historical throughput samples
            team_size: Total team size
            min_contributors: Minimum active contributors (defaults to team_size)
            max_contributors: Maximum active contributors (defaults to team_size)
            s_curve_size: S-curve percentage (0-50)
            lt_samples: Lead time samples in days
            split_rate_samples: Split rate samples
        """
        self.tp_samples = tp_samples
        self.team_size = team_size if team_size is not None else 1
        self.min_contributors = min_contributors if min_contributors is not None else self.team_size
        self.max_contributors = max_contributors if max_contributors is not None else self.team_size
        self.s_curve_size = s_curve_size if s_curve_size is not None else 0
        self.lt_samples = lt_samples or []
        self.split_rate_samples = split_rate_samples or []

        # Initialize ML forecaster with K-Fold CV protocol
        self.ml_forecaster = MLForecaster(max_lag=4, n_splits=5, validation_size=0.2)

        # Pre-calculate S-curve if needed
        if self.s_curve_size > 0:
            self.contributors_distribution = self._calculate_s_curve()
        else:
            self.contributors_distribution = [self.max_contributors] * 100

    def _calculate_s_curve(self) -> List[int]:
        """Calculate S-curve distribution for team ramp-up/down."""
        simulation_data = {
            'minContributors': self.min_contributors,
            'maxContributors': self.max_contributors,
            'sCurveSize': self.s_curve_size
        }
        return calculate_contributors_distribution(simulation_data)

    def _apply_team_dynamics(self,
                            base_throughput: float,
                            percent_complete: float) -> float:
        """
        Apply team dynamics to base throughput using S-curve.

        Args:
            base_throughput: Base throughput from ML forecast
            percent_complete: Percentage of work completed (0-100)

        Returns:
            Adjusted throughput considering team size
        """
        percent_idx = max(0, min(99, int(percent_complete)))
        contributors_this_period = self.contributors_distribution[percent_idx]

        # Adjust throughput based on active contributors
        adjusted_tp = base_throughput * (contributors_this_period / self.team_size)

        return max(0, adjusted_tp)

    def _apply_split_rate(self) -> float:
        """Get random split rate."""
        if not self.split_rate_samples:
            return 1.0

        return random_sample_average(
            self.split_rate_samples,
            1,
            len(self.split_rate_samples) * 3
        )

    def _calculate_lead_time_weeks(self) -> float:
        """Calculate lead time in weeks."""
        if not self.lt_samples:
            return 0.0

        lead_time_days = random_sample_average(
            self.lt_samples,
            round(len(self.lt_samples) * 0.1),
            round(len(self.lt_samples) * 0.9)
        )

        return lead_time_days / 7.0

    def simulate_project_with_ml(self,
                                 backlog: int,
                                 forecast_steps: int,
                                 n_simulations: int = 1000) -> Dict[str, Any]:
        """
        Simulate project completion using ML forecasts with team dynamics.

        Args:
            backlog: Number of tasks to complete
            forecast_steps: Number of weeks to forecast with ML
            n_simulations: Number of Monte Carlo simulations for uncertainty

        Returns:
            Dictionary with simulation results
        """
        # Train ML models using K-Fold CV with Grid Search
        self.ml_forecaster.train_models(np.array(self.tp_samples), use_kfold_cv=True)

        # Get ML forecast (ensemble of all models)
        ml_forecasts = self.ml_forecaster.forecast(
            np.array(self.tp_samples),
            steps=forecast_steps,
            model_name='ensemble'
        )

        ensemble_stats = self.ml_forecaster.get_ensemble_forecast(ml_forecasts)

        # Run simulations with ML forecasts
        completion_times = []
        effort_totals = []

        for sim in range(n_simulations):
            # Apply split rate
            split_rate = self._apply_split_rate()
            total_tasks = backlog * split_rate

            # Apply lead time
            lead_time_weeks = self._calculate_lead_time_weeks()

            # Simulate week by week
            remaining = total_tasks
            week = 0
            effort = 0

            while remaining > 0 and week < forecast_steps * 2:  # Safety limit
                # Get ML forecast for this week
                if week < forecast_steps:
                    # Use ML forecast (with some random variation)
                    base_tp = ensemble_stats['mean'][week]
                    variation = np.random.normal(0, ensemble_stats['std'][week])
                    forecast_tp = max(0, base_tp + variation)
                else:
                    # Extend using last forecast value
                    base_tp = ensemble_stats['mean'][-1]
                    forecast_tp = max(0, base_tp + np.random.normal(0, ensemble_stats['std'][-1]))

                # Apply team dynamics
                percent_complete = ((total_tasks - remaining) / total_tasks * 100) if total_tasks > 0 else 0
                adjusted_tp = self._apply_team_dynamics(forecast_tp, percent_complete)

                # Track effort
                percent_idx = max(0, min(99, int(percent_complete)))
                contributors_this_week = self.contributors_distribution[percent_idx]
                effort += contributors_this_week

                # Update remaining
                remaining -= adjusted_tp
                week += 1

            completion_weeks = week + lead_time_weeks
            completion_times.append(completion_weeks)
            effort_totals.append(effort)

        # Calculate statistics
        completion_times_sorted = sorted(completion_times)
        effort_totals_sorted = sorted(effort_totals)

        return {
            'completion_times': completion_times_sorted,
            'effort_totals': effort_totals_sorted,
            'percentile_stats': {
                'p10': np.percentile(completion_times_sorted, 10),
                'p25': np.percentile(completion_times_sorted, 25),
                'p50': np.percentile(completion_times_sorted, 50),
                'p75': np.percentile(completion_times_sorted, 75),
                'p85': np.percentile(completion_times_sorted, 85),
                'p90': np.percentile(completion_times_sorted, 90),
                'p95': np.percentile(completion_times_sorted, 95)
            },
            'effort_stats': {
                'p50': np.percentile(effort_totals_sorted, 50),
                'p85': np.percentile(effort_totals_sorted, 85),
                'p95': np.percentile(effort_totals_sorted, 95)
            },
            'mean': np.mean(completion_times),
            'std': np.std(completion_times),
            'ml_forecasts': ml_forecasts,
            'ensemble_stats': ensemble_stats,
            'ml_results': self.ml_forecaster.get_results_summary()
        }


# ============================================================================
# ML DEADLINE ANALYSIS FUNCTIONS
# ============================================================================

def ml_analyze_deadline(
    tp_samples: List[float],
    backlog: int,
    deadline_date: str,
    start_date: str,
    team_size: int = 1,
    min_contributors: Optional[int] = None,
    max_contributors: Optional[int] = None,
    s_curve_size: int = 0,
    lt_samples: Optional[List[float]] = None,
    split_rate_samples: Optional[List[float]] = None,
    forecast_weeks: int = 20,
    n_simulations: int = 1000
) -> Dict[str, Any]:
    """
    ML-based deadline analysis with team dynamics.

    Args:
        tp_samples: Historical throughput samples
        backlog: Number of tasks to complete
        deadline_date: Deadline (DD/MM/YY or DD/MM/YYYY)
        start_date: Start date (DD/MM/YY or DD/MM/YYYY)
        team_size: Total team size
        min_contributors: Minimum active contributors
        max_contributors: Maximum active contributors
        s_curve_size: S-curve percentage (0-50)
        lt_samples: Lead time samples (days)
        split_rate_samples: Split rate samples
        forecast_weeks: Number of weeks to forecast
        n_simulations: Number of simulations

    Returns:
        Deadline analysis with ML forecasts
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

    # Initialize forecaster
    forecaster = MLDeadlineForecaster(
        tp_samples=tp_samples,
        team_size=team_size,
        min_contributors=min_contributors,
        max_contributors=max_contributors,
        s_curve_size=s_curve_size,
        lt_samples=lt_samples,
        split_rate_samples=split_rate_samples
    )

    # Run ML simulation
    result = forecaster.simulate_project_with_ml(
        backlog=backlog,
        forecast_steps=forecast_weeks,
        n_simulations=n_simulations
    )

    projected_weeks_p85 = result['percentile_stats']['p85']
    projected_weeks_p50 = result['percentile_stats']['p50']

    # Can meet deadline?
    can_meet_deadline = weeks_to_deadline >= projected_weeks_p85

    # Estimate work by deadline using ML forecasts
    work_by_deadline = ml_forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=deadline_date,
        team_size=team_size,
        min_contributors=min_contributors,
        max_contributors=max_contributors,
        s_curve_size=s_curve_size,
        lt_samples=lt_samples,
        n_simulations=n_simulations
    )

    projected_work_p85 = work_by_deadline['items_p85']

    # Calculate percentages
    scope_completion_pct = min(100, (projected_work_p85 / backlog * 100)) if backlog > 0 else 100
    deadline_completion_pct = (weeks_to_deadline / projected_weeks_p85 * 100) if projected_weeks_p85 > 0 else 100

    return {
        'deadline_date': deadline.strftime('%d/%m/%y'),
        'start_date': start.strftime('%d/%m/%y'),
        'weeks_to_deadline': round(weeks_to_deadline, 1),
        'projected_weeks_p85': round(projected_weeks_p85, 1),
        'projected_weeks_p50': round(projected_weeks_p50, 1),
        'projected_work_p85': int(projected_work_p85),
        'projected_effort_p85': int(result['effort_stats']['p85']),
        'backlog': backlog,
        'can_meet_deadline': can_meet_deadline,
        'scope_completion_pct': round(scope_completion_pct),
        'deadline_completion_pct': round(deadline_completion_pct),
        'percentile_stats': result['percentile_stats'],
        'ml_models': result['ml_results'],
        'forecast_method': 'Machine Learning + Team Dynamics'
    }


def ml_forecast_how_many(
    tp_samples: List[float],
    start_date: str,
    end_date: str,
    team_size: int = 1,
    min_contributors: Optional[int] = None,
    max_contributors: Optional[int] = None,
    s_curve_size: int = 0,
    lt_samples: Optional[List[float]] = None,
    n_simulations: int = 1000
) -> Dict[str, Any]:
    """
    ML forecast: How many items in a time period?

    Args:
        tp_samples: Historical throughput
        start_date: Start date
        end_date: End date
        team_size: Total team size
        min_contributors: Minimum contributors
        max_contributors: Maximum contributors
        s_curve_size: S-curve percentage
        lt_samples: Lead time samples
        n_simulations: Number of simulations

    Returns:
        Forecast of items deliverable in period
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

    days = (end - start).days
    weeks = math.ceil(days / 7.0)

    # Initialize forecaster
    forecaster = MLDeadlineForecaster(
        tp_samples=tp_samples,
        team_size=team_size,
        min_contributors=min_contributors,
        max_contributors=max_contributors,
        s_curve_size=s_curve_size,
        lt_samples=lt_samples
    )

    # Train ML models using K-Fold CV with Grid Search
    forecaster.ml_forecaster.train_models(np.array(tp_samples), use_kfold_cv=True)

    # Get ML forecast
    ml_forecasts = forecaster.ml_forecaster.forecast(
        np.array(tp_samples),
        steps=weeks,
        model_name='ensemble'
    )

    ensemble_stats = forecaster.ml_forecaster.get_ensemble_forecast(ml_forecasts)

    # Simulate total items
    items_completed = []

    for sim in range(n_simulations):
        total_items = 0

        for week_idx in range(weeks):
            # ML forecast with variation
            if week_idx < len(ensemble_stats['mean']):
                base_tp = ensemble_stats['mean'][week_idx]
                variation = np.random.normal(0, ensemble_stats['std'][week_idx])
                forecast_tp = max(0, base_tp + variation)
            else:
                forecast_tp = ensemble_stats['mean'][-1]

            # Apply team dynamics
            percent_complete = (week_idx / weeks * 100) if weeks > 0 else 0
            adjusted_tp = forecaster._apply_team_dynamics(forecast_tp, percent_complete)

            total_items += adjusted_tp

        items_completed.append(int(total_items))

    items_completed_sorted = sorted(items_completed)

    return {
        'start_date': start.strftime('%d/%m/%Y'),
        'end_date': end.strftime('%d/%m/%Y'),
        'days': days,
        'weeks': weeks,
        'items_p95': int(np.percentile(items_completed_sorted, 95)),
        'items_p85': int(np.percentile(items_completed_sorted, 85)),
        'items_p50': int(np.percentile(items_completed_sorted, 50)),
        'items_mean': round(np.mean(items_completed), 1),
        'ml_forecasts': ensemble_stats,
        'forecast_method': 'Machine Learning + Team Dynamics'
    }


def ml_forecast_when(
    tp_samples: List[float],
    backlog: int,
    start_date: str,
    team_size: int = 1,
    min_contributors: Optional[int] = None,
    max_contributors: Optional[int] = None,
    s_curve_size: int = 0,
    lt_samples: Optional[List[float]] = None,
    split_rate_samples: Optional[List[float]] = None,
    forecast_weeks: int = 20,
    n_simulations: int = 1000
) -> Dict[str, Any]:
    """
    ML forecast: When will backlog be completed?

    Args:
        tp_samples: Historical throughput
        backlog: Number of items
        start_date: Start date
        team_size: Total team size
        min_contributors: Minimum contributors
        max_contributors: Maximum contributors
        s_curve_size: S-curve percentage
        lt_samples: Lead time samples
        split_rate_samples: Split rate samples
        forecast_weeks: Weeks to forecast
        n_simulations: Number of simulations

    Returns:
        Forecast completion dates
    """
    # Parse date
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

    # Initialize forecaster
    forecaster = MLDeadlineForecaster(
        tp_samples=tp_samples,
        team_size=team_size,
        min_contributors=min_contributors,
        max_contributors=max_contributors,
        s_curve_size=s_curve_size,
        lt_samples=lt_samples,
        split_rate_samples=split_rate_samples
    )

    # Run simulation
    result = forecaster.simulate_project_with_ml(
        backlog=backlog,
        forecast_steps=forecast_weeks,
        n_simulations=n_simulations
    )

    percentile_stats = result['percentile_stats']

    # Calculate dates
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
        'start_date': start.strftime('%d/%m/%y'),
        'date_p95': date_p95.strftime('%d/%m/%y'),
        'date_p85': date_p85.strftime('%d/%m/%y'),
        'date_p50': date_p50.strftime('%d/%m/%y'),
        'weeks_p95': round(weeks_p95, 1),
        'weeks_p85': round(weeks_p85, 1),
        'weeks_p50': round(weeks_p50, 1),
        'effort_p85': int(result['effort_stats']['p85']),
        'percentile_stats': percentile_stats,
        'ml_models': result['ml_results'],
        'forecast_method': 'Machine Learning + Team Dynamics'
    }
