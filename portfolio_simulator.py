"""
Portfolio Simulator - Monte Carlo simulation for portfolio-level forecasting
Aggregates forecasts from multiple projects to provide portfolio completion estimates
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class ProjectForecastInput:
    """Input data for a single project in portfolio simulation"""
    project_id: int
    project_name: str
    backlog: int
    tp_samples: List[float]
    priority: int = 3
    cod_weekly: Optional[float] = None
    wsjf_score: Optional[float] = None
    depends_on: List[int] = None  # List of project_ids this depends on

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class ProjectForecastResult:
    """Forecast result for a single project"""
    project_id: int
    project_name: str
    p50_weeks: float
    p85_weeks: float
    p95_weeks: float
    mean_weeks: float
    std_weeks: float
    cod_total: Optional[float] = None  # Total CoD = cod_weekly * p85_weeks


@dataclass
class PortfolioForecastResult:
    """Result of portfolio-level Monte Carlo simulation"""
    portfolio_name: str
    n_simulations: int

    # Portfolio completion times (in weeks)
    p50_weeks: float
    p85_weeks: float
    p95_weeks: float
    mean_weeks: float
    std_weeks: float

    # Individual project results
    project_results: List[ProjectForecastResult]

    # Cost of Delay analysis
    total_cod: Optional[float] = None
    cod_by_project: Optional[Dict[int, float]] = None

    # Critical path
    critical_path_projects: List[int] = None

    # Risk metrics
    high_risk_projects: List[int] = None
    risk_score: float = 0.0  # Overall portfolio risk (0-100)

    def to_dict(self):
        return {
            'portfolio_name': self.portfolio_name,
            'n_simulations': self.n_simulations,
            'completion_forecast': {
                'p50_weeks': round(self.p50_weeks, 2),
                'p85_weeks': round(self.p85_weeks, 2),
                'p95_weeks': round(self.p95_weeks, 2),
                'mean_weeks': round(self.mean_weeks, 2),
                'std_weeks': round(self.std_weeks, 2)
            },
            'project_results': [
                {
                    'project_id': pr.project_id,
                    'project_name': pr.project_name,
                    'p50_weeks': round(pr.p50_weeks, 2),
                    'p85_weeks': round(pr.p85_weeks, 2),
                    'p95_weeks': round(pr.p95_weeks, 2),
                    'mean_weeks': round(pr.mean_weeks, 2),
                    'cod_total': round(pr.cod_total, 2) if pr.cod_total else None
                }
                for pr in self.project_results
            ],
            'cost_of_delay': {
                'total_cod': round(self.total_cod, 2) if self.total_cod else None,
                'by_project': {
                    str(k): round(v, 2)
                    for k, v in (self.cod_by_project or {}).items()
                }
            },
            'critical_path': {
                'projects': self.critical_path_projects or []
            },
            'risk': {
                'score': round(self.risk_score, 2),
                'high_risk_projects': self.high_risk_projects or []
            }
        }


def simulate_project_throughput(
    tp_samples: List[float],
    backlog: int,
    n_simulations: int = 10000
) -> Tuple[np.ndarray, Dict]:
    """
    Simulate throughput for a single project using Monte Carlo.

    Returns:
        - Array of simulated weeks to completion
        - Dictionary with statistics
    """
    if not tp_samples or len(tp_samples) == 0:
        raise ValueError("tp_samples cannot be empty")

    if backlog <= 0:
        raise ValueError("backlog must be positive")

    tp_array = np.array(tp_samples)
    mean_tp = np.mean(tp_array)
    std_tp = np.std(tp_array, ddof=1) if len(tp_array) > 1 else mean_tp * 0.2

    # Generate random throughput samples
    simulated_throughput = np.random.normal(mean_tp, std_tp, n_simulations)
    simulated_throughput = np.maximum(simulated_throughput, 0.1)  # Prevent division by zero

    # Calculate weeks to completion for each simulation
    simulated_weeks = backlog / simulated_throughput

    stats = {
        'mean': float(np.mean(simulated_weeks)),
        'std': float(np.std(simulated_weeks)),
        'p50': float(np.percentile(simulated_weeks, 50)),
        'p85': float(np.percentile(simulated_weeks, 85)),
        'p95': float(np.percentile(simulated_weeks, 95))
    }

    return simulated_weeks, stats


def simulate_portfolio_parallel(
    projects: List[ProjectForecastInput],
    n_simulations: int = 10000,
    confidence_level: str = 'P85'
) -> PortfolioForecastResult:
    """
    Simulate portfolio completion assuming projects run in parallel.
    Portfolio completes when ALL projects complete.

    Args:
        projects: List of project forecast inputs
        n_simulations: Number of Monte Carlo simulations
        confidence_level: 'P50', 'P85', or 'P95'

    Returns:
        PortfolioForecastResult with completion forecast
    """
    if not projects:
        raise ValueError("projects list cannot be empty")

    # Simulate each project
    project_results = []
    project_simulations = {}  # project_id -> array of simulated weeks

    for project in projects:
        try:
            simulated_weeks, stats = simulate_project_throughput(
                project.tp_samples,
                project.backlog,
                n_simulations
            )

            project_simulations[project.project_id] = simulated_weeks

            # Calculate CoD if provided
            cod_total = None
            if project.cod_weekly:
                cod_total = project.cod_weekly * stats['p85']

            result = ProjectForecastResult(
                project_id=project.project_id,
                project_name=project.project_name,
                p50_weeks=stats['p50'],
                p85_weeks=stats['p85'],
                p95_weeks=stats['p95'],
                mean_weeks=stats['mean'],
                std_weeks=stats['std'],
                cod_total=cod_total
            )

            project_results.append(result)

        except Exception as e:
            print(f"Warning: Failed to simulate project {project.project_id}: {e}")
            continue

    if not project_results:
        raise ValueError("All project simulations failed")

    # Portfolio completion = max of all projects (parallel execution)
    # For each simulation, take the max completion time across all projects
    all_project_weeks = np.array([project_simulations[p.project_id] for p in projects])
    portfolio_weeks = np.max(all_project_weeks, axis=0)

    # Calculate portfolio statistics
    portfolio_p50 = float(np.percentile(portfolio_weeks, 50))
    portfolio_p85 = float(np.percentile(portfolio_weeks, 85))
    portfolio_p95 = float(np.percentile(portfolio_weeks, 95))
    portfolio_mean = float(np.mean(portfolio_weeks))
    portfolio_std = float(np.std(portfolio_weeks))

    # Calculate total CoD
    total_cod = sum(pr.cod_total for pr in project_results if pr.cod_total)
    cod_by_project = {
        pr.project_id: pr.cod_total
        for pr in project_results if pr.cod_total
    }

    # Identify critical path projects (projects that often determine portfolio completion)
    # A project is on the critical path if it's the longest in many simulations
    critical_counts = {}
    for sim_idx in range(n_simulations):
        # Find which project took longest in this simulation
        max_week = -1
        max_project = None
        for project in projects:
            week = project_simulations[project.project_id][sim_idx]
            if week > max_week:
                max_week = week
                max_project = project.project_id

        critical_counts[max_project] = critical_counts.get(max_project, 0) + 1

    # Projects that are critical in >20% of simulations
    critical_threshold = n_simulations * 0.2
    critical_path_projects = [
        pid for pid, count in critical_counts.items()
        if count >= critical_threshold
    ]

    # Identify high-risk projects (high variance)
    high_risk_projects = []
    risk_scores = []
    for project, result in zip(projects, project_results):
        # Risk = coefficient of variation (std / mean)
        cv = result.std_weeks / result.mean_weeks if result.mean_weeks > 0 else 0
        risk_scores.append(cv)
        if cv > 0.5:  # High variability
            high_risk_projects.append(project.project_id)

    # Overall portfolio risk score (0-100)
    avg_cv = np.mean(risk_scores) if risk_scores else 0
    risk_score = min(100, avg_cv * 100)

    return PortfolioForecastResult(
        portfolio_name="Portfolio",
        n_simulations=n_simulations,
        p50_weeks=portfolio_p50,
        p85_weeks=portfolio_p85,
        p95_weeks=portfolio_p95,
        mean_weeks=portfolio_mean,
        std_weeks=portfolio_std,
        project_results=project_results,
        total_cod=total_cod if total_cod > 0 else None,
        cod_by_project=cod_by_project if cod_by_project else None,
        critical_path_projects=critical_path_projects,
        high_risk_projects=high_risk_projects,
        risk_score=risk_score
    )


def simulate_portfolio_sequential(
    projects: List[ProjectForecastInput],
    n_simulations: int = 10000,
    confidence_level: str = 'P85'
) -> PortfolioForecastResult:
    """
    Simulate portfolio completion assuming projects run sequentially (one after another).
    Projects are executed in order based on WSJF score (highest first) or priority.

    Args:
        projects: List of project forecast inputs
        n_simulations: Number of Monte Carlo simulations
        confidence_level: 'P50', 'P85', or 'P95'

    Returns:
        PortfolioForecastResult with completion forecast
    """
    if not projects:
        raise ValueError("projects list cannot be empty")

    # Sort projects by WSJF (highest first), then priority (lowest number = highest priority)
    sorted_projects = sorted(
        projects,
        key=lambda p: (-p.wsjf_score if p.wsjf_score else 0, p.priority)
    )

    # Simulate each project
    project_results = []
    project_simulations = {}

    for project in sorted_projects:
        try:
            simulated_weeks, stats = simulate_project_throughput(
                project.tp_samples,
                project.backlog,
                n_simulations
            )

            project_simulations[project.project_id] = simulated_weeks

            # Calculate CoD
            cod_total = None
            if project.cod_weekly:
                cod_total = project.cod_weekly * stats['p85']

            result = ProjectForecastResult(
                project_id=project.project_id,
                project_name=project.project_name,
                p50_weeks=stats['p50'],
                p85_weeks=stats['p85'],
                p95_weeks=stats['p95'],
                mean_weeks=stats['mean'],
                std_weeks=stats['std'],
                cod_total=cod_total
            )

            project_results.append(result)

        except Exception as e:
            print(f"Warning: Failed to simulate project {project.project_id}: {e}")
            continue

    if not project_results:
        raise ValueError("All project simulations failed")

    # Portfolio completion = sum of all projects (sequential execution)
    all_project_weeks = np.array([project_simulations[p.project_id] for p in sorted_projects])
    portfolio_weeks = np.sum(all_project_weeks, axis=0)

    # Calculate portfolio statistics
    portfolio_p50 = float(np.percentile(portfolio_weeks, 50))
    portfolio_p85 = float(np.percentile(portfolio_weeks, 85))
    portfolio_p95 = float(np.percentile(portfolio_weeks, 95))
    portfolio_mean = float(np.mean(portfolio_weeks))
    portfolio_std = float(np.std(portfolio_weeks))

    # Calculate total CoD
    total_cod = sum(pr.cod_total for pr in project_results if pr.cod_total)
    cod_by_project = {
        pr.project_id: pr.cod_total
        for pr in project_results if pr.cod_total
    }

    # All projects are on critical path in sequential execution
    critical_path_projects = [p.project_id for p in sorted_projects]

    # Identify high-risk projects
    high_risk_projects = []
    risk_scores = []
    for project, result in zip(sorted_projects, project_results):
        cv = result.std_weeks / result.mean_weeks if result.mean_weeks > 0 else 0
        risk_scores.append(cv)
        if cv > 0.5:
            high_risk_projects.append(project.project_id)

    avg_cv = np.mean(risk_scores) if risk_scores else 0
    risk_score = min(100, avg_cv * 100)

    return PortfolioForecastResult(
        portfolio_name="Portfolio (Sequential)",
        n_simulations=n_simulations,
        p50_weeks=portfolio_p50,
        p85_weeks=portfolio_p85,
        p95_weeks=portfolio_p95,
        mean_weeks=portfolio_mean,
        std_weeks=portfolio_std,
        project_results=project_results,
        total_cod=total_cod if total_cod > 0 else None,
        cod_by_project=cod_by_project if cod_by_project else None,
        critical_path_projects=critical_path_projects,
        high_risk_projects=high_risk_projects,
        risk_score=risk_score
    )


def compare_execution_strategies(
    projects: List[ProjectForecastInput],
    n_simulations: int = 10000
) -> Dict:
    """
    Compare parallel vs sequential execution strategies.

    Returns:
        Dictionary with results from both strategies
    """
    parallel_result = simulate_portfolio_parallel(projects, n_simulations)
    sequential_result = simulate_portfolio_sequential(projects, n_simulations)

    return {
        'parallel': parallel_result.to_dict(),
        'sequential': sequential_result.to_dict(),
        'comparison': {
            'time_diff_p85': round(sequential_result.p85_weeks - parallel_result.p85_weeks, 2),
            'cod_diff': round(
                (sequential_result.total_cod or 0) - (parallel_result.total_cod or 0), 2
            ) if (sequential_result.total_cod and parallel_result.total_cod) else None,
            'recommendation': 'parallel' if parallel_result.p85_weeks < sequential_result.p85_weeks else 'sequential'
        }
    }
