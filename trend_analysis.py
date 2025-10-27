"""
Trend Analysis Module for Flow Forecaster
Automatic detection of trends, seasonality, anomalies, and performance degradation
"""
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from scipy import stats
from scipy.signal import find_peaks


@dataclass
class TrendAnalysis:
    """Results of trend analysis"""
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0-1, how strong is the trend
    trend_coefficient: float  # Slope of the trend line
    trend_pvalue: float  # Statistical significance
    mann_kendall_tau: Optional[float]  # Non-parametric trend strength
    mann_kendall_pvalue: Optional[float]

    recent_avg: float  # Average of recent period
    historical_avg: float  # Average of historical period
    change_pct: float  # Percentage change

    is_significant: bool  # Is the change statistically significant?
    confidence_level: float  # 0-1
    slope_confidence_interval: Tuple[float, float]
    volatility: float  # Recent standard deviation

    # Visual data for plotting
    trend_line: List[float]  # Fitted trend line values

    def to_dict(self) -> Dict:
        return {
            'trend_direction': self.trend_direction,
            'trend_strength': round(self.trend_strength, 3),
            'trend_coefficient': round(self.trend_coefficient, 4),
            'trend_pvalue': round(self.trend_pvalue, 4),
            'mann_kendall_tau': round(self.mann_kendall_tau, 4) if self.mann_kendall_tau is not None else None,
            'mann_kendall_pvalue': round(self.mann_kendall_pvalue, 4) if self.mann_kendall_pvalue is not None else None,
            'recent_avg': round(self.recent_avg, 2),
            'historical_avg': round(self.historical_avg, 2),
            'change_pct': round(self.change_pct, 2),
            'is_significant': self.is_significant,
            'confidence_level': round(self.confidence_level, 3),
            'slope_confidence_interval': [round(v, 4) for v in self.slope_confidence_interval],
            'volatility': round(self.volatility, 3),
            'trend_line': [round(v, 2) for v in self.trend_line]
        }


@dataclass
class SeasonalityAnalysis:
    """Results of seasonality analysis"""
    has_seasonality: bool
    period: Optional[int]  # Detected period (e.g., 4 for quarterly)
    seasonal_strength: float  # 0-1
    seasonality_confidence: float  # 0-1 combined confidence
    dominant_periods: List[int]
    peak_indices: List[int]
    trough_indices: List[int]
    seasonal_pattern: List[float]  # The repeating pattern
    deseasonalized_data: List[float]  # Data with seasonality removed

    # Specific patterns detected
    patterns: Dict[str, Any]  # e.g., {'end_of_sprint_drop': True}

    def to_dict(self) -> Dict:
        return {
            'has_seasonality': self.has_seasonality,
            'period': self.period,
            'seasonal_strength': round(self.seasonal_strength, 3),
            'seasonality_confidence': round(self.seasonality_confidence, 3),
            'dominant_periods': self.dominant_periods,
            'peak_indices': self.peak_indices,
            'trough_indices': self.trough_indices,
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
    recent_anomaly: bool
    latest_anomaly_score: Optional[float]

    def to_dict(self) -> Dict:
        return {
            'anomalies_count': self.anomalies_count,
            'anomaly_indices': self.anomaly_indices,
            'anomaly_values': [round(v, 2) for v in self.anomaly_values],
            'anomaly_scores': [round(s, 3) for s in self.anomaly_scores],
            'method_used': self.method_used,
            'threshold': round(self.threshold, 3),
            'upper_bound': round(self.upper_bound, 2),
            'lower_bound': round(self.lower_bound, 2),
            'recent_anomaly': self.recent_anomaly,
            'latest_anomaly_score': round(self.latest_anomaly_score, 3) if self.latest_anomaly_score is not None else None
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
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'scenario_name': self.scenario_name,
            'improvement_rate': round(self.improvement_rate, 2),
            'projected_values': [round(v, 2) for v in self.projected_values],
            'time_to_target': self.time_to_target,
            'lower_bound': [round(v, 2) for v in self.lower_bound],
            'upper_bound': [round(v, 2) for v in self.upper_bound],
            'notes': self.notes
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


def _mann_kendall_test(data: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Run a Mann-Kendall trend test returning tau and p-value."""
    if len(data) < 3:
        return None, None

    try:
        tau, p_value = stats.kendalltau(np.arange(len(data)), data)
    except Exception:
        return None, None

    if tau is not None and np.isnan(tau):
        tau = None
    if p_value is not None and np.isnan(p_value):
        p_value = None

    return (float(tau) if tau is not None else None, float(p_value) if p_value is not None else None)


def _slope_confidence_interval(
    slope: float,
    std_err: float,
    n: int,
    significance_level: float
) -> Tuple[float, float]:
    """Compute a confidence interval for the regression slope."""
    if n <= 2 or std_err is None or np.isnan(std_err):
        return float(slope), float(slope)

    try:
        t_value = stats.t.ppf(1 - significance_level / 2, n - 2)
    except Exception:
        t_value = 0

    if np.isnan(t_value):
        t_value = 0

    margin = t_value * std_err
    if np.isnan(margin):
        margin = 0

    return float(slope - margin), float(slope + margin)


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
    tau, mann_kendall_pvalue = _mann_kendall_test(data_array)

    # Determine trend direction and strength
    r_strength = abs(r_value)
    tau_strength = abs(tau) if tau is not None else 0.0
    trend_strength = float(np.clip(0.7 * (r_strength ** 2) + 0.3 * tau_strength, 0, 1))

    if tau is not None and abs(tau) >= 0.2:
        trend_direction = 'improving' if tau > 0 else 'declining'
    elif abs(slope) < 0.01:  # Very small slope
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
    combined_pvalue = min(p_value, mann_kendall_pvalue) if mann_kendall_pvalue is not None else p_value
    is_significant = (p_value < significance_level) or (mann_kendall_pvalue is not None and mann_kendall_pvalue < significance_level)
    confidence_level = float(np.clip(1 - combined_pvalue, 0, 1))
    slope_confidence_interval = _slope_confidence_interval(slope, std_err, n, significance_level)
    volatility = float(np.std(data_array[-min(6, n):])) if n > 1 else 0.0

    return TrendAnalysis(
        trend_direction=trend_direction,
        trend_strength=trend_strength,
        trend_coefficient=slope,
        trend_pvalue=p_value,
        mann_kendall_tau=tau,
        mann_kendall_pvalue=mann_kendall_pvalue,
        recent_avg=recent_avg,
        historical_avg=historical_avg,
        change_pct=change_pct,
        is_significant=is_significant,
        confidence_level=confidence_level,
        slope_confidence_interval=slope_confidence_interval,
        volatility=volatility,
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
            seasonality_confidence=0.0,
            dominant_periods=[],
            peak_indices=[],
            trough_indices=[],
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
    seasonal_pattern: List[float] = []
    deseasonalized_data = data_array.tolist()
    dominant_periods: List[int] = []
    peak_indices: List[int] = []
    trough_indices: List[int] = []

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

        # Extract dominant periods using FFT
        demeaned = data_array - np.mean(data_array)
        fft = np.fft.rfft(demeaned)
        power = np.abs(fft)
        power_nonzero = power[1:] if len(power) > 1 else np.array([])
        freqs = np.fft.rfftfreq(n, d=1)

        if len(power_nonzero) > 0:
            sorted_indices = np.argsort(power_nonzero)[-3:] + 1  # Ignore zero frequency
            for idx in reversed(sorted_indices):
                freq = freqs[idx]
                if freq <= 0:
                    continue
                period_estimate = int(round(1 / freq))
                if period_estimate >= 2 and period_estimate <= max(n // 2, max_period) and period_estimate not in dominant_periods:
                    dominant_periods.append(period_estimate)

        # Detect peaks and troughs for pattern insights
        peak_indices, _ = find_peaks(data_array)
        trough_indices, _ = find_peaks(-data_array)

    # Detect specific patterns
    patterns = {}
    if len(data) >= 4:
        # Check for end-of-period drops
        last_quarter = data[-len(data)//4:]
        rest = data[:-len(data)//4]
        if np.mean(last_quarter) < np.mean(rest) * 0.8:
            patterns['end_period_drop'] = True

    if has_seasonality and best_period:
        patterns['dominant_period'] = best_period
        patterns['peak_count'] = len(peak_indices)
        patterns['trough_count'] = len(trough_indices)
        if best_period in (2, 4):
            patterns['sprint_cycle_candidate'] = True

    # Combine confidence metrics
    if has_seasonality:
        if 'power_nonzero' in locals() and len(power_nonzero) > 0:
            power_total = float(np.sum(power_nonzero))
            top_power = float(np.max(power_nonzero))
        else:
            fft_vals = np.abs(np.fft.rfft(data_array))[1:]
            power_total = float(np.sum(fft_vals))
            top_power = float(np.max(fft_vals)) if len(fft_vals) else 0.0
        freq_confidence = (top_power / power_total) if power_total > 0 else 0.0
        seasonality_confidence = float(np.clip((seasonal_strength + freq_confidence) / 2, 0, 1))
    else:
        seasonality_confidence = 0.0

    return SeasonalityAnalysis(
        has_seasonality=has_seasonality,
        period=best_period,
        seasonal_strength=seasonal_strength,
        seasonality_confidence=seasonality_confidence,
        dominant_periods=dominant_periods,
        peak_indices=peak_indices,
        trough_indices=trough_indices,
        seasonal_pattern=seasonal_pattern,
        deseasonalized_data=deseasonalized_data,
        patterns=patterns
    )


def detect_anomalies(
    data: List[float],
    method: str = 'iqr',
    sensitivity: float = 1.5,
    rolling_window: int = 5
) -> AnomalyDetection:
    """
    Detect anomalies/outliers in data.

    Args:
        data: Time series data
        method: Detection method ('iqr', 'zscore', 'mad', 'rolling_zscore')
        sensitivity: Sensitivity parameter (higher = more strict)
        rolling_window: Window size for rolling z-score method

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
            lower_bound=float(np.min(data)),
            recent_anomaly=False,
            latest_anomaly_score=None
        )

    data_array = np.array(data, dtype=float)
    n = len(data_array)

    anomaly_indices = []
    anomaly_scores = []
    upper_bound = float(np.max(data_array))
    lower_bound = float(np.min(data_array))

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

    elif method == 'rolling_zscore':
        window = max(3, int(rolling_window))
        dynamic_lowers = []
        dynamic_uppers = []
        threshold = max(1.5, sensitivity * 1.5)

        for i, value in enumerate(data_array):
            start = max(0, i - window + 1)
            window_slice = data_array[start:i + 1]
            mean = np.mean(window_slice)
            std = np.std(window_slice)
            if std == 0:
                std = 1e-6

            bound_margin = sensitivity * std
            dynamic_lowers.append(mean - bound_margin)
            dynamic_uppers.append(mean + bound_margin)

            if i >= window - 1:
                z_score = abs((value - mean) / std)
                if z_score > threshold:
                    anomaly_indices.append(i)
                    anomaly_scores.append(min(1.0, z_score / (threshold * 2)))

        if dynamic_lowers:
            lower_bound = float(min(dynamic_lowers))
        if dynamic_uppers:
            upper_bound = float(max(dynamic_uppers))

    else:
        raise ValueError(f"Unknown method: {method}")

    anomaly_values = [data_array[i] for i in anomaly_indices]
    recent_anomaly = len(data_array) - 1 in anomaly_indices
    latest_anomaly_score = None
    if recent_anomaly:
        last_idx = anomaly_indices.index(len(data_array) - 1)
        latest_anomaly_score = anomaly_scores[last_idx] if last_idx < len(anomaly_scores) else None

    return AnomalyDetection(
        anomalies_count=len(anomaly_indices),
        anomaly_indices=anomaly_indices,
        anomaly_values=anomaly_values,
        anomaly_scores=anomaly_scores,
        method_used=method,
        threshold=sensitivity,
        upper_bound=upper_bound,
        lower_bound=lower_bound,
        recent_anomaly=recent_anomaly,
        latest_anomaly_score=latest_anomaly_score
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

        if rate == 10:
            notes = 'Cenário padrão: melhoria de 10% por sprint/prazo.'
        elif rate < 10:
            notes = f'Cenário conservador com crescimento de {rate}% por período.'
        elif rate > 10:
            notes = f'Hipótese agressiva com melhoria de {rate}% por período.'
        else:
            notes = None

        if target_value and time_to_target:
            notes = (notes + f' Atinge a meta ({target_value:.2f}) em {time_to_target} períodos.') if notes else f'Atinge a meta ({target_value:.2f}) em {time_to_target} períodos.'

        projections.append(ImprovementProjection(
            scenario_name=scenario_name,
            improvement_rate=rate,
            projected_values=projected,
            time_to_target=time_to_target,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            notes=notes
        ))

    return projections


def generate_performance_alerts(
    data: List[float],
    trend: TrendAnalysis,
    anomalies: AnomalyDetection,
    seasonality: Optional[SeasonalityAnalysis] = None,
    metric_name: str = 'throughput'
) -> List[PerformanceAlert]:
    """
    Generate alerts based on trend and anomaly analysis.

    Args:
        data: Time series data
        trend: TrendAnalysis results
        anomalies: AnomalyDetection results
        seasonality: Optional seasonality analysis for contextual alerts
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
    if anomalies.recent_anomaly:
        score = anomalies.latest_anomaly_score or 0
        severity = 'critical' if score > 0.8 else 'high'
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

    # Alert 4: Excess volatility
    if trend.volatility > max(0.01, trend.recent_avg) * 0.3:
        volatility_pct = (trend.volatility / trend.recent_avg * 100) if trend.recent_avg > 0 else trend.volatility * 100
        alerts.append(PerformanceAlert(
            severity='medium',
            alert_type='volatility',
            message=f'Volatilidade elevada: desvios recentes representam {volatility_pct:.1f}% do valor médio.',
            metric=metric_name,
            current_value=current_value,
            expected_value=expected_value,
            deviation_pct=volatility_pct,
            recommendation='Reforce políticas de entrada, fatie histórias grandes e estabilize cadência de entregas.'
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

    # Alert 5: Seasonality driven degradation
    if seasonality and seasonality.has_seasonality and seasonality.patterns.get('end_period_drop'):
        alerts.append(PerformanceAlert(
            severity='medium',
            alert_type='seasonality',
            message='Queda recorrente ao final do ciclo detectada. Ajuste previsões para absorver esse comportamento.',
            metric=metric_name,
            current_value=current_value,
            expected_value=expected_value,
            deviation_pct=((current_value - expected_value) / expected_value * 100) if expected_value > 0 else 0,
            recommendation='Planeje capacidade extra para o final do ciclo ou distribua melhor as entregas ao longo do período.'
        ))

    # Alert 6: Positive trend (recognition)
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

    alerts = generate_performance_alerts(
        data,
        trend,
        anomalies,
        seasonality=seasonality,
        metric_name=metric_name
    )

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
