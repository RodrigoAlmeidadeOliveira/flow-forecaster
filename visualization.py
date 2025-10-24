"""
Visualization Module
Generates charts and plots for forecasting results
"""

import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class ForecastVisualizer:
    """Create visualizations for forecasting results"""

    def __init__(self):
        self.figures = []
        self._symbol_replacements = {
            '⚠️': '[ALERTA] ',
            '⚠': '[ALERTA] ',
            'ℹ️': '[INFO] ',
            'ℹ': '[INFO] ',
            '✓': '[OK] ',
            '✅': '[OK] ',
            '❗': '[ALERTA] ',
            '❗️': '[ALERTA] ',
            '✔️': '[OK] ',
            '✔': '[OK] ',
            '️': '',  # variation selector
        }

    def _sanitize_text(self, text: str) -> str:
        """Replace unsupported glyphs (emoji/symbols) with ASCII-friendly markers."""
        if not isinstance(text, str):
            return text
        cleaned = text
        for symbol, replacement in self._symbol_replacements.items():
            cleaned = cleaned.replace(symbol, replacement)
        return cleaned

    def plot_ml_forecasts(self, historical_data: np.ndarray,
                         forecasts: Dict[str, np.ndarray],
                         ensemble_stats: Dict[str, np.ndarray],
                         start_date: Optional[str] = None) -> str:
        """
        Plot ML model forecasts with confidence intervals.

        Args:
            historical_data: Historical throughput values
            forecasts: Dictionary of forecasts from different models
            ensemble_stats: Ensemble statistics (mean, p10, p90, etc.)
            start_date: Optional start date for x-axis labels

        Returns:
            Base64 encoded image string
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        # Prepare dates
        n_historical = len(historical_data)
        n_forecast = len(ensemble_stats['mean'])

        if start_date:
            try:
                base_date = datetime.strptime(start_date, '%Y-%m-%d')
                historical_dates = [base_date + timedelta(weeks=i) for i in range(n_historical)]
                forecast_dates = [base_date + timedelta(weeks=n_historical + i) for i in range(n_forecast)]
                use_dates = True
            except:
                use_dates = False
        else:
            use_dates = False

        if use_dates:
            x_hist = historical_dates
            x_forecast = forecast_dates
        else:
            x_hist = list(range(n_historical))
            x_forecast = list(range(n_historical, n_historical + n_forecast))

        # Plot historical data
        ax.plot(x_hist, historical_data, 'o-', color='#2E86AB', linewidth=2,
                markersize=6, label='Historical Data', zorder=3)

        # Plot individual model forecasts (lighter lines)
        colors = ['#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        for idx, (model_name, forecast) in enumerate(forecasts.items()):
            color = colors[idx % len(colors)]
            ax.plot(x_forecast, forecast, '--', alpha=0.4, linewidth=1.5,
                   color=color, label=f'{model_name}')

        # Plot ensemble mean
        ax.plot(x_forecast, ensemble_stats['mean'], 'o-', color='#E63946',
                linewidth=2.5, markersize=7, label='Ensemble Mean', zorder=3)

        # Plot confidence intervals
        ax.fill_between(x_forecast, ensemble_stats['p10'], ensemble_stats['p90'],
                       alpha=0.2, color='#E63946', label='P10-P90 Range')
        ax.fill_between(x_forecast, ensemble_stats['p25'], ensemble_stats['p75'],
                       alpha=0.3, color='#E63946', label='P25-P75 Range')

        # Styling
        ax.set_xlabel('Week' if not use_dates else 'Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput', fontsize=12, fontweight='bold')
        ax.set_title('ML Ensemble Forecast with Confidence Intervals', fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        if use_dates:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def plot_walk_forward_forecasts(self, historical_data: np.ndarray,
                                    walk_forward_results: Dict[str, Dict],
                                    start_date: Optional[str] = None) -> Dict[str, str]:
        """
        Plot walk-forward validation results for each model.

        Args:
            historical_data: Complete historical throughput series
            walk_forward_results: Metrics and predictions per model
            start_date: Optional reference date for the first observation

        Returns:
            Dictionary mapping model name to base64-encoded image
        """
        if not walk_forward_results:
            return {}

        charts: Dict[str, str] = {}
        n_samples = len(historical_data)

        use_dates = False
        if start_date:
            try:
                base_date = datetime.strptime(start_date, '%Y-%m-%d')
                x_axis = [base_date + timedelta(weeks=i) for i in range(n_samples)]
                use_dates = True
            except ValueError:
                x_axis = list(range(n_samples))
        else:
            x_axis = list(range(n_samples))

        for model_name, result in walk_forward_results.items():
            predictions = result.get('predictions') or []
            actuals = result.get('actuals') or []
            indices = result.get('indices') or []

            if not predictions or not actuals or not indices:
                continue

            paired = sorted(zip(indices, actuals, predictions), key=lambda x: x[0])
            sorted_indices, sorted_actuals, sorted_predictions = zip(*paired)

            fig, ax = plt.subplots(figsize=(12, 6))

            ax.plot(x_axis, historical_data, color='#2E86AB', linewidth=1.8,
                    alpha=0.6, label='Histórico completo')

            x_test = [x_axis[idx] for idx in sorted_indices]
            ax.plot(x_test, sorted_actuals, 'o-', color='#1B998B', linewidth=2,
                    markersize=4, label='Realizado (validação)', zorder=3)
            ax.plot(x_test, sorted_predictions, 's--', color='#E63946', linewidth=2,
                    markersize=5, label='Previsto', zorder=4)

            test_start = result.get('test_start_index')
            if isinstance(test_start, int) and 0 <= test_start < len(x_axis):
                split_value = x_axis[test_start]
                ax.axvline(split_value, color='#666', linestyle=':', linewidth=1.5,
                           label='Início da validação', zorder=2)

            ax.set_xlabel('Semana' if not use_dates else 'Data', fontsize=11, fontweight='bold')
            ax.set_ylabel('Throughput', fontsize=11, fontweight='bold')
            ax.set_title(f'Walk-forward validation - {model_name}', fontsize=13, fontweight='bold')
            ax.legend(loc='best', framealpha=0.9)
            ax.grid(True, alpha=0.3)

            if use_dates:
                plt.xticks(rotation=45, ha='right')

            plt.tight_layout()
            charts[model_name] = self._fig_to_base64(fig)

        return charts

    def plot_monte_carlo_results(self, historical_data: np.ndarray,
                                mc_results: Dict,
                                start_date: Optional[str] = None) -> str:
        """
        Plot Monte Carlo simulation results.

        Args:
            historical_data: Historical throughput values
            mc_results: Monte Carlo simulation results
            start_date: Optional start date for x-axis labels

        Returns:
            Base64 encoded image string
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Left plot: Completion time distribution
        completion_times = mc_results['completion_times']
        ax1.hist(completion_times, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')

        # Add percentile lines
        percentiles = [10, 50, 85, 90]
        colors_p = ['#6A994E', '#F18F01', '#E63946', '#A23B72']
        for p, color in zip(percentiles, colors_p):
            value = np.percentile(completion_times, p)
            ax1.axvline(value, color=color, linestyle='--', linewidth=2,
                       label=f'P{p}: {value:.1f} weeks')

        ax1.set_xlabel('Completion Time (weeks)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax1.set_title('Monte Carlo: Completion Time Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Right plot: Sample burn-down trajectories
        burn_downs = mc_results.get('burn_downs', [])[:20]  # Show first 20 simulations
        max_weeks = max(len(bd) for bd in burn_downs) if burn_downs else 0

        for bd in burn_downs:
            weeks = list(range(len(bd)))
            ax2.plot(weeks, bd, alpha=0.3, color='#2E86AB', linewidth=1)

        # Add median burn-down
        if burn_downs:
            # Interpolate to common length
            common_weeks = list(range(max_weeks))
            all_values = []
            for week in common_weeks:
                week_values = [bd[week] if week < len(bd) else 0 for bd in burn_downs]
                all_values.append(week_values)

            median_values = [np.median(vals) for vals in all_values]
            ax2.plot(common_weeks, median_values, color='#E63946', linewidth=3,
                    label='Median Trajectory', zorder=3)

        ax2.set_xlabel('Week', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Remaining Tasks', fontsize=12, fontweight='bold')
        ax2.set_title('Monte Carlo: Sample Burn-Down Trajectories', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def plot_comparison_chart(self, historical_data: np.ndarray,
                             ml_forecast: np.ndarray,
                             mc_percentiles: Dict[str, float],
                             start_date: Optional[str] = None) -> str:
        """
        Create comparison chart between ML and Monte Carlo forecasts.

        Args:
            historical_data: Historical throughput values
            ml_forecast: ML ensemble forecast
            mc_percentiles: Monte Carlo percentile results
            start_date: Optional start date

        Returns:
            Base64 encoded image string
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        # Prepare x-axis
        n_hist = len(historical_data)
        n_forecast = len(ml_forecast)

        if start_date:
            try:
                base_date = datetime.strptime(start_date, '%Y-%m-%d')
                x_hist = [base_date + timedelta(weeks=i) for i in range(n_hist)]
                x_forecast = [base_date + timedelta(weeks=n_hist + i) for i in range(n_forecast)]
                use_dates = True
            except:
                use_dates = False
        else:
            use_dates = False

        if not use_dates:
            x_hist = list(range(n_hist))
            x_forecast = list(range(n_hist, n_hist + n_forecast))

        # Plot historical
        ax.plot(x_hist, historical_data, 'o-', color='#2E86AB',
                linewidth=2, markersize=6, label='Historical', zorder=3)

        # Plot ML forecast
        ax.plot(x_forecast, ml_forecast, 's-', color='#E63946',
                linewidth=2, markersize=7, label='ML Forecast', zorder=3)

        # Add Monte Carlo reference lines
        if mc_percentiles:
            avg_mc = mc_percentiles.get('p50', 0)
            ax.axhline(avg_mc, color='#6A994E', linestyle='--', linewidth=2,
                      label=f'Monte Carlo P50: {avg_mc:.1f}', zorder=2)

        ax.set_xlabel('Week' if not use_dates else 'Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput', fontsize=12, fontweight='bold')
        ax.set_title('Forecast Comparison: ML vs Monte Carlo', fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        if use_dates:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def plot_historical_analysis(self, historical_data: np.ndarray,
                                start_date: Optional[str] = None) -> str:
        """
        Create comprehensive historical data analysis plot.

        Args:
            historical_data: Historical throughput values
            start_date: Optional start date

        Returns:
            Base64 encoded image string
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Time series plot
        if start_date:
            try:
                base_date = datetime.strptime(start_date, '%Y-%m-%d')
                dates = [base_date + timedelta(weeks=i) for i in range(len(historical_data))]
                ax1.plot(dates, historical_data, 'o-', color='#2E86AB', linewidth=2)
                ax1.set_xlabel('Date')
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            except:
                ax1.plot(historical_data, 'o-', color='#2E86AB', linewidth=2)
                ax1.set_xlabel('Week')
        else:
            ax1.plot(historical_data, 'o-', color='#2E86AB', linewidth=2)
            ax1.set_xlabel('Week')

        # Add rolling average
        if len(historical_data) >= 4:
            rolling_avg = pd.Series(historical_data).rolling(window=4, center=True).mean()
            if start_date and 'dates' in locals():
                ax1.plot(dates, rolling_avg, '--', color='#E63946', linewidth=2,
                        label='4-week Rolling Avg')
            else:
                ax1.plot(rolling_avg, '--', color='#E63946', linewidth=2,
                        label='4-week Rolling Avg')

        ax1.set_ylabel('Throughput')
        ax1.set_title('Historical Throughput Over Time', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Distribution histogram
        ax2.hist(historical_data, bins=20, color='#2E86AB', alpha=0.7, edgecolor='black')
        ax2.axvline(np.mean(historical_data), color='#E63946', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(historical_data):.1f}')
        ax2.axvline(np.median(historical_data), color='#6A994E', linestyle='--',
                   linewidth=2, label=f'Median: {np.median(historical_data):.1f}')
        ax2.set_xlabel('Throughput')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Throughput Distribution', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 3. Box plot
        ax3.boxplot(historical_data, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='#2E86AB', alpha=0.7),
                   medianprops=dict(color='#E63946', linewidth=2))
        ax3.set_ylabel('Throughput')
        ax3.set_title('Throughput Box Plot', fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')

        # 4. Autocorrelation
        if len(historical_data) > 1:
            lags = min(len(historical_data) // 2, 12)
            autocorr = [np.corrcoef(historical_data[:-i], historical_data[i:])[0, 1]
                       for i in range(1, lags + 1)]
            ax4.bar(range(1, lags + 1), autocorr, color='#2E86AB', alpha=0.7)
            ax4.axhline(0, color='black', linewidth=0.5)
            ax4.axhline(0.2, color='#E63946', linestyle='--', alpha=0.5, label='Significance')
            ax4.axhline(-0.2, color='#E63946', linestyle='--', alpha=0.5)
            ax4.set_xlabel('Lag')
            ax4.set_ylabel('Autocorrelation')
            ax4.set_title('Autocorrelation Analysis', fontweight='bold')
            ax4.legend()
            ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string with optimizations."""
        buffer = io.BytesIO()
        # Reduced DPI for faster rendering, removed bbox_inches for speed
        fig.savefig(buffer, format='png', dpi=72, bbox_inches=None, pad_inches=0.1)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        buffer.close()
        return f"data:image/png;base64,{image_base64}"

    def plot_dependency_impact(self, dependency_analysis: Dict) -> str:
        """
        Plot dependency analysis results showing impact and risks.

        Args:
            dependency_analysis: Dictionary with dependency analysis results

        Returns:
            Base64 encoded image string
        """
        fig = plt.figure(figsize=(14, 9))
        gs = fig.add_gridspec(
            3,
            4,
            height_ratios=[0.7, 2.2, 2.2],
            hspace=0.45,
            wspace=0.35
        )

        n_deps = dependency_analysis['total_dependencies']
        on_time_prob = dependency_analysis['on_time_probability']
        expected_delay = dependency_analysis.get('expected_delay_days', 0.0)
        at_least_one_delayed = dependency_analysis.get('at_least_one_delayed_probability', 0.0)
        risk_score = dependency_analysis['risk_score']
        risk_level = dependency_analysis['risk_level']
        percentiles = dependency_analysis.get('delay_percentiles', {})

        risk_palette = {
            'LOW': '#2ecc71',
            'MEDIUM': '#f1c40f',
            'HIGH': '#e67e22',
            'CRITICAL': '#e74c3c'
        }
        risk_color = risk_palette.get(risk_level.upper(), '#6c757d')

        # ------------------------------------------------------------------
        # Top metrics row
        # ------------------------------------------------------------------
        ax_metrics = fig.add_subplot(gs[0, :])
        ax_metrics.axis('off')
        card_positions = [0.02, 0.35, 0.68]
        card_width = 0.29
        card_height = 0.78
        metric_cards = [
            {
                'title': 'On-time Probability',
                'value': f"{on_time_prob * 100:.1f}%",
                'subtitle': self._sanitize_text(
                    f"Odds: {dependency_analysis['odds_ratio']} | "
                    f"At least one delayed: {at_least_one_delayed * 100:.1f}%"
                ),
                'color': '#2E86AB'
            },
            {
                'title': 'Expected Delay (if delayed)',
                'value': f"{expected_delay:.1f} days",
                'subtitle': self._sanitize_text(
                    f"P50: {percentiles.get('p50', 0):.1f}d | "
                    f"P90: {percentiles.get('p90', 0):.1f}d"
                ),
                'color': '#E67E22'
            },
            {
                'title': 'Risk Level',
                'value': self._sanitize_text(f"{risk_level}"),
                'subtitle': self._sanitize_text(
                    f"Score: {risk_score:.0f}/100 | Dependencies: {n_deps}"
                ),
                'color': risk_color
            }
        ]

        for idx, card in enumerate(metric_cards):
            x0 = card_positions[idx]
            box = FancyBboxPatch(
                (x0, 0.1),
                card_width,
                card_height,
                boxstyle="round,pad=0.02",
                linewidth=1.5,
                facecolor=card['color'],
                edgecolor=card['color'],
                alpha=0.18,
                transform=ax_metrics.transAxes
            )
            ax_metrics.add_patch(box)
            ax_metrics.text(
                x0 + card_width / 2,
                0.72,
                card['title'],
                fontsize=11,
                fontweight='bold',
                ha='center',
                va='center',
                color='#1f1f1f'
            )
            ax_metrics.text(
                x0 + card_width / 2,
                0.46,
                card['value'],
                fontsize=20,
                fontweight='bold',
                ha='center',
                va='center',
                color=card['color']
            )
            ax_metrics.text(
                x0 + card_width / 2,
                0.22,
                card['subtitle'],
                fontsize=9,
                ha='center',
                va='center',
                color='#333333'
            )

        # ------------------------------------------------------------------
        # 1. On-time Probability vs Number of Dependencies
        # ------------------------------------------------------------------
        ax1 = fig.add_subplot(gs[1, :2])

        # Show exponential decay curve
        x = range(0, max(8, n_deps + 3))
        y_simple = [0.5 ** i for i in x]

        ax1.plot(
            x,
            [p * 100 for p in y_simple],
            color='#7FDBFF',
            alpha=0.8,
            linewidth=2.5,
            label='Simplified model (50% each)'
        )
        ax1.scatter(
            [n_deps],
            [on_time_prob * 100],
            s=180,
            c=risk_color,
            marker='o',
            zorder=5,
            edgecolors='#2c3e50',
            linewidths=1.5
        )
        ax1.axhline(
            y=on_time_prob * 100,
            color=risk_color,
            linestyle='--',
            alpha=0.5,
            label=f'Current probability: {on_time_prob * 100:.1f}%'
        )

        ax1.set_xlabel('Number of dependencies', fontsize=11, fontweight='bold')
        ax1.set_ylabel('On-time delivery probability (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Impact of dependency count on delivery confidence', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.25)
        ax1.set_facecolor('#f8f9fa')
        for spine in ax1.spines.values():
            spine.set_color('#dcdcdc')
        ax1.legend(loc='upper right', fontsize=9, frameon=False)

        # Add annotation
        dep_label = "dependency" if n_deps == 1 else "dependencies"
        annotation = self._sanitize_text(
            f"{n_deps} {dep_label}\n{on_time_prob * 100:.1f}% probability\n({dependency_analysis['odds_ratio']})"
        )
        ax1.annotate(
            annotation,
            xy=(n_deps, on_time_prob * 100),
            xytext=(n_deps + 0.7, min(100, on_time_prob * 100 + 15)),
            arrowprops=dict(arrowstyle='->', color=risk_color, lw=2),
            fontsize=9,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9)
        )

        # ------------------------------------------------------------------
        # 2. Delay Distribution (Percentiles)
        # ------------------------------------------------------------------
        ax2 = fig.add_subplot(gs[1, 2:])
        p_labels = list(percentiles.keys())
        p_values = [percentiles[p] for p in p_labels]

        colors = plt.cm.YlOrRd(np.linspace(0.4, 0.85, len(p_labels))) if p_labels else []
        bars = ax2.barh(
            p_labels,
            p_values,
            color=colors,
            edgecolor='#d35400',
            linewidth=1.1
        )

        ax2.set_xlabel('Expected delay (days)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Percentile', fontsize=11, fontweight='bold')
        ax2.set_title('Delay distribution when dependency slips', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.25, axis='x')
        ax2.set_facecolor('#fef9f3')
        for spine in ax2.spines.values():
            spine.set_color('#dcdcdc')

        max_delay = max(p_values) if p_values else 0
        for i, (bar, val) in enumerate(zip(bars, p_values)):
            ax2.text(
                val + (max_delay * 0.02 if max_delay else 0.5),
                bar.get_y() + bar.get_height() / 2,
                f'{val:.1f} d',
                va='center',
                fontsize=9,
                fontweight='bold',
                color='#6e2c00'
            )

        # ------------------------------------------------------------------
        # Bottom-left: risk gauge + critical path (sub-gridspec)
        # ------------------------------------------------------------------
        sub_gs = gs[2, :2].subgridspec(2, 1, height_ratios=[0.8, 1.4], hspace=0.30)

        ax_risk = fig.add_subplot(sub_gs[0])
        ax_risk.set_xlim(0, 100)
        ax_risk.set_ylim(0, 1)
        ax_risk.axis('off')
        ax_risk.set_title('Aggregate risk profile', fontsize=11, fontweight='bold', loc='left')

        risk_zones = [
            (0, 25, '#d4efdf'),
            (25, 50, '#fcf3cf'),
            (50, 75, '#fdebd0'),
            (75, 100, '#f5b7b1')
        ]
        for start, end, color in risk_zones:
            ax_risk.axvspan(start, end, color=color, alpha=0.8, ymin=0.35, ymax=0.85)

        ax_risk.barh(
            0.6,
            risk_score,
            height=0.25,
            color=risk_color,
            alpha=0.7,
            edgecolor='#444'
        )
        ax_risk.scatter([risk_score], [0.6], color='#2c3e50', s=40, zorder=3)
        ax_risk.text(
            risk_score,
            0.25,
            self._sanitize_text(f'{risk_score:.0f}/100 - {risk_level}'),
            ha='center',
            va='center',
            fontsize=10,
            fontweight='bold'
        )
        ax_risk.text(0, 0.05, '0', fontsize=9, fontweight='bold')
        ax_risk.text(50, 0.05, '50', fontsize=9, fontweight='bold', ha='center')
        ax_risk.text(100, 0.05, '100', fontsize=9, fontweight='bold', ha='right')

        ax4 = fig.add_subplot(sub_gs[1])
        critical_path = dependency_analysis['critical_path'][:5]

        if critical_path:
            y_pos = np.arange(len(critical_path))
            labels = [cp[:40] + '...' if len(cp) > 40 else cp for cp in critical_path]

            priorities = list(range(len(critical_path), 0, -1))
            colors_crit = plt.cm.Reds(np.linspace(0.35, 0.85, len(critical_path)))
            ax4.barh(
                y_pos,
                priorities,
                color=colors_crit,
                edgecolor='#922b21',
                linewidth=1.1
            )
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(labels, fontsize=9)
            ax4.set_xlabel('Priority (1 = most critical)', fontsize=10, fontweight='bold')
            ax4.set_title('Top 5 critical dependencies', fontsize=11, fontweight='bold', loc='left')
            ax4.set_facecolor('#fdf0ee')
            ax4.invert_yaxis()
            for spine in ax4.spines.values():
                spine.set_visible(False)
            ax4.grid(True, axis='x', alpha=0.15)
        else:
            ax4.text(0.5, 0.5, 'No critical dependencies identified', ha='center', va='center', fontsize=11)
            ax4.axis('off')

        # ------------------------------------------------------------------
        # 5. Summary & recommendations
        # ------------------------------------------------------------------
        ax_summary = fig.add_subplot(gs[2, 2:])
        ax_summary.axis('off')

        summary_lines = [
            "Dependency analysis snapshot",
            f"- Total dependencies: {n_deps}",
            f"- On-time probability: {on_time_prob * 100:.1f}% ({dependency_analysis['odds_ratio']})",
            f"- At least one delayed: {at_least_one_delayed * 100:.1f}%",
            f"- Mean delay if slipped: {expected_delay:.1f} days",
            f"- Median delay (P50): {percentiles.get('p50', 0):.1f} days",
            f"- 90th percentile delay: {percentiles.get('p90', 0):.1f} days",
        ]
        summary_text = self._sanitize_text("\n".join(summary_lines))

        ax_summary.text(
            0.02,
            0.96,
            summary_text,
            transform=ax_summary.transAxes,
            fontsize=10,
            va='top',
            ha='left',
            bbox=dict(boxstyle='round', facecolor='#fdf7e3', edgecolor='#f1c40f', alpha=0.9)
        )

        # Recommendations block
        recommendations = dependency_analysis.get('recommendations', [])
        if recommendations:
            sanitized_recs = [self._sanitize_text(rec) for rec in recommendations[:4]]
            rec_text = "Priority recommendations:\n" + "\n".join([f"- {rec}" for rec in sanitized_recs])
            ax_summary.text(
                0.02,
                0.38,
                rec_text,
                transform=ax_summary.transAxes,
                fontsize=9.5,
                va='top',
                ha='left',
                bbox=dict(boxstyle='round', facecolor='#e8f4fb', edgecolor='#3498db', alpha=0.9)
            )

        fig.suptitle(
            'Dependency Impact Analysis for Project Forecasting',
            fontsize=14,
            fontweight='bold',
            y=0.98
        )

        return self._fig_to_base64(fig)


# For pandas import if needed
try:
    import pandas as pd
except ImportError:
    pd = None
