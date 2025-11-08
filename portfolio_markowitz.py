"""
Markowitz Efficient Frontier utilities for Flow Forecaster portfolios.

This module derives expected returns and risk metrics for project portfolios,
simulates thousands of random allocations via Monte Carlo, and extracts the
efficient frontier alongside Sharpe-optimal allocations.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

import numpy as np

# Default mapping between qualitative risk level and volatility (weekly std dev)
RISK_LEVEL_SIGMA = {
    'low': 0.08,
    'medium': 0.15,
    'high': 0.25,
    'critical': 0.35
}

RISK_LEVEL_RANK = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4
}

DEFAULT_RISK_FREE_RATE = 0.02  # 2% annualized placeholder


class PortfolioMarkowitzAnalyzer:
    """Compute Markowitz metrics, Monte Carlo simulations, and efficient frontiers."""

    def __init__(self, projects: List[Dict[str, Any]], risk_free_rate: float = DEFAULT_RISK_FREE_RATE):
        if len(projects) < 2:
            raise ValueError("At least two projects are required to compute an efficient frontier.")

        self.projects = projects
        self.risk_free_rate = float(risk_free_rate)
        self.project_count = len(projects)
        self.expected_returns = np.array([
            max(float(project.get('expected_return', 0.01)), 0.0001)
            for project in projects
        ], dtype=float)
        self.volatility = np.array([
            max(float(project.get('volatility', 0.05)), 0.01)
            for project in projects
        ], dtype=float)
        self.covariance = self._build_covariance_matrix()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_analysis(
        self,
        current_weights: Optional[np.ndarray] = None,
        num_samples: int = 4000,
        chart_samples: int = 400,
        frontier_points: int = 60
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo sampling, extract the efficient frontier, and evaluate the
        current allocation.
        """
        weights, returns, risks, sharpes = self._simulate_portfolios(num_samples)

        cloud_points = self._sample_points_for_chart(returns, risks, sharpes, chart_samples)
        best_idx = int(np.argmax(sharpes))
        best_portfolio = self._portfolio_summary(weights[best_idx], returns[best_idx], risks[best_idx])
        frontier = self._build_efficient_frontier(weights, returns, risks, frontier_points)

        current_summary = None
        if current_weights is not None and len(current_weights) == self.project_count:
            current_summary = self._portfolio_summary(current_weights)

        return {
            'risk_free_rate': self.risk_free_rate,
            'monte_carlo': {
                'points': cloud_points,
                'sample_size': num_samples
            },
            'efficient_frontier': frontier,
            'best_portfolio': best_portfolio,
            'current_portfolio': current_summary
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_covariance_matrix(self) -> np.ndarray:
        size = self.project_count
        covariance = np.zeros((size, size), dtype=float)

        for i in range(size):
            for j in range(size):
                if i == j:
                    covariance[i, j] = self.volatility[i] ** 2
                    continue
                corr = self._estimate_correlation(self.projects[i], self.projects[j])
                covariance[i, j] = corr * self.volatility[i] * self.volatility[j]

        # Small jitter to ensure positive definiteness numerically
        covariance += np.eye(size) * 1e-6
        return covariance

    def _estimate_correlation(self, proj_a: Dict[str, Any], proj_b: Dict[str, Any]) -> float:
        """Heuristic correlation based on qualitative risk proximity."""
        risk_a = RISK_LEVEL_RANK.get(proj_a.get('risk_level', 'medium'), 2)
        risk_b = RISK_LEVEL_RANK.get(proj_b.get('risk_level', 'medium'), 2)
        diff = abs(risk_a - risk_b)

        # Base correlation decreases as risk profiles diverge
        correlation = 0.55 - (diff * 0.12)
        correlation = max(0.1, min(0.65, correlation))
        return correlation

    def _simulate_portfolios(self, num_samples: int):
        """Generate random portfolio weights via Dirichlet sampling."""
        weights = np.random.dirichlet(np.ones(self.project_count), size=num_samples)
        returns = weights @ self.expected_returns
        risks = np.sqrt(np.einsum('ij,jk,ik->i', weights, self.covariance, weights))
        sharpes = (returns - self.risk_free_rate) / np.maximum(risks, 1e-6)
        return weights, returns, risks, sharpes

    def _build_efficient_frontier(
        self,
        weights: np.ndarray,
        returns: np.ndarray,
        risks: np.ndarray,
        max_points: int
    ) -> List[Dict[str, Any]]:
        """Extract the efficient frontier by scanning sorted portfolios."""
        sorted_indices = np.argsort(risks)
        efficient: List[Dict[str, Any]] = []
        best_return = -np.inf

        for idx in sorted_indices:
            ret = returns[idx]
            risk = risks[idx]
            if ret >= best_return + 1e-4:
                best_return = ret
                efficient.append(self._portfolio_summary(weights[idx], ret, risk))
                if len(efficient) >= max_points:
                    break

        return efficient

    def _sample_points_for_chart(
        self,
        returns: np.ndarray,
        risks: np.ndarray,
        sharpes: np.ndarray,
        sample_size: int
    ) -> List[Dict[str, float]]:
        """Down-sample Monte Carlo portfolios for visualization."""
        total = len(returns)
        if total == 0:
            return []

        size = min(sample_size, total)
        indices = np.random.choice(total, size=size, replace=False) if size < total else range(total)

        return [
            {
                'expected_return': float(returns[i]),
                'risk': float(risks[i]),
                'sharpe': float(sharpes[i])
            }
            for i in indices
        ]

    def _portfolio_summary(
        self,
        weights: np.ndarray,
        expected_return: Optional[float] = None,
        risk: Optional[float] = None
    ) -> Dict[str, Any]:
        """Build a JSON-friendly summary for a weight vector."""
        if expected_return is None:
            expected_return = float(weights @ self.expected_returns)
        if risk is None:
            risk = float(np.sqrt(weights @ self.covariance @ weights.T))

        sharpe = (expected_return - self.risk_free_rate) / max(risk, 1e-6)

        weight_entries = []
        for weight, project in zip(weights, self.projects):
            weight_entries.append({
                'project_id': project['id'],
                'project_name': project['name'],
                'weight': float(weight)
            })

        weight_entries.sort(key=lambda item: item['weight'], reverse=True)

        return {
            'expected_return': float(expected_return),
            'risk': float(risk),
            'sharpe': float(sharpe),
            'weights': weight_entries
        }
