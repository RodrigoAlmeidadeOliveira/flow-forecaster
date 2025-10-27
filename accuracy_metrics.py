"""
Accuracy Metrics for Forecast vs Actual Analysis
Calculates various accuracy metrics to evaluate forecast quality
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccuracyMetrics:
    """Container for accuracy metrics"""
    # Basic metrics
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Squared Error
    mape: float  # Mean Absolute Percentage Error
    mpe: float  # Mean Percentage Error (bias)

    # Additional metrics
    median_ape: float  # Median Absolute Percentage Error
    r_squared: float  # Coefficient of Determination
    accuracy_rate: float  # Percentage of forecasts within acceptable range

    # Statistical info
    n_samples: int
    min_error: float
    max_error: float
    std_error: float

    # Bias indicators
    overforecast_count: int
    underforecast_count: int
    bias_direction: str  # 'overforecasting', 'underforecasting', 'balanced'

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'mae': round(self.mae, 2),
            'rmse': round(self.rmse, 2),
            'mape': round(self.mape, 2),
            'mpe': round(self.mpe, 2),
            'median_ape': round(self.median_ape, 2),
            'r_squared': round(self.r_squared, 4),
            'accuracy_rate': round(self.accuracy_rate, 2),
            'n_samples': self.n_samples,
            'min_error': round(self.min_error, 2),
            'max_error': round(self.max_error, 2),
            'std_error': round(self.std_error, 2),
            'overforecast_count': self.overforecast_count,
            'underforecast_count': self.underforecast_count,
            'bias_direction': self.bias_direction
        }

    def get_quality_rating(self) -> Dict[str, str]:
        """
        Evaluate forecast quality based on metrics

        Returns:
            Dict with overall rating and component ratings
        """
        ratings = {}

        # MAPE rating (industry standard)
        if self.mape < 10:
            ratings['mape'] = 'Excelente'
        elif self.mape < 20:
            ratings['mape'] = 'Bom'
        elif self.mape < 50:
            ratings['mape'] = 'Aceitável'
        else:
            ratings['mape'] = 'Ruim'

        # Accuracy rate rating
        if self.accuracy_rate >= 80:
            ratings['accuracy_rate'] = 'Excelente'
        elif self.accuracy_rate >= 60:
            ratings['accuracy_rate'] = 'Bom'
        elif self.accuracy_rate >= 40:
            ratings['accuracy_rate'] = 'Aceitável'
        else:
            ratings['accuracy_rate'] = 'Ruim'

        # R² rating
        if self.r_squared >= 0.9:
            ratings['r_squared'] = 'Excelente'
        elif self.r_squared >= 0.7:
            ratings['r_squared'] = 'Bom'
        elif self.r_squared >= 0.5:
            ratings['r_squared'] = 'Aceitável'
        else:
            ratings['r_squared'] = 'Ruim'

        # Overall rating (weighted average)
        score = 0
        if ratings['mape'] == 'Excelente':
            score += 3
        elif ratings['mape'] == 'Bom':
            score += 2
        elif ratings['mape'] == 'Aceitável':
            score += 1

        if ratings['accuracy_rate'] == 'Excelente':
            score += 2
        elif ratings['accuracy_rate'] == 'Bom':
            score += 1.5
        elif ratings['accuracy_rate'] == 'Aceitável':
            score += 0.5

        if ratings['r_squared'] == 'Excelente':
            score += 2
        elif ratings['r_squared'] == 'Bom':
            score += 1.5
        elif ratings['r_squared'] == 'Aceitável':
            score += 0.5

        if score >= 6:
            ratings['overall'] = 'Excelente'
        elif score >= 4:
            ratings['overall'] = 'Bom'
        elif score >= 2:
            ratings['overall'] = 'Aceitável'
        else:
            ratings['overall'] = 'Ruim'

        return ratings


def calculate_accuracy_metrics(
    forecasts: List[float],
    actuals: List[float],
    acceptable_error_pct: float = 20.0
) -> AccuracyMetrics:
    """
    Calculate comprehensive accuracy metrics for forecast vs actual comparison.

    Args:
        forecasts: List of forecasted values
        actuals: List of actual values
        acceptable_error_pct: Percentage error considered acceptable (default 20%)

    Returns:
        AccuracyMetrics object with all calculated metrics

    Raises:
        ValueError: If inputs are invalid
    """
    if not forecasts or not actuals:
        raise ValueError("Forecasts and actuals cannot be empty")

    if len(forecasts) != len(actuals):
        raise ValueError(f"Forecasts ({len(forecasts)}) and actuals ({len(actuals)}) must have same length")

    forecasts = np.array(forecasts, dtype=float)
    actuals = np.array(actuals, dtype=float)

    # Check for zero or negative actuals (problematic for percentage metrics)
    if np.any(actuals <= 0):
        raise ValueError("Actual values must be positive for percentage-based metrics")

    n = len(forecasts)

    # Calculate errors
    errors = forecasts - actuals
    abs_errors = np.abs(errors)
    pct_errors = (errors / actuals) * 100
    abs_pct_errors = np.abs(pct_errors)

    # Basic metrics
    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    mape = float(np.mean(abs_pct_errors))
    mpe = float(np.mean(pct_errors))

    # Additional metrics
    median_ape = float(np.median(abs_pct_errors))

    # R-squared (coefficient of determination)
    ss_res = np.sum((actuals - forecasts) ** 2)
    ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
    r_squared = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0

    # Accuracy rate (percentage within acceptable error)
    within_range = np.sum(abs_pct_errors <= acceptable_error_pct)
    accuracy_rate = float((within_range / n) * 100)

    # Error statistics
    min_error = float(np.min(errors))
    max_error = float(np.max(errors))
    std_error = float(np.std(errors))

    # Bias analysis
    overforecast_count = int(np.sum(errors > 0))
    underforecast_count = int(np.sum(errors < 0))

    if overforecast_count > underforecast_count * 1.5:
        bias_direction = 'overforecasting'
    elif underforecast_count > overforecast_count * 1.5:
        bias_direction = 'underforecasting'
    else:
        bias_direction = 'balanced'

    return AccuracyMetrics(
        mae=mae,
        rmse=rmse,
        mape=mape,
        mpe=mpe,
        median_ape=median_ape,
        r_squared=r_squared,
        accuracy_rate=accuracy_rate,
        n_samples=n,
        min_error=min_error,
        max_error=max_error,
        std_error=std_error,
        overforecast_count=overforecast_count,
        underforecast_count=underforecast_count,
        bias_direction=bias_direction
    )


def calculate_time_series_metrics(
    forecasts: List[float],
    actuals: List[float],
    dates: Optional[List[datetime]] = None
) -> Dict:
    """
    Calculate time-series specific metrics and trends.

    Args:
        forecasts: List of forecasted values
        actuals: List of actual values
        dates: Optional list of dates for temporal analysis

    Returns:
        Dictionary with time-series metrics
    """
    forecasts = np.array(forecasts, dtype=float)
    actuals = np.array(actuals, dtype=float)
    errors = forecasts - actuals

    # Trend analysis
    if len(forecasts) >= 3:
        # Calculate if error is increasing or decreasing over time
        error_trend = np.polyfit(range(len(errors)), errors, 1)[0]
        trend_direction = 'improving' if error_trend < 0 else 'worsening' if error_trend > 0 else 'stable'
    else:
        error_trend = 0.0
        trend_direction = 'insufficient_data'

    # Recent vs historical performance
    if len(forecasts) >= 6:
        recent_mape = float(np.mean(np.abs((errors[-3:] / actuals[-3:]) * 100)))
        historical_mape = float(np.mean(np.abs((errors[:-3] / actuals[:-3]) * 100)))
        performance_change = recent_mape - historical_mape
    else:
        recent_mape = None
        historical_mape = None
        performance_change = None

    return {
        'error_trend': float(error_trend),
        'trend_direction': trend_direction,
        'recent_mape': round(recent_mape, 2) if recent_mape else None,
        'historical_mape': round(historical_mape, 2) if historical_mape else None,
        'performance_change': round(performance_change, 2) if performance_change else None,
        'performance_trend': 'improving' if performance_change and performance_change < 0 else 'worsening' if performance_change and performance_change > 0 else 'stable'
    }


def detect_data_quality_issues(
    forecasts: List[float],
    actuals: List[float],
    tp_samples: Optional[List[float]] = None
) -> List[Dict[str, str]]:
    """
    Detect potential data quality issues in forecasts or actuals.

    Args:
        forecasts: List of forecasted values
        actuals: List of actual values
        tp_samples: Optional throughput samples for additional validation

    Returns:
        List of detected issues with severity and description
    """
    issues = []

    forecasts = np.array(forecasts, dtype=float)
    actuals = np.array(actuals, dtype=float)

    # Issue 1: Insufficient data
    if len(forecasts) < 3:
        issues.append({
            'severity': 'warning',
            'type': 'insufficient_data',
            'message': f'Apenas {len(forecasts)} comparações disponíveis. Mínimo recomendado: 5 para análise confiável.'
        })

    # Issue 2: Extreme outliers
    errors = forecasts - actuals
    pct_errors = (errors / actuals) * 100
    outliers = np.abs(pct_errors) > 100  # More than 100% error

    if np.any(outliers):
        outlier_count = int(np.sum(outliers))
        issues.append({
            'severity': 'high',
            'type': 'extreme_outliers',
            'message': f'{outlier_count} previsões com erro superior a 100%. Revise os dados de entrada.'
        })

    # Issue 3: Consistent bias
    if len(forecasts) >= 5:
        overforecast = np.sum(errors > 0)
        underforecast = np.sum(errors < 0)

        if overforecast >= len(forecasts) * 0.8:
            issues.append({
                'severity': 'medium',
                'type': 'consistent_overforecast',
                'message': f'Superestimativa consistente em {overforecast}/{len(forecasts)} casos. Considere ajustar parâmetros.'
            })
        elif underforecast >= len(forecasts) * 0.8:
            issues.append({
                'severity': 'medium',
                'type': 'consistent_underforecast',
                'message': f'Subestimativa consistente em {underforecast}/{len(forecasts)} casos. Considere ajustar parâmetros.'
            })

    # Issue 4: High variability
    if len(forecasts) >= 3:
        cv = np.std(errors) / np.mean(np.abs(errors)) if np.mean(np.abs(errors)) > 0 else 0
        if cv > 1.5:
            issues.append({
                'severity': 'medium',
                'type': 'high_variability',
                'message': f'Alta variabilidade nos erros (CV={cv:.2f}). Previsões inconsistentes.'
            })

    # Issue 5: Zero or negative actuals
    if np.any(actuals <= 0):
        zero_count = int(np.sum(actuals <= 0))
        issues.append({
            'severity': 'high',
            'type': 'invalid_actuals',
            'message': f'{zero_count} valores reais inválidos (≤0). Corrija os dados.'
        })

    # Issue 6: Forecast and actual completely misaligned
    correlation = np.corrcoef(forecasts, actuals)[0, 1]
    if len(forecasts) >= 5 and correlation < 0.3:
        issues.append({
            'severity': 'high',
            'type': 'low_correlation',
            'message': f'Correlação muito baixa ({correlation:.2f}) entre previsões e realidade. Revise o modelo.'
        })

    # Issue 7: Throughput samples quality (if provided)
    if tp_samples:
        tp_array = np.array(tp_samples, dtype=float)
        if len(tp_array) < 5:
            issues.append({
                'severity': 'warning',
                'type': 'few_throughput_samples',
                'message': f'Apenas {len(tp_array)} amostras de throughput. Mínimo recomendado: 5-8.'
            })

        # Check for outliers in throughput
        if len(tp_array) >= 3:
            q1 = np.percentile(tp_array, 25)
            q3 = np.percentile(tp_array, 75)
            iqr = q3 - q1
            outlier_threshold = q3 + 3 * iqr
            tp_outliers = np.sum(tp_array > outlier_threshold)

            if tp_outliers > 0:
                issues.append({
                    'severity': 'warning',
                    'type': 'throughput_outliers',
                    'message': f'{tp_outliers} outliers detectados nas amostras de throughput. Considere revisar.'
                })

    return issues


def generate_recommendations(
    metrics: AccuracyMetrics,
    issues: List[Dict[str, str]]
) -> List[str]:
    """
    Generate actionable recommendations based on metrics and issues.

    Args:
        metrics: Calculated accuracy metrics
        issues: List of detected data quality issues

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Based on MAPE
    if metrics.mape > 50:
        recommendations.append(
            "MAPE muito alto (>50%). Considere: (1) Coletar mais amostras históricas, "
            "(2) Revisar dados de entrada, (3) Ajustar parâmetros do modelo."
        )
    elif metrics.mape > 30:
        recommendations.append(
            "MAPE acima do ideal. Sugestão: Verifique se há outliers nos dados históricos "
            "e considere usar intervalos de confiança mais conservadores (P85-P95)."
        )

    # Based on bias
    if metrics.bias_direction == 'overforecasting':
        recommendations.append(
            "Padrão de superestimativa detectado. Suas previsões tendem a ser otimistas demais. "
            "Considere usar percentis mais conservadores (P85 ou P95) para planejamento."
        )
    elif metrics.bias_direction == 'underforecasting':
        recommendations.append(
            "Padrão de subestimativa detectado. Suas previsões tendem a ser pessimistas. "
            "Isso pode indicar melhorias no processo ou dados históricos de período com baixa performance."
        )

    # Based on R²
    if metrics.r_squared < 0.5:
        recommendations.append(
            "Baixa correlação entre previsões e realidade (R²<0.5). "
            "Isso pode indicar que o modelo não está capturando bem as características do projeto. "
            "Revise: (1) Qualidade dos dados, (2) Quantidade de amostras, (3) Mudanças no processo."
        )

    # Based on accuracy rate
    if metrics.accuracy_rate < 50:
        recommendations.append(
            f"Apenas {metrics.accuracy_rate:.0f}% das previsões ficaram dentro da margem aceitável. "
            "Considere aumentar o número de simulações (para 50k+) ou usar margens de confiança mais amplas."
        )

    # Based on sample size
    if metrics.n_samples < 5:
        recommendations.append(
            f"Poucas comparações disponíveis ({metrics.n_samples}). "
            "Continue registrando resultados reais para melhorar a análise ao longo do tempo."
        )

    # Based on high-severity issues
    high_severity_issues = [i for i in issues if i['severity'] == 'high']
    if high_severity_issues:
        recommendations.append(
            f"⚠️ {len(high_severity_issues)} problemas críticos detectados nos dados. "
            "Resolva-os antes de confiar nas métricas de acurácia."
        )

    # Positive feedback
    if metrics.mape < 20 and metrics.accuracy_rate > 70:
        recommendations.append(
            "✓ Suas previsões estão com boa acurácia! Continue monitorando e ajustando conforme necessário."
        )

    return recommendations
