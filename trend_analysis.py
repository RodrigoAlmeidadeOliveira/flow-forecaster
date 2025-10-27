"""
Trend Analysis Module for Flow Forecaster
Automatic detection of trends, seasonality, anomalies, and performance degradation
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import find_peaks


@dataclass
class TrendAnalysis:
    """Results of trend analysis"""
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0-1, how strong is the trend
    trend_coefficient: float  # Slope of the trend line
    trend_pvalue: float  # Statistical significance

    recent_avg: float  # Average of recent period
    historical_avg: float  # Average of historical period
    change_pct: float  # Percentage change

    is_significant: bool  # Is the change statistically significant?
    confidence_level: float  # 0-1

    # Visual data for plotting
    trend_line: List[float]  # Fitted trend line values

    def to_dict(self) -> Dict:
        return {
            'trend_direction': self.trend_direction,
            'trend_strength': round(self.trend_strength, 3),
            'trend_coefficient': round(self.trend_coefficient, 4),
            'trend_pvalue': round(self.trend_pvalue, 4),
            'recent_avg': round(self.recent_avg, 2),
            'historical_avg': round(self.historical_avg, 2),
            'change_pct': round(self.change_pct, 2),
            'is_significant': self.is_significant,
            'confidence_level': round(self.confidence_level, 3),
            'trend_line': [round(v, 2) for v in self.trend_line]
        }


@dataclass
class SeasonalityAnalysis:
    """Results of seasonality analysis"""
    has_seasonality: bool
    period: Optional[int]  # Detected period (e.g., 4 for quarterly)
    seasonal_strength: float  # 0-1
    seasonal_pattern: List[float]  # The repeating pattern
    deseasonalized_data: List[float]  # Data with seasonality removed

    # Specific patterns detected
    patterns: Dict[str, any]  # e.g., {'end_of_sprint_drop': True}

    def to_dict(self) -> Dict:
        return {
            'has_seasonality': self.has_seasonality,
            'period': self.period,
            'seasonal_strength': round(self.seasonal_strength, 3),
            'seasonal_pattern': [round(v, 2) for v in self.seasonal_pattern] if self.seasonal_pattern else [],
            'deseasonalized_data': [round(v, 2) for v in self.deseasonalized_data],
            'patterns': self.patterns
        }


@dataclass
class AnomalyDetection:
    """Results of anomaly detection"""
    anomalies_count: int
    anomaly_indices: List[int]  # Indices of anomalous points
    anomaly_values: List[float]  # Values of anomalous points
    anomaly_scores: List[float]  # How anomalous each point is (0-1)

    method_used: str  # 'iqr', 'zscore', 'isolation_forest'
    threshold: float

    # Context
    upper_bound: float
    lower_bound: float

    def to_dict(self) -> Dict:
        return {
            'anomalies_count': self.anomalies_count,
            'anomaly_indices': self.anomaly_indices,
            'anomaly_values': [round(v, 2) for v in self.anomaly_values],
            'anomaly_scores': [round(s, 3) for s in self.anomaly_scores],
            'method_used': self.method_used,
            'threshold': round(self.threshold, 3),
            'upper_bound': round(self.upper_bound, 2),
            'lower_bound': round(self.lower_bound, 2)
        }


@dataclass
class ImprovementProjection:
    """Projection of improvements"""
    scenario_name: str  # e.g., 'conservative', 'moderate', 'optimistic'
    improvement_rate: float  # Percentage per period
    projected_values: List[float]  # Future projected values
    time_to_target: Optional[int]  # Periods to reach target (if specified)

    # Confidence
    lower_bound: List[float]
    upper_bound: List[float]

    def to_dict(self) -> Dict:
        return {
            'scenario_name': self.scenario_name,
            'improvement_rate': round(self.improvement_rate, 2),
            'projected_values': [round(v, 2) for v in self.projected_values],
            'time_to_target': self.time_to_target,
            'lower_bound': [round(v, 2) for v in self.lower_bound],
            'upper_bound': [round(v, 2) for v in self.upper_bound]
        }


@dataclass
class PerformanceAlert:
    """Performance degradation alert"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    alert_type: str  # 'degradation', 'anomaly', 'volatility', 'stagnation'
    message: str
    metric: str  # 'throughput', 'lead_time', etc.

    current_value: float
    expected_value: float
    deviation_pct: float

    recommendation: str

    def to_dict(self) -> Dict:
        return {
            'severity': self.severity,
            'alert_type': self.alert_type,
            'message': self.message,
            'metric': self.metric,
            'current_value': round(self.current_value, 2),
            'expected_value': round(self.expected_value, 2),
            'deviation_pct': round(self.deviation_pct, 2),
            'recommendation': self.recommendation
        }


def detect_trend(
    data: List[float],
    significance_level: float = 0.05
) -> TrendAnalysis:
    """
    Detect trend in time series data using linear regression and Mann-Kendall test.

    Args:
        data: Time series data (e.g., throughput over time)
        significance_level: p-value threshold for significance (default 0.05)

    Returns:
        TrendAnalysis object with results
    """
    if len(data) < 3:
        raise ValueError("Need at least 3 data points for trend analysis")

    data_array = np.array(data, dtype=float)
    n = len(data_array)
    x = np.arange(n)

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, data_array)
    trend_line = slope * x + intercept

    # Determine trend direction and strength
    r_squared = r_value ** 2
    trend_strength = abs(r_squared)  # How well the trend fits the data

    if abs(slope) < 0.01:  # Very small slope
        trend_direction = 'stable'
    elif slope > 0:
        trend_direction = 'improving'
    else:
        trend_direction = 'declining'

    # Calculate recent vs historical average
    split_point = max(3, n // 3)  # Use last 1/3 as "recent"
    historical_avg = float(np.mean(data_array[:-split_point]))
    recent_avg = float(np.mean(data_array[-split_point:]))

    change_pct = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0

    # Statistical significance
    is_significant = p_value < significance_level
    confidence_level = 1 - p_value

    return TrendAnalysis(
        trend_direction=trend_direction,
        trend_strength=trend_strength,
        trend_coefficient=slope,
        trend_pvalue=p_value,
        recent_avg=recent_avg,
        historical_avg=historical_avg,
        change_pct=change_pct,
        is_significant=is_significant,
        confidence_level=confidence_level,
        trend_line=trend_line.tolist()
    )


def analyze_seasonality(
    data: List[float],
    max_period: int = 8
) -> SeasonalityAnalysis:
    """
    Detect seasonality patterns in data.

    Args:
        data: Time series data
        max_period: Maximum period to check (e.g., 8 for bi-weekly)

    Returns:
        SeasonalityAnalysis object
    """
    if len(data) < max_period * 2:
        # Not enough data for seasonality analysis
        return SeasonalityAnalysis(
            has_seasonality=False,
            period=None,
            seasonal_strength=0.0,
            seasonal_pattern=[],
            deseasonalized_data=data,
            patterns={}
        )

    data_array = np.array(data, dtype=float)
    n = len(data_array)

    # Try different periods and find the one with highest autocorrelation
    best_period = None
    best_autocorr = 0.0

    for period in range(2, min(max_period + 1, n // 2)):
        # Calculate autocorrelation at this lag
        try:
            autocorr = np.corrcoef(data_array[:-period], data_array[period:])[0, 1]
            if not np.isnan(autocorr) and abs(autocorr) > best_autocorr:
                best_autocorr = abs(autocorr)
                best_period = period
        except:
            continue

    has_seasonality = best_autocorr > 0.3  # Threshold for seasonality
    seasonal_strength = best_autocorr if has_seasonality else 0.0

    # Extract seasonal pattern
    seasonal_pattern = []
    deseasonalized_data = data_array.tolist()

    if has_seasonality and best_period:
        # Calculate average for each position in the cycle
        seasonal_pattern = []
        for i in range(best_period):
            indices = list(range(i, n, best_period))
            seasonal_pattern.append(float(np.mean(data_array[indices])))

        # Deseasonalize
        overall_mean = np.mean(data_array)
        seasonal_indices = [i % best_period for i in range(n)]
        adjustments = [seasonal_pattern[idx] - overall_mean for idx in seasonal_indices]
        deseasonalized_data = (data_array - adjustments).tolist()

    # Detect specific patterns
    patterns = {}
    if len(data) >= 4:
        # Check for end-of-period drops
        last_quarter = data[-len(data)//4:]
        rest = data[:-len(data)//4]
        if np.mean(last_quarter) < np.mean(rest) * 0.8:
            patterns['end_period_drop'] = True

    return SeasonalityAnalysis(
        has_seasonality=has_seasonality,
        period=best_period,
        seasonal_strength=seasonal_strength,
        seasonal_pattern=seasonal_pattern,
        deseasonalized_data=deseasonalized_data,
        patterns=patterns
    )


def detect_anomalies(
    data: List[float],
    method: str = 'iqr',
    sensitivity: float = 1.5
) -> AnomalyDetection:
    """
    Detect anomalies/outliers in data.

    Args:
        data: Time series data
        method: Detection method ('iqr', 'zscore', 'mad')
        sensitivity: Sensitivity parameter (higher = more strict)

    Returns:
        AnomalyDetection object
    """
    if len(data) < 4:
        return AnomalyDetection(
            anomalies_count=0,
            anomaly_indices=[],
            anomaly_values=[],
            anomaly_scores=[],
            method_used=method,
            threshold=sensitivity,
            upper_bound=float(np.max(data)),
            lower_bound=float(np.min(data))
        )

    data_array = np.array(data, dtype=float)
    n = len(data_array)

    anomaly_indices = []
    anomaly_scores = []

    if method == 'iqr':
        # Interquartile Range method
        q1 = np.percentile(data_array, 25)
        q3 = np.percentile(data_array, 75)
        iqr = q3 - q1

        lower_bound = q1 - sensitivity * iqr
        upper_bound = q3 + sensitivity * iqr

        for i, value in enumerate(data_array):
            if value < lower_bound or value > upper_bound:
                anomaly_indices.append(i)
                # Score: how many IQRs away from the bounds
                if value < lower_bound:
                    score = (lower_bound - value) / (iqr if iqr > 0 else 1)
                else:
                    score = (value - upper_bound) / (iqr if iqr > 0 else 1)
                anomaly_scores.append(min(1.0, score / 3))  # Normalize to 0-1

    elif method == 'zscore':
        # Z-score method
        mean = np.mean(data_array)
        std = np.std(data_array)

        if std == 0:
            std = 1  # Avoid division by zero

        threshold = sensitivity * 2  # sensitivity * standard deviations
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std

        for i, value in enumerate(data_array):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                anomaly_indices.append(i)
                anomaly_scores.append(min(1.0, z_score / (threshold * 2)))

    elif method == 'mad':
        # Median Absolute Deviation
        median = np.median(data_array)
        mad = np.median(np.abs(data_array - median))

        if mad == 0:
            mad = 1

        threshold = sensitivity * 3.5  # Modified z-score threshold
        lower_bound = median - threshold * mad
        upper_bound = median + threshold * mad

        for i, value in enumerate(data_array):
            modified_z = abs(0.6745 * (value - median) / mad)
            if modified_z > threshold:
                anomaly_indices.append(i)
                anomaly_scores.append(min(1.0, modified_z / (threshold * 2)))

    else:
        raise ValueError(f"Unknown method: {method}")

    anomaly_values = [data_array[i] for i in anomaly_indices]

    return AnomalyDetection(
        anomalies_count=len(anomaly_indices),
        anomaly_indices=anomaly_indices,
        anomaly_values=anomaly_values,
        anomaly_scores=anomaly_scores,
        method_used=method,
        threshold=sensitivity,
        upper_bound=upper_bound,
        lower_bound=lower_bound
    )


def project_improvement(
    data: List[float],
    improvement_rates: List[float] = [5, 10, 15],  # Percentage improvements
    periods_ahead: int = 10,
    target_value: Optional[float] = None
) -> List[ImprovementProjection]:
    """
    Project future values with different improvement scenarios.

    Args:
        data: Historical time series data
        improvement_rates: List of improvement rates (%) to simulate
        periods_ahead: Number of future periods to project
        target_value: Optional target value to calculate time-to-target

    Returns:
        List of ImprovementProjection objects for each scenario
    """
    if len(data) < 2:
        raise ValueError("Need at least 2 data points for projections")

    data_array = np.array(data, dtype=float)
    current_value = data_array[-1]
    recent_std = np.std(data_array[-min(5, len(data_array)):])  # Std of recent values

    projections = []

    scenario_names = {
        5: 'conservative',
        10: 'moderate',
        15: 'optimistic',
        20: 'aggressive'
    }

    for rate in improvement_rates:
        scenario_name = scenario_names.get(rate, f'{rate}% improvement')

        # Project values with compound improvement
        projected = []
        value = current_value

        for _ in range(periods_ahead):
            value = value * (1 + rate / 100)
            projected.append(value)

        # Calculate confidence bounds (assume increasing uncertainty)
        lower_bound = []
        upper_bound = []
        for i, val in enumerate(projected):
            uncertainty = recent_std * np.sqrt(i + 1)  # Uncertainty grows with time
            lower_bound.append(max(0, val - 1.96 * uncertainty))
            upper_bound.append(val + 1.96 * uncertainty)

        # Calculate time to target
        time_to_target = None
        if target_value and target_value > current_value:
            for i, val in enumerate(projected):
                if val >= target_value:
                    time_to_target = i + 1
                    break

        projections.append(ImprovementProjection(
            scenario_name=scenario_name,
            improvement_rate=rate,
            projected_values=projected,
            time_to_target=time_to_target,
            lower_bound=lower_bound,
            upper_bound=upper_bound
        ))

    return projections


def generate_performance_alerts(
    data: List[float],
    trend: TrendAnalysis,
    anomalies: AnomalyDetection,
    metric_name: str = 'throughput'
) -> List[PerformanceAlert]:
    """
    Generate alerts based on trend and anomaly analysis.

    Args:
        data: Time series data
        trend: TrendAnalysis results
        anomalies: AnomalyDetection results
        metric_name: Name of the metric being analyzed

    Returns:
        List of PerformanceAlert objects
    """
    alerts = []

    if len(data) < 3:
        return alerts

    current_value = data[-1]
    expected_value = trend.recent_avg

    # Alert 1: Significant degradation
    if trend.trend_direction == 'declining' and trend.is_significant:
        severity = 'critical' if abs(trend.change_pct) > 20 else 'high' if abs(trend.change_pct) > 10 else 'medium'

        alerts.append(PerformanceAlert(
            severity=severity,
            alert_type='degradation',
            message=f'{metric_name.capitalize()} em declínio: {abs(trend.change_pct):.1f}% de queda detectada',
            metric=metric_name,
            current_value=trend.recent_avg,
            expected_value=trend.historical_avg,
            deviation_pct=trend.change_pct,
            recommendation='Investigue possíveis causas: mudanças no time, aumento de complexidade, impedimentos técnicos.'
        ))

    # Alert 2: High anomaly count
    if anomalies.anomalies_count > len(data) * 0.2:  # More than 20% anomalies
        alerts.append(PerformanceAlert(
            severity='high',
            alert_type='volatility',
            message=f'Alta variabilidade detectada: {anomalies.anomalies_count} outliers em {len(data)} pontos',
            metric=metric_name,
            current_value=current_value,
            expected_value=expected_value,
            deviation_pct=((current_value - expected_value) / expected_value * 100) if expected_value > 0 else 0,
            recommendation='Processo instável. Considere: padronizar tamanho de itens, reduzir interrupções, melhorar estimativas.'
        ))

    # Alert 3: Recent anomaly
    if anomalies.anomalies_count > 0 and len(data) - 1 in anomalies.anomaly_indices:
        severity = 'critical' if anomalies.anomaly_scores[anomalies.anomaly_indices.index(len(data) - 1)] > 0.8 else 'high'

        alerts.append(PerformanceAlert(
            severity=severity,
            alert_type='anomaly',
            message=f'Anomalia detectada no período mais recente: {current_value:.1f} (esperado: {expected_value:.1f})',
            metric=metric_name,
            current_value=current_value,
            expected_value=expected_value,
            deviation_pct=((current_value - expected_value) / expected_value * 100) if expected_value > 0 else 0,
            recommendation='Valor atípico detectado. Verifique se foi um evento pontual ou indica mudança no processo.'
        ))

    # Alert 4: Stagnation (no improvement)
    if trend.trend_direction == 'stable' and len(data) >= 8:
        # Check if there's been no improvement for a while
        recent_trend = detect_trend(data[-8:])
        if abs(recent_trend.change_pct) < 5:  # Less than 5% change
            alerts.append(PerformanceAlert(
                severity='medium',
                alert_type='stagnation',
                message=f'{metric_name.capitalize()} estagnado: sem melhorias significativas nos últimos períodos',
                metric=metric_name,
                current_value=current_value,
                expected_value=expected_value,
                deviation_pct=0,
                recommendation='Considere iniciativas de melhoria: retrospectivas focadas, experimentos de processo, treinamento do time.'
            ))

    # Alert 5: Positive trend (not an alert, but recognition)
    if trend.trend_direction == 'improving' and trend.is_significant and trend.change_pct > 15:
        alerts.append(PerformanceAlert(
            severity='low',
            alert_type='improvement',
            message=f'✓ {metric_name.capitalize()} melhorando: {trend.change_pct:.1f}% de aumento!',
            metric=metric_name,
            current_value=trend.recent_avg,
            expected_value=trend.historical_avg,
            deviation_pct=trend.change_pct,
            recommendation='Excelente! Identifique o que está funcionando para manter/ampliar as melhorias.'
        ))

    return alerts


def comprehensive_trend_analysis(
    data: List[float],
    metric_name: str = 'throughput',
    detect_seasonality: bool = True,
    project_future: bool = True
) -> Dict:
    """
    Perform comprehensive trend analysis combining all methods.

    Args:
        data: Time series data
        metric_name: Name of the metric
        detect_seasonality: Whether to perform seasonality analysis
        project_future: Whether to project future improvements

    Returns:
        Dictionary with all analysis results
    """
    if len(data) < 3:
        return {
            'error': 'Insufficient data for trend analysis (minimum 3 points required)',
            'data_points': len(data)
        }

    # Perform all analyses
    trend = detect_trend(data)
    anomalies = detect_anomalies(data, method='iqr')

    seasonality = None
    if detect_seasonality and len(data) >= 8:
        seasonality = analyze_seasonality(data)

    projections = None
    if project_future:
        projections = project_improvement(data, improvement_rates=[5, 10, 15])

    alerts = generate_performance_alerts(data, trend, anomalies, metric_name)

    return {
        'metric_name': metric_name,
        'data_points': len(data),
        'trend': trend.to_dict(),
        'seasonality': seasonality.to_dict() if seasonality else None,
        'anomalies': anomalies.to_dict(),
        'projections': [p.to_dict() for p in projections] if projections else None,
        'alerts': [a.to_dict() for a in alerts],
        'summary': {
            'overall_status': trend.trend_direction,
            'is_healthy': trend.trend_direction in ['improving', 'stable'] and anomalies.anomalies_count <= len(data) * 0.1,
            'requires_attention': len([a for a in alerts if a.severity in ['critical', 'high']]) > 0
        }
    }
