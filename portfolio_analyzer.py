"""
Portfolio Analyzer for Flow Forecaster
Analyzes multiple projects to provide portfolio-level insights
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from models import Project, Forecast, Actual
from accuracy_metrics import calculate_accuracy_metrics


@dataclass
class ProjectHealthScore:
    """Health score for a single project"""
    project_id: int
    project_name: str
    overall_score: float  # 0-100
    forecast_accuracy_score: float  # 0-100
    delivery_performance_score: float  # 0-100
    capacity_health_score: float  # 0-100
    risk_score: float  # 0-100 (higher = riskier)

    # Detailed metrics
    mape: Optional[float]
    bias: Optional[str]
    forecast_count: int
    actual_count: int

    # Status indicators
    health_status: str  # excellent, good, warning, critical
    alerts: List[str]

    def to_dict(self) -> Dict:
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'overall_score': round(self.overall_score, 2),
            'forecast_accuracy_score': round(self.forecast_accuracy_score, 2),
            'delivery_performance_score': round(self.delivery_performance_score, 2),
            'capacity_health_score': round(self.capacity_health_score, 2),
            'risk_score': round(self.risk_score, 2),
            'mape': round(self.mape, 2) if self.mape else None,
            'bias': self.bias,
            'forecast_count': self.forecast_count,
            'actual_count': self.actual_count,
            'health_status': self.health_status,
            'alerts': self.alerts
        }


@dataclass
class CapacityAnalysis:
    """Portfolio capacity analysis"""
    total_capacity: float  # Total FTE available
    allocated_capacity: float  # Total FTE allocated to projects
    available_capacity: float  # Remaining capacity
    utilization_rate: float  # % of capacity used

    over_allocated_projects: List[Dict]
    under_allocated_projects: List[Dict]

    status: str  # optimal, over_utilized, under_utilized
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            'total_capacity': round(self.total_capacity, 2),
            'allocated_capacity': round(self.allocated_capacity, 2),
            'available_capacity': round(self.available_capacity, 2),
            'utilization_rate': round(self.utilization_rate, 2),
            'over_allocated_projects': self.over_allocated_projects,
            'under_allocated_projects': self.under_allocated_projects,
            'status': self.status,
            'recommendations': self.recommendations
        }


@dataclass
class PrioritizationMatrix:
    """Project prioritization based on value vs risk"""
    high_value_low_risk: List[Dict]  # Quick wins
    high_value_high_risk: List[Dict]  # Strategic bets
    low_value_low_risk: List[Dict]  # Fill-ins
    low_value_high_risk: List[Dict]  # Money pits (avoid)

    def to_dict(self) -> Dict:
        return {
            'high_value_low_risk': self.high_value_low_risk,
            'high_value_high_risk': self.high_value_high_risk,
            'low_value_low_risk': self.low_value_low_risk,
            'low_value_high_risk': self.low_value_high_risk
        }


def calculate_project_health_score(
    project: Project,
    forecasts: List[Forecast],
    actuals_map: Dict[int, List[Actual]]
) -> ProjectHealthScore:
    """
    Calculate comprehensive health score for a project.

    Args:
        project: Project instance
        forecasts: List of forecasts for this project
        actuals_map: Map of forecast_id to list of actuals

    Returns:
        ProjectHealthScore object
    """
    alerts = []

    # 1. Forecast Accuracy Score (based on MAPE if actuals exist)
    forecast_accuracy_score = 50.0  # Default if no actuals
    mape = None
    bias = None
    actual_count = 0

    if forecasts:
        # Get forecasts with actuals
        forecasts_with_actuals = []
        actuals_with_data = []

        for forecast in forecasts:
            if forecast.id in actuals_map and actuals_map[forecast.id]:
                actual = actuals_map[forecast.id][0]  # Take first actual
                if forecast.projected_weeks_p85 and actual.actual_weeks_taken:
                    forecasts_with_actuals.append(forecast.projected_weeks_p85)
                    actuals_with_data.append(actual.actual_weeks_taken)
                    actual_count += 1

        if len(forecasts_with_actuals) >= 2:
            try:
                metrics = calculate_accuracy_metrics(forecasts_with_actuals, actuals_with_data)
                mape = metrics.mape
                bias = metrics.bias_direction

                # Convert MAPE to score (0-100, lower MAPE = higher score)
                if mape < 10:
                    forecast_accuracy_score = 100
                elif mape < 20:
                    forecast_accuracy_score = 90
                elif mape < 30:
                    forecast_accuracy_score = 75
                elif mape < 50:
                    forecast_accuracy_score = 50
                else:
                    forecast_accuracy_score = 25
            except:
                pass
        elif actual_count == 0:
            alerts.append("Nenhum resultado real registrado para validar previsões")

    # 2. Delivery Performance Score (based on meeting deadlines)
    delivery_performance_score = 70.0  # Default
    if forecasts:
        on_time_count = sum(1 for f in forecasts if f.can_meet_deadline)
        if len(forecasts) > 0:
            delivery_performance_score = (on_time_count / len(forecasts)) * 100

    # 3. Capacity Health Score
    capacity_health_score = 100.0
    if project.capacity_allocated < 0.5:
        capacity_health_score = 50
        alerts.append(f"Capacidade alocada muito baixa ({project.capacity_allocated} FTE)")
    elif project.capacity_allocated > project.team_size * 1.2:
        capacity_health_score = 40
        alerts.append(f"Projeto sobre-alocado: {project.capacity_allocated} FTE com time de {project.team_size}")

    # 4. Risk Score (based on project risk level)
    risk_map = {
        'low': 20,
        'medium': 50,
        'high': 75,
        'critical': 95
    }
    risk_score = risk_map.get(project.risk_level, 50)

    # 5. Overall Score (weighted average)
    overall_score = (
        forecast_accuracy_score * 0.35 +
        delivery_performance_score * 0.30 +
        capacity_health_score * 0.20 +
        (100 - risk_score) * 0.15  # Lower risk = higher score
    )

    # Determine health status
    if overall_score >= 80:
        health_status = 'excellent'
    elif overall_score >= 60:
        health_status = 'good'
    elif overall_score >= 40:
        health_status = 'warning'
    else:
        health_status = 'critical'
        alerts.append("Health score crítico - revisão urgente necessária")

    return ProjectHealthScore(
        project_id=project.id,
        project_name=project.name,
        overall_score=overall_score,
        forecast_accuracy_score=forecast_accuracy_score,
        delivery_performance_score=delivery_performance_score,
        capacity_health_score=capacity_health_score,
        risk_score=risk_score,
        mape=mape,
        bias=bias,
        forecast_count=len(forecasts),
        actual_count=actual_count,
        health_status=health_status,
        alerts=alerts
    )


def analyze_portfolio_capacity(
    projects: List[Project],
    total_available_capacity: Optional[float] = None
) -> CapacityAnalysis:
    """
    Analyze capacity allocation across portfolio.

    Args:
        projects: List of active projects
        total_available_capacity: Total FTE available (if None, calculated from projects)

    Returns:
        CapacityAnalysis object
    """
    # Calculate total allocated capacity
    allocated_capacity = sum(p.capacity_allocated for p in projects if p.status == 'active')

    # Estimate total capacity if not provided
    if total_available_capacity is None:
        # Estimate: sum of all team sizes
        total_available_capacity = sum(p.team_size for p in projects if p.status == 'active')

    available_capacity = max(0, total_available_capacity - allocated_capacity)
    utilization_rate = (allocated_capacity / total_available_capacity * 100) if total_available_capacity > 0 else 0

    # Identify over/under allocated projects
    over_allocated = []
    under_allocated = []

    for project in projects:
        if project.status != 'active':
            continue

        if project.capacity_allocated > project.team_size * 1.1:
            over_allocated.append({
                'id': project.id,
                'name': project.name,
                'allocated': project.capacity_allocated,
                'team_size': project.team_size,
                'over_allocation_pct': ((project.capacity_allocated / project.team_size) - 1) * 100
            })
        elif project.capacity_allocated < project.team_size * 0.5:
            under_allocated.append({
                'id': project.id,
                'name': project.name,
                'allocated': project.capacity_allocated,
                'team_size': project.team_size,
                'under_allocation_pct': (1 - (project.capacity_allocated / project.team_size)) * 100
            })

    # Determine status
    if utilization_rate > 95:
        status = 'over_utilized'
    elif utilization_rate < 70:
        status = 'under_utilized'
    else:
        status = 'optimal'

    # Generate recommendations
    recommendations = []
    if status == 'over_utilized':
        recommendations.append(f"Portfolio sobre-utilizado ({utilization_rate:.1f}%). Considere realocar recursos ou adiar projetos de menor prioridade.")
    elif status == 'under_utilized':
        recommendations.append(f"Capacidade ociosa detectada ({available_capacity:.1f} FTE disponíveis). Oportunidade para acelerar projetos prioritários.")

    if over_allocated:
        recommendations.append(f"{len(over_allocated)} projetos sobre-alocados. Revise alocações e considere redistribuição.")

    if under_allocated:
        recommendations.append(f"{len(under_allocated)} projetos sub-utilizados. Avalie se podem ser acelerados ou se recursos podem ser realocados.")

    return CapacityAnalysis(
        total_capacity=total_available_capacity,
        allocated_capacity=allocated_capacity,
        available_capacity=available_capacity,
        utilization_rate=utilization_rate,
        over_allocated_projects=over_allocated,
        under_allocated_projects=under_allocated,
        status=status,
        recommendations=recommendations
    )


def create_prioritization_matrix(projects: List[Project]) -> PrioritizationMatrix:
    """
    Create value vs risk prioritization matrix.

    Args:
        projects: List of projects

    Returns:
        PrioritizationMatrix with projects categorized
    """
    high_value_low_risk = []
    high_value_high_risk = []
    low_value_low_risk = []
    low_value_high_risk = []

    # Risk thresholds
    risk_scores = {'low': 25, 'medium': 50, 'high': 75, 'critical': 90}

    for project in projects:
        if project.status not in ['active', 'on_hold']:
            continue

        project_dict = {
            'id': project.id,
            'name': project.name,
            'business_value': project.business_value,
            'risk_level': project.risk_level,
            'risk_score': risk_scores.get(project.risk_level, 50),
            'priority': project.priority,
            'status': project.status,
            'owner': project.owner
        }

        # Categorize
        is_high_value = project.business_value >= 60
        is_high_risk = project.risk_level in ['high', 'critical']

        if is_high_value and not is_high_risk:
            high_value_low_risk.append(project_dict)
        elif is_high_value and is_high_risk:
            high_value_high_risk.append(project_dict)
        elif not is_high_value and not is_high_risk:
            low_value_low_risk.append(project_dict)
        else:  # low value, high risk
            low_value_high_risk.append(project_dict)

    # Sort by business value within each quadrant
    high_value_low_risk.sort(key=lambda x: x['business_value'], reverse=True)
    high_value_high_risk.sort(key=lambda x: x['business_value'], reverse=True)
    low_value_low_risk.sort(key=lambda x: x['business_value'], reverse=True)
    low_value_high_risk.sort(key=lambda x: x['business_value'], reverse=True)

    return PrioritizationMatrix(
        high_value_low_risk=high_value_low_risk,
        high_value_high_risk=high_value_high_risk,
        low_value_low_risk=low_value_low_risk,
        low_value_high_risk=low_value_high_risk
    )


def generate_portfolio_alerts(
    projects: List[Project],
    health_scores: List[ProjectHealthScore],
    capacity_analysis: CapacityAnalysis
) -> List[Dict]:
    """
    Generate portfolio-level alerts based on analysis.

    Args:
        projects: List of projects
        health_scores: List of calculated health scores
        capacity_analysis: Capacity analysis results

    Returns:
        List of alert dictionaries
    """
    alerts = []

    # Critical health scores
    critical_projects = [hs for hs in health_scores if hs.health_status == 'critical']
    if critical_projects:
        alerts.append({
            'severity': 'critical',
            'type': 'health',
            'message': f'{len(critical_projects)} projeto(s) com health score crítico',
            'projects': [p.project_name for p in critical_projects],
            'action': 'Revisão urgente necessária'
        })

    # Over-utilization
    if capacity_analysis.status == 'over_utilized':
        alerts.append({
            'severity': 'high',
            'type': 'capacity',
            'message': f'Portfolio sobre-utilizado ({capacity_analysis.utilization_rate:.1f}%)',
            'action': 'Considere realocar recursos ou repriorizar projetos'
        })

    # Projects without recent forecasts
    stale_projects = [p for p in projects if p.status == 'active' and (not p.forecasts or len(p.forecasts) == 0)]
    if stale_projects:
        alerts.append({
            'severity': 'medium',
            'type': 'forecast',
            'message': f'{len(stale_projects)} projeto(s) ativo(s) sem previsões',
            'projects': [p.name for p in stale_projects],
            'action': 'Crie forecasts para melhor planejamento'
        })

    # High risk projects without mitigation
    high_risk_active = [p for p in projects if p.status == 'active' and p.risk_level in ['high', 'critical']]
    if high_risk_active:
        alerts.append({
            'severity': 'medium',
            'type': 'risk',
            'message': f'{len(high_risk_active)} projeto(s) de alto risco em andamento',
            'projects': [p.name for p in high_risk_active],
            'action': 'Garanta que planos de mitigação estejam em prática'
        })

    return alerts
