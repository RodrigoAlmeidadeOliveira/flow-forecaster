"""
Portfolio Optimizer
Uses linear programming to optimize project selection and resource allocation
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

try:
    from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, value
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("Warning: PuLP not installed. Install with: pip install pulp")


@dataclass
class OptimizationConstraints:
    """Constraints for portfolio optimization"""
    max_budget: float
    max_capacity: float  # FTE
    min_business_value: Optional[float] = None
    max_risk_score: Optional[float] = None
    mandatory_projects: List[int] = None
    excluded_projects: List[int] = None
    max_duration_weeks: Optional[float] = None

    def __post_init__(self):
        if self.mandatory_projects is None:
            self.mandatory_projects = []
        if self.excluded_projects is None:
            self.excluded_projects = []


@dataclass
class OptimizationResult:
    """Result of portfolio optimization"""
    selected_projects: List[int]
    total_value: float
    total_cost: float
    total_capacity: float
    total_duration: float
    total_risk_score: float
    projects_included: int
    projects_excluded: int
    optimization_status: str
    objective_value: float
    constraints_satisfied: bool
    recommendations: List[str]


@dataclass
class Scenario:
    """What-if scenario definition"""
    scenario_name: str
    scenario_description: str
    constraints: OptimizationConstraints
    result: Optional[OptimizationResult] = None


class PortfolioOptimizer:
    """
    Portfolio optimization engine using linear programming

    Solves the project selection problem:
    - Maximize: Total business value
    - Subject to: Budget, capacity, risk constraints
    - Variables: Binary (0/1) for each project
    """

    def __init__(self):
        if not PULP_AVAILABLE:
            raise ImportError("PuLP library is required for optimization. Install with: pip install pulp")

    def optimize_portfolio(
        self,
        projects: List[Dict[str, Any]],
        constraints: OptimizationConstraints,
        objective: str = 'maximize_value'
    ) -> OptimizationResult:
        """
        Optimize portfolio using linear programming

        Args:
            projects: List of project dictionaries with metrics
            constraints: Optimization constraints
            objective: Optimization objective
                - 'maximize_value': Maximize total business value
                - 'maximize_wsjf': Maximize total WSJF score
                - 'minimize_risk': Minimize total risk
                - 'maximize_value_risk_adjusted': Maximize value/risk ratio

        Returns:
            OptimizationResult with selected projects and metrics
        """
        # Create LP problem
        prob = LpProblem("Portfolio_Optimization", LpMaximize)

        # Create binary variables for each project (0 = not selected, 1 = selected)
        project_vars = {}
        for project in projects:
            proj_id = project['id']
            project_vars[proj_id] = LpVariable(f"project_{proj_id}", cat='Binary')

        # Define objective function
        if objective == 'maximize_value':
            # Maximize total business value
            prob += lpSum([
                project_vars[p['id']] * p.get('business_value', 0)
                for p in projects
            ])
        elif objective == 'maximize_wsjf':
            # Maximize total WSJF score
            prob += lpSum([
                project_vars[p['id']] * p.get('wsjf_score', 0)
                for p in projects if p.get('wsjf_score')
            ])
        elif objective == 'minimize_risk':
            # Minimize total risk (inverse)
            risk_scores = []
            for p in projects:
                risk_val = self._get_risk_numeric(p.get('risk_level', 'medium'))
                risk_scores.append(project_vars[p['id']] * -risk_val)
            prob += lpSum(risk_scores)
        elif objective == 'maximize_value_risk_adjusted':
            # Maximize value/risk ratio
            prob += lpSum([
                project_vars[p['id']] * (
                    p.get('business_value', 0) / max(self._get_risk_numeric(p.get('risk_level', 'medium')), 1)
                )
                for p in projects
            ])

        # Add constraints

        # 1. Budget constraint
        if constraints.max_budget:
            prob += lpSum([
                project_vars[p['id']] * p.get('budget_allocated', 0)
                for p in projects
            ]) <= constraints.max_budget, "Budget_Constraint"

        # 2. Capacity constraint
        if constraints.max_capacity:
            prob += lpSum([
                project_vars[p['id']] * p.get('capacity_allocated', 0)
                for p in projects
            ]) <= constraints.max_capacity, "Capacity_Constraint"

        # 3. Minimum business value constraint
        if constraints.min_business_value:
            prob += lpSum([
                project_vars[p['id']] * p.get('business_value', 0)
                for p in projects
            ]) >= constraints.min_business_value, "Min_Business_Value"

        # 4. Maximum risk constraint
        if constraints.max_risk_score:
            prob += lpSum([
                project_vars[p['id']] * self._get_risk_numeric(p.get('risk_level', 'medium'))
                for p in projects
            ]) <= constraints.max_risk_score, "Max_Risk_Score"

        # 5. Mandatory projects
        for proj_id in constraints.mandatory_projects:
            if proj_id in project_vars:
                prob += project_vars[proj_id] == 1, f"Mandatory_Project_{proj_id}"

        # 6. Excluded projects
        for proj_id in constraints.excluded_projects:
            if proj_id in project_vars:
                prob += project_vars[proj_id] == 0, f"Excluded_Project_{proj_id}"

        # Solve the problem
        prob.solve()

        # Extract results
        selected_projects = []
        total_value = 0
        total_cost = 0
        total_capacity = 0
        total_duration = 0
        total_risk = 0

        for project in projects:
            proj_id = project['id']
            if proj_id in project_vars and value(project_vars[proj_id]) == 1:
                selected_projects.append(proj_id)
                total_value += project.get('business_value', 0)
                total_cost += project.get('budget_allocated', 0)
                total_capacity += project.get('capacity_allocated', 0)
                total_duration += project.get('estimated_duration_p85', 0)
                total_risk += self._get_risk_numeric(project.get('risk_level', 'medium'))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            projects,
            selected_projects,
            constraints,
            total_cost,
            total_capacity
        )

        return OptimizationResult(
            selected_projects=selected_projects,
            total_value=total_value,
            total_cost=total_cost,
            total_capacity=total_capacity,
            total_duration=total_duration,
            total_risk_score=total_risk,
            projects_included=len(selected_projects),
            projects_excluded=len(projects) - len(selected_projects),
            optimization_status=LpStatus[prob.status],
            objective_value=value(prob.objective),
            constraints_satisfied=prob.status == 1,  # 1 = Optimal
            recommendations=recommendations
        )

    def compare_scenarios(
        self,
        projects: List[Dict[str, Any]],
        scenarios: List[Scenario]
    ) -> Dict[str, Any]:
        """
        Compare multiple what-if scenarios

        Args:
            projects: List of project dictionaries
            scenarios: List of scenario definitions

        Returns:
            Comparison data with recommendations
        """
        results = []

        for scenario in scenarios:
            result = self.optimize_portfolio(
                projects,
                scenario.constraints,
                objective='maximize_value'
            )
            scenario.result = result
            results.append({
                'scenario_name': scenario.scenario_name,
                'description': scenario.scenario_description,
                'projects_selected': result.projects_included,
                'total_value': result.total_value,
                'total_cost': result.total_cost,
                'total_capacity': result.total_capacity,
                'optimization_status': result.optimization_status,
                'selected_project_ids': result.selected_projects
            })

        # Find best scenario
        valid_results = [r for r in results if r['optimization_status'] == 'Optimal']
        if valid_results:
            best_scenario = max(valid_results, key=lambda x: x['total_value'])
        else:
            best_scenario = None

        return {
            'scenarios': results,
            'best_scenario': best_scenario['scenario_name'] if best_scenario else None,
            'comparison': self._generate_scenario_comparison(results)
        }

    def generate_pareto_frontier(
        self,
        projects: List[Dict[str, Any]],
        constraints: OptimizationConstraints,
        axis_x: str = 'cost',
        axis_y: str = 'value',
        points: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate Pareto frontier for trade-off analysis

        Args:
            projects: List of project dictionaries
            constraints: Base constraints
            axis_x: X-axis metric (cost, risk, duration)
            axis_y: Y-axis metric (value, wsjf)
            points: Number of points to generate

        Returns:
            List of Pareto-optimal points
        """
        pareto_points = []

        # Generate points by varying constraints
        if axis_x == 'cost':
            min_budget = min(p.get('budget_allocated', 0) for p in projects)
            max_budget = constraints.max_budget or sum(p.get('budget_allocated', 0) for p in projects)

            for i in range(points):
                budget = min_budget + (max_budget - min_budget) * i / (points - 1)
                temp_constraints = OptimizationConstraints(
                    max_budget=budget,
                    max_capacity=constraints.max_capacity,
                    mandatory_projects=constraints.mandatory_projects,
                    excluded_projects=constraints.excluded_projects
                )

                result = self.optimize_portfolio(projects, temp_constraints)
                if result.optimization_status == 'Optimal':
                    pareto_points.append({
                        'x': result.total_cost,
                        'y': result.total_value,
                        'projects_count': result.projects_included,
                        'budget_limit': budget
                    })

        return pareto_points

    def _get_risk_numeric(self, risk_level: str) -> int:
        """Convert risk level to numeric value"""
        risk_map = {
            'very_low': 1,
            'low': 2,
            'medium': 3,
            'high': 4,
            'critical': 5
        }
        return risk_map.get(risk_level, 3)

    def _generate_recommendations(
        self,
        projects: List[Dict[str, Any]],
        selected_ids: List[int],
        constraints: OptimizationConstraints,
        total_cost: float,
        total_capacity: float
    ) -> List[str]:
        """Generate recommendations based on optimization results"""
        recommendations = []

        # Budget utilization
        if constraints.max_budget:
            budget_used_pct = (total_cost / constraints.max_budget) * 100
            if budget_used_pct > 95:
                recommendations.append(f"Budget {budget_used_pct:.1f}% utilized - Consider increasing budget for more projects")
            elif budget_used_pct < 50:
                recommendations.append(f"Only {budget_used_pct:.1f}% budget utilized - Room to add more projects")

        # Capacity utilization
        if constraints.max_capacity:
            capacity_used_pct = (total_capacity / constraints.max_capacity) * 100
            if capacity_used_pct > 95:
                recommendations.append(f"Capacity {capacity_used_pct:.1f}% utilized - Team is at full capacity")
            elif capacity_used_pct < 50:
                recommendations.append(f"Only {capacity_used_pct:.1f}% capacity utilized - Can take on more work")

        # Excluded high-value projects
        excluded_projects = [p for p in projects if p['id'] not in selected_ids]
        high_value_excluded = [
            p for p in excluded_projects
            if p.get('business_value', 0) > 70
        ]
        if high_value_excluded:
            recommendations.append(
                f"{len(high_value_excluded)} high-value project(s) excluded due to constraints. "
                f"Consider: {', '.join([p['name'] for p in high_value_excluded[:3]])}"
            )

        # Risk concentration
        selected_projects = [p for p in projects if p['id'] in selected_ids]
        high_risk_count = sum(
            1 for p in selected_projects
            if p.get('risk_level') in ['high', 'critical']
        )
        if high_risk_count > len(selected_projects) * 0.3:
            recommendations.append(
                f"{high_risk_count} high-risk projects in optimized portfolio. "
                f"Consider mitigation strategies."
            )

        return recommendations

    def _generate_scenario_comparison(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison insights between scenarios"""
        if not results:
            return {}

        # Find differences in project selection
        all_selected = set()
        for r in results:
            all_selected.update(r['selected_project_ids'])

        # Projects that vary across scenarios
        varying_projects = []
        for proj_id in all_selected:
            scenarios_with_project = [
                r['scenario_name'] for r in results
                if proj_id in r['selected_project_ids']
            ]
            if len(scenarios_with_project) < len(results):
                varying_projects.append({
                    'project_id': proj_id,
                    'in_scenarios': scenarios_with_project,
                    'frequency': len(scenarios_with_project)
                })

        return {
            'total_unique_projects': len(all_selected),
            'varying_projects': varying_projects,
            'value_range': {
                'min': min(r['total_value'] for r in results),
                'max': max(r['total_value'] for r in results),
                'spread': max(r['total_value'] for r in results) - min(r['total_value'] for r in results)
            }
        }


def optimize_portfolio_simple(
    projects: List[Dict[str, Any]],
    max_budget: float,
    max_capacity: float
) -> Dict[str, Any]:
    """
    Simplified portfolio optimization interface

    Args:
        projects: List of project dictionaries
        max_budget: Maximum budget in currency
        max_capacity: Maximum FTE capacity

    Returns:
        Optimization result dictionary
    """
    if not PULP_AVAILABLE:
        return {
            'error': 'PuLP library not installed',
            'message': 'Install with: pip install pulp'
        }

    optimizer = PortfolioOptimizer()
    constraints = OptimizationConstraints(
        max_budget=max_budget,
        max_capacity=max_capacity
    )

    result = optimizer.optimize_portfolio(projects, constraints)

    return {
        'selected_projects': result.selected_projects,
        'total_value': result.total_value,
        'total_cost': result.total_cost,
        'total_capacity': result.total_capacity,
        'projects_included': result.projects_included,
        'projects_excluded': result.projects_excluded,
        'status': result.optimization_status,
        'recommendations': result.recommendations
    }
