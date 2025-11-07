"""
Cost of Delay Portfolio Analyzer
Advanced CoD analysis and WSJF optimization for portfolios
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class ProjectCoDProfile:
    """Cost of Delay profile for a single project"""
    project_id: int
    project_name: str

    # Duration estimates (weeks)
    duration_p50: float
    duration_p85: float
    duration_p95: float

    # Cost of Delay (R$/week)
    cod_weekly: float

    # WSJF components (0-100 scale)
    business_value: int
    time_criticality: int
    risk_reduction: int

    # Calculated fields
    wsjf_score: Optional[float] = None
    total_cod: Optional[float] = None  # cod_weekly * duration

    def __post_init__(self):
        """Calculate derived fields"""
        # WSJF = (Business Value + Time Criticality + Risk Reduction) / Duration
        if self.duration_p50 > 0:
            self.wsjf_score = (
                self.business_value + self.time_criticality + self.risk_reduction
            ) / self.duration_p50

        # Total CoD = weekly cost * expected duration (P85)
        if self.cod_weekly:
            self.total_cod = self.cod_weekly * self.duration_p85


@dataclass
class CoDOptimizationResult:
    """Result of CoD-based portfolio optimization"""

    # Original sequence
    original_sequence: List[int]  # project_ids
    original_total_cod: float
    original_duration: float

    # Optimized sequence (by WSJF)
    optimized_sequence: List[int]  # project_ids sorted by WSJF
    optimized_total_cod: float
    optimized_duration: float

    # Savings
    cod_savings: float
    cod_savings_pct: float
    time_savings: float

    # Project rankings
    project_rankings: Dict[int, Dict]  # project_id -> {rank, wsjf, cod}

    def to_dict(self):
        return {
            'original': {
                'sequence': self.original_sequence,
                'total_cod': round(self.original_total_cod, 2),
                'duration': round(self.original_duration, 2)
            },
            'optimized': {
                'sequence': self.optimized_sequence,
                'total_cod': round(self.optimized_total_cod, 2),
                'duration': round(self.optimized_duration, 2)
            },
            'savings': {
                'cod_savings': round(self.cod_savings, 2),
                'cod_savings_pct': round(self.cod_savings_pct, 2),
                'time_savings': round(self.time_savings, 2)
            },
            'project_rankings': {
                str(k): {
                    'rank': v['rank'],
                    'wsjf': round(v['wsjf'], 2),
                    'cod': round(v['cod'], 2),
                    'name': v['name']
                }
                for k, v in self.project_rankings.items()
            }
        }


@dataclass
class PortfolioCoDAnalysis:
    """Complete CoD analysis for a portfolio"""
    portfolio_id: int
    portfolio_name: str

    # Projects
    projects: List[ProjectCoDProfile]

    # Portfolio totals
    total_cod_parallel: float  # If all run in parallel
    total_cod_sequential: float  # If run in sequence (unoptimized)
    total_cod_optimized: float  # If run in sequence (WSJF optimized)

    # Duration
    duration_parallel_p85: float
    duration_sequential_p85: float

    # Optimization
    optimization_result: Optional[CoDOptimizationResult] = None

    # Risk assessment
    high_cod_projects: List[int] = None  # Projects with high CoD
    critical_deadline_projects: List[int] = None  # Projects with high time criticality

    def to_dict(self):
        return {
            'portfolio_id': self.portfolio_id,
            'portfolio_name': self.portfolio_name,
            'projects': [
                {
                    'project_id': p.project_id,
                    'project_name': p.project_name,
                    'duration_p85': round(p.duration_p85, 2),
                    'cod_weekly': round(p.cod_weekly, 2) if p.cod_weekly else None,
                    'wsjf_score': round(p.wsjf_score, 2) if p.wsjf_score else None,
                    'total_cod': round(p.total_cod, 2) if p.total_cod else None,
                    'business_value': p.business_value,
                    'time_criticality': p.time_criticality,
                    'risk_reduction': p.risk_reduction
                }
                for p in self.projects
            ],
            'totals': {
                'parallel': {
                    'duration_p85': round(self.duration_parallel_p85, 2),
                    'total_cod': round(self.total_cod_parallel, 2)
                },
                'sequential_unoptimized': {
                    'duration_p85': round(self.duration_sequential_p85, 2),
                    'total_cod': round(self.total_cod_sequential, 2)
                },
                'sequential_optimized': {
                    'duration_p85': round(self.duration_sequential_p85, 2),
                    'total_cod': round(self.total_cod_optimized, 2)
                }
            },
            'optimization': self.optimization_result.to_dict() if self.optimization_result else None,
            'risk_assessment': {
                'high_cod_projects': self.high_cod_projects or [],
                'critical_deadline_projects': self.critical_deadline_projects or []
            }
        }


def calculate_wsjf(business_value: int, time_criticality: int,
                   risk_reduction: int, duration: float) -> float:
    """
    Calculate WSJF score.

    WSJF = (Business Value + Time Criticality + Risk Reduction/Opportunity Enablement) / Job Duration

    Higher WSJF = higher priority (should be done first)
    """
    if duration <= 0:
        return 0.0

    return (business_value + time_criticality + risk_reduction) / duration


def optimize_sequence_by_wsjf(projects: List[ProjectCoDProfile]) -> List[ProjectCoDProfile]:
    """
    Optimize project sequence using WSJF.

    Projects with higher WSJF should be done first to minimize total CoD.

    Returns:
        Projects sorted by WSJF (descending)
    """
    # Ensure all projects have WSJF calculated
    for project in projects:
        if project.wsjf_score is None and project.duration_p50 > 0:
            project.wsjf_score = calculate_wsjf(
                project.business_value,
                project.time_criticality,
                project.risk_reduction,
                project.duration_p50
            )

    # Sort by WSJF descending (highest first)
    sorted_projects = sorted(projects, key=lambda p: p.wsjf_score or 0, reverse=True)

    return sorted_projects


def calculate_sequential_cod(projects: List[ProjectCoDProfile]) -> Tuple[float, float]:
    """
    Calculate total CoD for sequential execution (projects in order).

    In sequential execution:
    - Project 1 completes at time T1, incurs CoD = cod_weekly * T1
    - Project 2 completes at time T1+T2, incurs CoD = cod_weekly * (T1+T2)
    - etc.

    Returns:
        (total_cod, total_duration)
    """
    total_cod = 0.0
    cumulative_time = 0.0
    total_duration = 0.0

    for project in projects:
        # Add project duration to cumulative time
        cumulative_time += project.duration_p85
        total_duration += project.duration_p85

        # CoD for this project = weekly rate * time until completion
        if project.cod_weekly:
            project_cod = project.cod_weekly * cumulative_time
            total_cod += project_cod

    return total_cod, total_duration


def calculate_parallel_cod(projects: List[ProjectCoDProfile]) -> Tuple[float, float]:
    """
    Calculate total CoD for parallel execution.

    In parallel execution:
    - All projects run simultaneously
    - Portfolio completes when longest project completes
    - Each project incurs CoD = cod_weekly * its_own_duration

    Returns:
        (total_cod, total_duration)
    """
    if not projects:
        return 0.0, 0.0

    total_cod = sum(p.cod_weekly * p.duration_p85 for p in projects if p.cod_weekly)
    max_duration = max(p.duration_p85 for p in projects)

    return total_cod, max_duration


def analyze_portfolio_cod(
    portfolio_id: int,
    portfolio_name: str,
    projects: List[ProjectCoDProfile]
) -> PortfolioCoDAnalysis:
    """
    Perform complete CoD analysis for a portfolio.

    Analyzes:
    - Current sequence vs WSJF-optimized sequence
    - Parallel vs sequential execution
    - Identifies high-CoD and critical projects

    Args:
        portfolio_id: Portfolio ID
        portfolio_name: Portfolio name
        projects: List of projects with CoD profiles

    Returns:
        PortfolioCoDAnalysis with complete analysis
    """
    if not projects:
        raise ValueError("Projects list cannot be empty")

    # Calculate parallel execution CoD
    total_cod_parallel, duration_parallel = calculate_parallel_cod(projects)

    # Calculate sequential CoD (original order)
    total_cod_sequential, duration_sequential = calculate_sequential_cod(projects)

    # Optimize sequence by WSJF
    optimized_projects = optimize_sequence_by_wsjf(projects.copy())
    total_cod_optimized, _ = calculate_sequential_cod(optimized_projects)

    # Create optimization result
    original_sequence = [p.project_id for p in projects]
    optimized_sequence = [p.project_id for p in optimized_projects]

    cod_savings = total_cod_sequential - total_cod_optimized
    cod_savings_pct = (cod_savings / total_cod_sequential * 100) if total_cod_sequential > 0 else 0

    # Create project rankings
    project_rankings = {}
    for rank, project in enumerate(optimized_projects, 1):
        project_rankings[project.project_id] = {
            'rank': rank,
            'wsjf': project.wsjf_score or 0,
            'cod': project.total_cod or 0,
            'name': project.project_name
        }

    optimization_result = CoDOptimizationResult(
        original_sequence=original_sequence,
        original_total_cod=total_cod_sequential,
        original_duration=duration_sequential,
        optimized_sequence=optimized_sequence,
        optimized_total_cod=total_cod_optimized,
        optimized_duration=duration_sequential,  # Same duration, different order
        cod_savings=cod_savings,
        cod_savings_pct=cod_savings_pct,
        time_savings=0.0,  # Sequential has same total time regardless of order
        project_rankings=project_rankings
    )

    # Identify high-CoD projects (top 25% by total CoD)
    projects_by_cod = sorted(
        [p for p in projects if p.total_cod],
        key=lambda p: p.total_cod,
        reverse=True
    )
    threshold_idx = max(1, len(projects_by_cod) // 4)
    high_cod_projects = [p.project_id for p in projects_by_cod[:threshold_idx]]

    # Identify critical deadline projects (time_criticality >= 70)
    critical_deadline_projects = [
        p.project_id for p in projects
        if p.time_criticality >= 70
    ]

    return PortfolioCoDAnalysis(
        portfolio_id=portfolio_id,
        portfolio_name=portfolio_name,
        projects=projects,
        total_cod_parallel=total_cod_parallel,
        total_cod_sequential=total_cod_sequential,
        total_cod_optimized=total_cod_optimized,
        duration_parallel_p85=duration_parallel,
        duration_sequential_p85=duration_sequential,
        optimization_result=optimization_result,
        high_cod_projects=high_cod_projects,
        critical_deadline_projects=critical_deadline_projects
    )


def calculate_delay_impact(
    project: ProjectCoDProfile,
    delay_weeks: float
) -> Dict:
    """
    Calculate financial impact of delaying a project.

    Args:
        project: Project CoD profile
        delay_weeks: Number of weeks to delay

    Returns:
        Dictionary with impact analysis
    """
    if not project.cod_weekly:
        return {
            'project_id': project.project_id,
            'project_name': project.project_name,
            'delay_weeks': delay_weeks,
            'additional_cod': 0,
            'new_total_cod': 0,
            'warning': 'No CoD data available'
        }

    additional_cod = project.cod_weekly * delay_weeks
    original_total = project.total_cod or (project.cod_weekly * project.duration_p85)
    new_total = original_total + additional_cod
    increase_pct = (additional_cod / original_total * 100) if original_total > 0 else 0

    return {
        'project_id': project.project_id,
        'project_name': project.project_name,
        'delay_weeks': delay_weeks,
        'cod_weekly': project.cod_weekly,
        'additional_cod': round(additional_cod, 2),
        'original_total_cod': round(original_total, 2),
        'new_total_cod': round(new_total, 2),
        'increase_pct': round(increase_pct, 2)
    }


def compare_prioritization_strategies(
    projects: List[ProjectCoDProfile]
) -> Dict:
    """
    Compare different prioritization strategies.

    Strategies:
    1. WSJF (recommended)
    2. Shortest Job First (by duration)
    3. Highest CoD First
    4. Business Value First

    Returns:
        Comparison of total CoD for each strategy
    """
    if not projects:
        return {}

    # Strategy 1: WSJF
    wsjf_sorted = optimize_sequence_by_wsjf(projects.copy())
    wsjf_cod, _ = calculate_sequential_cod(wsjf_sorted)

    # Strategy 2: Shortest Job First
    sjf_sorted = sorted(projects.copy(), key=lambda p: p.duration_p50)
    sjf_cod, _ = calculate_sequential_cod(sjf_sorted)

    # Strategy 3: Highest CoD First
    cod_sorted = sorted(
        projects.copy(),
        key=lambda p: p.cod_weekly if p.cod_weekly else 0,
        reverse=True
    )
    cod_first_cod, _ = calculate_sequential_cod(cod_sorted)

    # Strategy 4: Business Value First
    bv_sorted = sorted(projects.copy(), key=lambda p: p.business_value, reverse=True)
    bv_cod, _ = calculate_sequential_cod(bv_sorted)

    # Find best strategy
    strategies = {
        'wsjf': wsjf_cod,
        'shortest_first': sjf_cod,
        'highest_cod_first': cod_first_cod,
        'business_value_first': bv_cod
    }

    best_strategy = min(strategies.items(), key=lambda x: x[1])

    return {
        'strategies': {
            'wsjf': {
                'total_cod': round(wsjf_cod, 2),
                'sequence': [p.project_id for p in wsjf_sorted],
                'is_best': best_strategy[0] == 'wsjf'
            },
            'shortest_first': {
                'total_cod': round(sjf_cod, 2),
                'sequence': [p.project_id for p in sjf_sorted],
                'is_best': best_strategy[0] == 'shortest_first'
            },
            'highest_cod_first': {
                'total_cod': round(cod_first_cod, 2),
                'sequence': [p.project_id for p in cod_sorted],
                'is_best': best_strategy[0] == 'highest_cod_first'
            },
            'business_value_first': {
                'total_cod': round(bv_cod, 2),
                'sequence': [p.project_id for p in bv_sorted],
                'is_best': best_strategy[0] == 'business_value_first'
            }
        },
        'best_strategy': best_strategy[0],
        'best_total_cod': round(best_strategy[1], 2),
        'comparison': {
            'wsjf_vs_bv_savings': round(bv_cod - wsjf_cod, 2),
            'wsjf_vs_sjf_savings': round(sjf_cod - wsjf_cod, 2),
            'wsjf_vs_cod_savings': round(cod_first_cod - wsjf_cod, 2)
        }
    }
