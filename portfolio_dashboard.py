"""
Portfolio Dashboard - Data aggregation and metrics for integrated dashboard
Provides comprehensive portfolio view with metrics, alerts, and visualizations
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class ProjectMetrics:
    """Metrics for a single project in the portfolio"""
    project_id: int
    project_name: str
    status: str

    # Duration estimates
    estimated_duration_p50: float
    estimated_duration_p85: float
    estimated_duration_p95: float

    # Progress
    items_completed: int
    items_remaining: int
    completion_pct: float

    # Cost of Delay
    cod_weekly: Optional[float] = None
    wsjf_score: Optional[float] = None

    # Dates
    start_date: Optional[str] = None
    target_end_date: Optional[str] = None
    projected_end_date: Optional[str] = None

    # Health indicators
    on_track: bool = True
    risk_level: str = "medium"  # low, medium, high, critical

    # Resource allocation
    capacity_allocated: float = 1.0  # FTE
    budget_allocated: Optional[float] = None

    # Priority
    priority: int = 3


@dataclass
class PortfolioAlert:
    """Alert/warning about portfolio or project status"""
    alert_id: str
    severity: str  # info, warning, critical
    category: str  # deadline, resource, risk, cost
    title: str
    message: str
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    action_required: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PortfolioHealth:
    """Overall health indicators for portfolio"""
    overall_score: float  # 0-100
    on_track_count: int
    at_risk_count: int
    critical_count: int

    # Resource health
    capacity_utilization: float  # 0-100%
    capacity_available: float
    capacity_allocated: float
    capacity_overallocated: bool

    # Budget health
    budget_utilization: Optional[float] = None  # 0-100%
    budget_available: Optional[float] = None
    budget_allocated: Optional[float] = None
    budget_exceeded: bool = False

    # Schedule health
    projects_on_schedule: int = 0
    projects_delayed: int = 0
    avg_schedule_variance: float = 0.0  # weeks


@dataclass
class TimelineEvent:
    """Event on the portfolio timeline"""
    event_id: str
    event_type: str  # project_start, project_end, milestone, deadline
    project_id: int
    project_name: str
    date: str
    description: str
    is_critical: bool = False


@dataclass
class ResourceAllocation:
    """Resource allocation across time periods"""
    period: str  # Week or month identifier
    total_capacity: float
    allocated_capacity: float
    utilization_pct: float
    projects: List[Dict]  # List of {project_id, project_name, capacity}


@dataclass
class PortfolioDashboard:
    """Complete dashboard data for a portfolio"""
    portfolio_id: int
    portfolio_name: str

    # Summary metrics
    total_projects: int
    active_projects: int
    completed_projects: int

    # Timeline
    earliest_start: Optional[str]
    latest_end: Optional[str]
    current_duration_weeks: float
    projected_duration_weeks: float

    # Cost of Delay
    total_cod: Optional[float] = None
    critical_path_projects: List[int] = field(default_factory=list)

    # Health
    health: Optional[PortfolioHealth] = None

    # Projects
    projects: List[ProjectMetrics] = field(default_factory=list)

    # Alerts
    alerts: List[PortfolioAlert] = field(default_factory=list)

    # Timeline events
    timeline_events: List[TimelineEvent] = field(default_factory=list)

    # Resource allocation over time
    resource_timeline: List[ResourceAllocation] = field(default_factory=list)

    # Aggregated metrics
    avg_completion_pct: float = 0.0
    total_items_completed: int = 0
    total_items_remaining: int = 0

    def to_dict(self):
        return {
            'portfolio_id': self.portfolio_id,
            'portfolio_name': self.portfolio_name,
            'summary': {
                'total_projects': self.total_projects,
                'active_projects': self.active_projects,
                'completed_projects': self.completed_projects,
                'avg_completion_pct': round(self.avg_completion_pct, 1),
                'total_items_completed': self.total_items_completed,
                'total_items_remaining': self.total_items_remaining
            },
            'timeline': {
                'earliest_start': self.earliest_start,
                'latest_end': self.latest_end,
                'current_duration_weeks': round(self.current_duration_weeks, 1),
                'projected_duration_weeks': round(self.projected_duration_weeks, 1)
            },
            'cost_of_delay': {
                'total_cod': round(self.total_cod, 2) if self.total_cod else None,
                'critical_path_projects': self.critical_path_projects
            },
            'health': {
                'overall_score': round(self.health.overall_score, 1) if self.health else 0,
                'on_track_count': self.health.on_track_count if self.health else 0,
                'at_risk_count': self.health.at_risk_count if self.health else 0,
                'critical_count': self.health.critical_count if self.health else 0,
                'capacity_utilization': round(self.health.capacity_utilization, 1) if self.health else 0,
                'capacity_overallocated': self.health.capacity_overallocated if self.health else False,
                'budget_utilization': round(self.health.budget_utilization, 1) if self.health and self.health.budget_utilization else None,
                'budget_exceeded': self.health.budget_exceeded if self.health else False,
                'projects_on_schedule': self.health.projects_on_schedule if self.health else 0,
                'projects_delayed': self.health.projects_delayed if self.health else 0
            },
            'projects': [
                {
                    'project_id': p.project_id,
                    'project_name': p.project_name,
                    'status': p.status,
                    'completion_pct': round(p.completion_pct, 1),
                    'estimated_duration_p85': round(p.estimated_duration_p85, 1),
                    'on_track': p.on_track,
                    'risk_level': p.risk_level,
                    'wsjf_score': round(p.wsjf_score, 2) if p.wsjf_score else None,
                    'priority': p.priority,
                    'capacity_allocated': p.capacity_allocated
                }
                for p in self.projects
            ],
            'alerts': [
                {
                    'alert_id': a.alert_id,
                    'severity': a.severity,
                    'category': a.category,
                    'title': a.title,
                    'message': a.message,
                    'project_id': a.project_id,
                    'project_name': a.project_name,
                    'action_required': a.action_required
                }
                for a in self.alerts
            ],
            'timeline_events': [
                {
                    'event_id': e.event_id,
                    'event_type': e.event_type,
                    'project_id': e.project_id,
                    'project_name': e.project_name,
                    'date': e.date,
                    'description': e.description,
                    'is_critical': e.is_critical
                }
                for e in self.timeline_events
            ],
            'resource_timeline': [
                {
                    'period': r.period,
                    'total_capacity': r.total_capacity,
                    'allocated_capacity': round(r.allocated_capacity, 1),
                    'utilization_pct': round(r.utilization_pct, 1),
                    'projects': r.projects
                }
                for r in self.resource_timeline
            ]
        }


def calculate_portfolio_health(projects: List[ProjectMetrics],
                               total_capacity: Optional[float] = None,
                               total_budget: Optional[float] = None) -> PortfolioHealth:
    """
    Calculate overall portfolio health indicators.

    Args:
        projects: List of project metrics
        total_capacity: Total available capacity (FTE)
        total_budget: Total available budget

    Returns:
        PortfolioHealth with aggregated metrics
    """
    if not projects:
        return PortfolioHealth(
            overall_score=0,
            on_track_count=0,
            at_risk_count=0,
            critical_count=0,
            capacity_utilization=0,
            capacity_available=total_capacity or 0,
            capacity_allocated=0,
            capacity_overallocated=False
        )

    # Count project statuses
    on_track_count = sum(1 for p in projects if p.on_track and p.status == 'active')
    at_risk_count = sum(1 for p in projects if not p.on_track and p.risk_level in ['medium', 'high'] and p.status == 'active')
    critical_count = sum(1 for p in projects if p.risk_level == 'critical' and p.status == 'active')

    # Calculate capacity metrics
    total_allocated_capacity = sum(p.capacity_allocated for p in projects if p.status == 'active')
    capacity_available = total_capacity or total_allocated_capacity
    capacity_utilization = (total_allocated_capacity / capacity_available * 100) if capacity_available > 0 else 0
    capacity_overallocated = total_allocated_capacity > capacity_available if capacity_available else False

    # Calculate budget metrics
    budget_utilization = None
    budget_available_calc = total_budget
    budget_allocated_calc = None
    budget_exceeded = False

    if total_budget:
        total_allocated_budget = sum(p.budget_allocated for p in projects if p.budget_allocated and p.status == 'active')
        budget_allocated_calc = total_allocated_budget
        budget_utilization = (total_allocated_budget / total_budget * 100) if total_budget > 0 else 0
        budget_exceeded = total_allocated_budget > total_budget

    # Calculate schedule health
    projects_on_schedule = sum(1 for p in projects if p.on_track and p.status == 'active')
    projects_delayed = sum(1 for p in projects if not p.on_track and p.status == 'active')

    # Overall health score (0-100)
    # Based on: projects on track, capacity utilization, budget utilization
    active_projects = [p for p in projects if p.status == 'active']
    if active_projects:
        on_track_pct = (on_track_count / len(active_projects)) * 100

        # Penalize over-allocation
        capacity_score = 100 if not capacity_overallocated else max(0, 100 - (capacity_utilization - 100))
        budget_score = 100 if not budget_exceeded else max(0, 100 - (budget_utilization - 100)) if budget_utilization else 100

        # Weight: 50% on-track, 25% capacity, 25% budget
        overall_score = (on_track_pct * 0.5) + (capacity_score * 0.25) + (budget_score * 0.25)
    else:
        overall_score = 100

    return PortfolioHealth(
        overall_score=overall_score,
        on_track_count=on_track_count,
        at_risk_count=at_risk_count,
        critical_count=critical_count,
        capacity_utilization=capacity_utilization,
        capacity_available=capacity_available,
        capacity_allocated=total_allocated_capacity,
        capacity_overallocated=capacity_overallocated,
        budget_utilization=budget_utilization,
        budget_available=budget_available_calc,
        budget_allocated=budget_allocated_calc,
        budget_exceeded=budget_exceeded,
        projects_on_schedule=projects_on_schedule,
        projects_delayed=projects_delayed
    )


def generate_intelligent_alerts(projects: List[ProjectMetrics],
                                health: PortfolioHealth,
                                total_capacity: Optional[float] = None,
                                total_budget: Optional[float] = None) -> List[PortfolioAlert]:
    """
    Generate intelligent alerts based on portfolio and project status.

    Args:
        projects: List of project metrics
        health: Portfolio health indicators
        total_capacity: Total available capacity
        total_budget: Total available budget

    Returns:
        List of alerts ordered by severity
    """
    alerts = []
    alert_counter = 0

    # Critical alerts
    if health.capacity_overallocated:
        alert_counter += 1
        alerts.append(PortfolioAlert(
            alert_id=f"alert_{alert_counter}",
            severity="critical",
            category="resource",
            title="Capacidade Sobre-Alocada",
            message=f"Capacidade alocada ({health.capacity_allocated:.1f} FTE) excede disponível ({health.capacity_available:.1f} FTE). "
                   f"Sobre-alocação: {health.capacity_allocated - health.capacity_available:.1f} FTE.",
            action_required=True
        ))

    if health.budget_exceeded:
        alert_counter += 1
        alerts.append(PortfolioAlert(
            alert_id=f"alert_{alert_counter}",
            severity="critical",
            category="cost",
            title="Orçamento Excedido",
            message=f"Orçamento alocado (R$ {health.budget_allocated:,.0f}) excede disponível (R$ {health.budget_available:,.0f}). "
                   f"Excesso: R$ {health.budget_allocated - health.budget_available:,.0f}.",
            action_required=True
        ))

    # Critical projects
    for project in projects:
        if project.risk_level == 'critical' and project.status == 'active':
            alert_counter += 1
            alerts.append(PortfolioAlert(
                alert_id=f"alert_{alert_counter}",
                severity="critical",
                category="risk",
                title=f"Projeto Crítico: {project.project_name}",
                message=f"Projeto em estado crítico. Ação imediata necessária.",
                project_id=project.project_id,
                project_name=project.project_name,
                action_required=True
            ))

    # Warning alerts
    if health.capacity_utilization > 90 and not health.capacity_overallocated:
        alert_counter += 1
        alerts.append(PortfolioAlert(
            alert_id=f"alert_{alert_counter}",
            severity="warning",
            category="resource",
            title="Capacidade Quase Esgotada",
            message=f"Capacidade em {health.capacity_utilization:.0f}%. Pouca margem para novos projetos.",
            action_required=False
        ))

    if health.budget_utilization and health.budget_utilization > 90 and not health.budget_exceeded:
        alert_counter += 1
        alerts.append(PortfolioAlert(
            alert_id=f"alert_{alert_counter}",
            severity="warning",
            category="cost",
            title="Orçamento Quase Esgotado",
            message=f"Orçamento em {health.budget_utilization:.0f}%. Pouca margem para novos investimentos.",
            action_required=False
        ))

    # Projects at risk
    for project in projects:
        if not project.on_track and project.status == 'active' and project.risk_level in ['medium', 'high']:
            alert_counter += 1
            alerts.append(PortfolioAlert(
                alert_id=f"alert_{alert_counter}",
                severity="warning",
                category="deadline",
                title=f"Projeto em Risco: {project.project_name}",
                message=f"Projeto não está no prazo. Risco: {project.risk_level}.",
                project_id=project.project_id,
                project_name=project.project_name,
                action_required=True
            ))

    # Info alerts
    if health.overall_score >= 80:
        alert_counter += 1
        alerts.append(PortfolioAlert(
            alert_id=f"alert_{alert_counter}",
            severity="info",
            category="risk",
            title="Portfolio Saudável",
            message=f"Score de saúde: {health.overall_score:.0f}/100. Portfolio em bom estado.",
            action_required=False
        ))

    # Sort by severity: critical > warning > info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: severity_order[a.severity])

    return alerts


def generate_timeline_events(projects: List[ProjectMetrics]) -> List[TimelineEvent]:
    """
    Generate timeline events from project data.

    Args:
        projects: List of project metrics

    Returns:
        List of timeline events sorted by date
    """
    events = []

    for project in projects:
        # Project start
        if project.start_date:
            events.append(TimelineEvent(
                event_id=f"start_{project.project_id}",
                event_type="project_start",
                project_id=project.project_id,
                project_name=project.project_name,
                date=project.start_date,
                description=f"Início: {project.project_name}",
                is_critical=project.priority == 1
            ))

        # Target end
        if project.target_end_date:
            events.append(TimelineEvent(
                event_id=f"target_{project.project_id}",
                event_type="deadline",
                project_id=project.project_id,
                project_name=project.project_name,
                date=project.target_end_date,
                description=f"Prazo: {project.project_name}",
                is_critical=project.priority == 1
            ))

        # Projected end
        if project.projected_end_date:
            events.append(TimelineEvent(
                event_id=f"projected_{project.project_id}",
                event_type="project_end",
                project_id=project.project_id,
                project_name=project.project_name,
                date=project.projected_end_date,
                description=f"Conclusão prevista: {project.project_name}",
                is_critical=not project.on_track
            ))

    # Sort by date
    events.sort(key=lambda e: e.date if e.date else "9999-12-31")

    return events


def calculate_resource_timeline(projects: List[ProjectMetrics],
                                total_capacity: float,
                                weeks: int = 12) -> List[ResourceAllocation]:
    """
    Calculate resource allocation over time.

    Args:
        projects: List of project metrics
        total_capacity: Total available capacity
        weeks: Number of weeks to project

    Returns:
        List of resource allocations per week
    """
    timeline = []

    for week in range(weeks):
        # Simple model: assume all active projects use their allocated capacity
        active_projects = [p for p in projects if p.status == 'active']

        week_allocation = sum(p.capacity_allocated for p in active_projects)
        utilization = (week_allocation / total_capacity * 100) if total_capacity > 0 else 0

        projects_detail = [
            {
                'project_id': p.project_id,
                'project_name': p.project_name,
                'capacity': p.capacity_allocated
            }
            for p in active_projects
        ]

        timeline.append(ResourceAllocation(
            period=f"Week {week + 1}",
            total_capacity=total_capacity,
            allocated_capacity=week_allocation,
            utilization_pct=utilization,
            projects=projects_detail
        ))

    return timeline
