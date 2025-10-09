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
        """Convert matplotlib figure to base64 string."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"


# For pandas import if needed
try:
    import pandas as pd
except ImportError:
    pd = None
