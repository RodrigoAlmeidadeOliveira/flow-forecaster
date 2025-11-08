"""
Portfolio Risk Manager
Handles risk aggregation, rollup, and analysis for portfolios
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass
class RiskMetrics:
    """Aggregated risk metrics for a portfolio"""
    total_risks: int
    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    very_low_risks: int

    active_risks: int
    mitigated_risks: int
    accepted_risks: int
    occurred_risks: int
    closed_risks: int

    total_risk_score: float
    average_risk_score: float
    weighted_risk_score: float  # Weighted by probability

    total_potential_cost: float
    total_mitigation_cost: float
    expected_monetary_value: float  # EMV = sum(probability * impact_cost)

    # By category
    risks_by_category: Dict[str, int]
    high_risk_categories: List[str]

    # By project
    high_risk_projects: List[Dict[str, Any]]
    projects_without_risks: List[str]


@dataclass
class RiskHeatmapData:
    """Data for probability x impact heatmap"""
    matrix: List[List[int]]  # 5x5 matrix with risk counts
    risks_by_cell: Dict[Tuple[int, int], List[Dict[str, Any]]]  # (prob, impact) -> list of risks
    total_in_red_zone: int  # Critical risks (score >= 15)
    total_in_yellow_zone: int  # Medium/High risks (score 6-14)
    total_in_green_zone: int  # Low risks (score <= 5)


class PortfolioRiskManager:
    """Manages portfolio-level risk aggregation and analysis"""

    def __init__(self):
        pass

    def calculate_risk_metrics(self, risks: List[Dict[str, Any]]) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics for a portfolio

        Args:
            risks: List of risk dictionaries with all risk data

        Returns:
            RiskMetrics object with aggregated metrics
        """
        if not risks:
            return self._empty_metrics()

        # Count by risk level
        critical = sum(1 for r in risks if r.get('risk_level') == 'critical')
        high = sum(1 for r in risks if r.get('risk_level') == 'high')
        medium = sum(1 for r in risks if r.get('risk_level') == 'medium')
        low = sum(1 for r in risks if r.get('risk_level') == 'low')
        very_low = sum(1 for r in risks if r.get('risk_level') == 'very_low')

        # Count by status
        active = sum(1 for r in risks if r.get('status') in ['identified', 'assessed'])
        mitigated = sum(1 for r in risks if r.get('status') == 'mitigated')
        accepted = sum(1 for r in risks if r.get('status') == 'accepted')
        occurred = sum(1 for r in risks if r.get('status') == 'occurred')
        closed = sum(1 for r in risks if r.get('status') == 'closed')

        # Risk scores
        risk_scores = [r.get('risk_score', 0) for r in risks if r.get('risk_score')]
        total_score = sum(risk_scores)
        avg_score = total_score / len(risk_scores) if risk_scores else 0

        # Weighted risk score (weighted by probability)
        weighted_score = sum(
            r.get('risk_score', 0) * r.get('probability', 1) / 5.0
            for r in risks if r.get('risk_score')
        )

        # Cost calculations
        total_potential_cost = sum(
            r.get('estimated_cost_if_occurs', 0) or 0
            for r in risks
        )

        total_mitigation_cost = sum(
            r.get('mitigation_cost', 0) or 0
            for r in risks
        )

        # Expected Monetary Value (EMV) = sum(probability * impact_cost)
        emv = sum(
            (r.get('probability', 3) / 5.0) * (r.get('estimated_cost_if_occurs', 0) or 0)
            for r in risks
        )

        # By category
        risks_by_category = {}
        for r in risks:
            category = r.get('risk_category', 'general')
            risks_by_category[category] = risks_by_category.get(category, 0) + 1

        # High risk categories (categories with critical/high risks)
        high_risk_categories = list(set(
            r.get('risk_category', 'general')
            for r in risks
            if r.get('risk_level') in ['critical', 'high']
        ))

        # By project
        project_risk_counts = {}
        for r in risks:
            project_name = r.get('project_name')
            if project_name:
                if project_name not in project_risk_counts:
                    project_risk_counts[project_name] = {
                        'name': project_name,
                        'project_id': r.get('project_id'),
                        'total_risks': 0,
                        'critical_risks': 0,
                        'high_risks': 0
                    }
                project_risk_counts[project_name]['total_risks'] += 1
                if r.get('risk_level') == 'critical':
                    project_risk_counts[project_name]['critical_risks'] += 1
                elif r.get('risk_level') == 'high':
                    project_risk_counts[project_name]['high_risks'] += 1

        # High risk projects (projects with critical or multiple high risks)
        high_risk_projects = [
            p for p in project_risk_counts.values()
            if p['critical_risks'] > 0 or p['high_risks'] >= 2
        ]
        high_risk_projects.sort(key=lambda p: (p['critical_risks'], p['high_risks']), reverse=True)

        return RiskMetrics(
            total_risks=len(risks),
            critical_risks=critical,
            high_risks=high,
            medium_risks=medium,
            low_risks=low,
            very_low_risks=very_low,
            active_risks=active,
            mitigated_risks=mitigated,
            accepted_risks=accepted,
            occurred_risks=occurred,
            closed_risks=closed,
            total_risk_score=total_score,
            average_risk_score=avg_score,
            weighted_risk_score=weighted_score,
            total_potential_cost=total_potential_cost,
            total_mitigation_cost=total_mitigation_cost,
            expected_monetary_value=emv,
            risks_by_category=risks_by_category,
            high_risk_categories=high_risk_categories,
            high_risk_projects=high_risk_projects,
            projects_without_risks=[]  # Will be populated separately
        )

    def generate_heatmap_data(self, risks: List[Dict[str, Any]]) -> RiskHeatmapData:
        """
        Generate data for probability x impact heatmap

        Args:
            risks: List of risk dictionaries

        Returns:
            RiskHeatmapData object with matrix and zone counts
        """
        # Initialize 5x5 matrix (probability x impact)
        matrix = [[0 for _ in range(5)] for _ in range(5)]
        risks_by_cell = {}

        for risk in risks:
            prob = risk.get('probability', 3) - 1  # Convert 1-5 to 0-4 index
            impact = risk.get('impact', 3) - 1

            # Ensure within bounds
            prob = max(0, min(4, prob))
            impact = max(0, min(4, impact))

            matrix[prob][impact] += 1

            cell_key = (prob + 1, impact + 1)  # Store as 1-5 for readability
            if cell_key not in risks_by_cell:
                risks_by_cell[cell_key] = []
            risks_by_cell[cell_key].append(risk)

        # Count risks by zone
        red_zone = 0  # Critical/High (score >= 15)
        yellow_zone = 0  # Medium (score 10-14)
        green_zone = 0  # Low (score <= 9)

        for risk in risks:
            score = risk.get('risk_score', 0)
            if score >= 15:
                red_zone += 1
            elif score >= 10:
                yellow_zone += 1
            else:
                green_zone += 1

        return RiskHeatmapData(
            matrix=matrix,
            risks_by_cell=risks_by_cell,
            total_in_red_zone=red_zone,
            total_in_yellow_zone=yellow_zone,
            total_in_green_zone=green_zone
        )

    def rollup_project_risks(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rollup risks from individual projects to portfolio level

        This function analyzes project-level risk indicators and creates
        portfolio-level risks based on patterns.

        Args:
            projects: List of project dictionaries with risk indicators

        Returns:
            List of suggested portfolio-level risks
        """
        suggested_risks = []

        # Check for high-risk projects
        high_risk_projects = [p for p in projects if p.get('risk_level') in ['high', 'critical']]
        if len(high_risk_projects) > len(projects) * 0.3:  # >30% are high risk
            suggested_risks.append({
                'risk_title': 'Excessive High-Risk Projects',
                'risk_description': f'{len(high_risk_projects)} out of {len(projects)} projects are marked as high/critical risk',
                'risk_category': 'strategic',
                'probability': 4,
                'impact': 5,
                'suggested': True,
                'affected_projects': [p.get('name') for p in high_risk_projects]
            })

        # Check for capacity overallocation
        total_capacity_allocated = sum(p.get('capacity_allocated', 0) for p in projects)
        if total_capacity_allocated > 0:  # If we have capacity data
            suggested_risks.append({
                'risk_title': 'Resource Capacity Risk',
                'risk_description': f'Total capacity allocated: {total_capacity_allocated:.1f} FTE across all projects',
                'risk_category': 'resource',
                'probability': 3,
                'impact': 4,
                'suggested': True
            })

        # Check for projects with no end dates
        projects_no_deadline = [p for p in projects if not p.get('target_end_date')]
        if len(projects_no_deadline) > len(projects) * 0.4:  # >40% have no deadline
            suggested_risks.append({
                'risk_title': 'Lack of Project Deadlines',
                'risk_description': f'{len(projects_no_deadline)} projects have no target end date, making scheduling difficult',
                'risk_category': 'schedule',
                'probability': 4,
                'impact': 3,
                'suggested': True,
                'affected_projects': [p.get('name') for p in projects_no_deadline]
            })

        # Check for projects with low business value
        low_value_projects = [p for p in projects if p.get('business_value', 50) < 30]
        if len(low_value_projects) > len(projects) * 0.25:  # >25% low value
            suggested_risks.append({
                'risk_title': 'Portfolio Value Dilution',
                'risk_description': f'{len(low_value_projects)} projects have low business value (<30), potentially diluting portfolio ROI',
                'risk_category': 'strategic',
                'probability': 3,
                'impact': 3,
                'suggested': True,
                'affected_projects': [p.get('name') for p in low_value_projects]
            })

        return suggested_risks

    def generate_risk_alerts(self, metrics: RiskMetrics) -> List[Dict[str, Any]]:
        """
        Generate intelligent alerts based on risk metrics

        Args:
            metrics: RiskMetrics object

        Returns:
            List of alert dictionaries
        """
        alerts = []

        # Critical risk alert
        if metrics.critical_risks > 0:
            alerts.append({
                'type': 'critical',
                'severity': 'critical',
                'title': f'{metrics.critical_risks} Critical Risk(s) Identified',
                'message': f'Immediate attention required for {metrics.critical_risks} critical risk(s) with score >= 20',
                'action': 'Review critical risks and implement mitigation plans immediately',
                'icon': 'exclamation-triangle'
            })

        # High risk projects alert
        if len(metrics.high_risk_projects) > 0:
            alerts.append({
                'type': 'warning',
                'severity': 'high',
                'title': f'{len(metrics.high_risk_projects)} High-Risk Project(s)',
                'message': f'Projects with multiple high/critical risks: {", ".join([p["name"] for p in metrics.high_risk_projects[:3]])}',
                'action': 'Review project risk mitigation strategies',
                'icon': 'exclamation-circle'
            })

        # High EMV alert
        if metrics.expected_monetary_value > 100000:  # > R$ 100k
            alerts.append({
                'type': 'warning',
                'severity': 'high',
                'title': 'High Expected Risk Cost',
                'message': f'Expected Monetary Value (EMV) of risks: R$ {metrics.expected_monetary_value:,.0f}',
                'action': 'Consider increasing mitigation budget or accepting certain risks',
                'icon': 'dollar-sign'
            })

        # Many active risks
        if metrics.active_risks > 10:
            alerts.append({
                'type': 'info',
                'severity': 'medium',
                'title': 'Many Active Risks',
                'message': f'{metrics.active_risks} risks are in identified/assessed state',
                'action': 'Prioritize risk mitigation efforts for highest-impact risks',
                'icon': 'tasks'
            })

        # Category concentration
        if metrics.high_risk_categories:
            alerts.append({
                'type': 'info',
                'severity': 'medium',
                'title': 'Risk Category Concentration',
                'message': f'High risks concentrated in: {", ".join(metrics.high_risk_categories)}',
                'action': 'Consider specialized expertise or focus in these areas',
                'icon': 'chart-pie'
            })

        return alerts

    def _empty_metrics(self) -> RiskMetrics:
        """Return empty metrics when no risks exist"""
        return RiskMetrics(
            total_risks=0,
            critical_risks=0,
            high_risks=0,
            medium_risks=0,
            low_risks=0,
            very_low_risks=0,
            active_risks=0,
            mitigated_risks=0,
            accepted_risks=0,
            occurred_risks=0,
            closed_risks=0,
            total_risk_score=0,
            average_risk_score=0,
            weighted_risk_score=0,
            total_potential_cost=0,
            total_mitigation_cost=0,
            expected_monetary_value=0,
            risks_by_category={},
            high_risk_categories=[],
            high_risk_projects=[],
            projects_without_risks=[]
        )


def analyze_portfolio_risks(risks: List[Dict[str, Any]],
                            projects: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze all portfolio risks

    Args:
        risks: List of risk dictionaries
        projects: Optional list of project dictionaries for rollup analysis

    Returns:
        Complete risk analysis dictionary
    """
    manager = PortfolioRiskManager()

    # Calculate metrics
    metrics = manager.calculate_risk_metrics(risks)

    # Generate heatmap
    heatmap = manager.generate_heatmap_data(risks)

    # Generate alerts
    alerts = manager.generate_risk_alerts(metrics)

    # Rollup suggestions (if projects provided)
    suggested_risks = []
    if projects:
        suggested_risks = manager.rollup_project_risks(projects)

    return {
        'metrics': {
            'total_risks': metrics.total_risks,
            'by_level': {
                'critical': metrics.critical_risks,
                'high': metrics.high_risks,
                'medium': metrics.medium_risks,
                'low': metrics.low_risks,
                'very_low': metrics.very_low_risks
            },
            'by_status': {
                'active': metrics.active_risks,
                'mitigated': metrics.mitigated_risks,
                'accepted': metrics.accepted_risks,
                'occurred': metrics.occurred_risks,
                'closed': metrics.closed_risks
            },
            'scores': {
                'total': metrics.total_risk_score,
                'average': metrics.average_risk_score,
                'weighted': metrics.weighted_risk_score
            },
            'costs': {
                'total_potential': metrics.total_potential_cost,
                'total_mitigation': metrics.total_mitigation_cost,
                'expected_monetary_value': metrics.expected_monetary_value
            },
            'by_category': metrics.risks_by_category,
            'high_risk_categories': metrics.high_risk_categories,
            'high_risk_projects': metrics.high_risk_projects
        },
        'heatmap': {
            'matrix': heatmap.matrix,
            'risks_by_cell': {
                f'{k[0]},{k[1]}': v for k, v in heatmap.risks_by_cell.items()
            },
            'zones': {
                'red': heatmap.total_in_red_zone,
                'yellow': heatmap.total_in_yellow_zone,
                'green': heatmap.total_in_green_zone
            }
        },
        'alerts': alerts,
        'suggested_risks': suggested_risks
    }
