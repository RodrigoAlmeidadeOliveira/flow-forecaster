"""
Process Behaviour Chart (PBC) Analyzer
Also known as XmR Charts (Individual and Moving Range Charts)

Este módulo implementa Process Behaviour Charts para validar a qualidade
e previsibilidade dos dados de throughput antes de usar em forecasting.

Baseado nos conceitos de Dr. Donald Wheeler e no artigo de Nick Brown
sobre validação de dados para forecasting.

Terminologia:
- X Chart: Individual values chart (valores de throughput)
- mR Chart: Moving Range chart (variação entre valores consecutivos)
- UNPL: Upper Natural Process Limit (limite superior do processo)
- LNL: Lower Natural Process Limit (limite inferior do processo)
- Process Signals: Indicadores de processo não-previsível
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class PBCResult:
    """
    Resultado da análise de Process Behaviour Chart.

    Attributes:
        data_points: Número de pontos de dados analisados
        average: Média dos valores (X̄)
        unpl: Upper Natural Process Limit
        lnl: Lower Natural Process Limit
        average_moving_range: Média dos moving ranges (mR̄)
        unpl_mr: Upper limit para moving range chart
        is_predictable: Se o processo é previsível (sem sinais)
        signals: Lista de sinais detectados
        points_beyond_limits: Pontos além dos limites
        run_signals: Sinais de runs detectados
        trend_signals: Sinais de trends detectados
        predictability_score: Score de previsibilidade (0-100)
        recommendation: Recomendação baseada na análise
    """
    data_points: int
    average: float
    unpl: float
    lnl: float
    average_moving_range: float
    unpl_mr: float
    is_predictable: bool
    signals: List[str]
    points_beyond_limits: List[Dict]
    run_signals: List[Dict]
    trend_signals: List[Dict]
    predictability_score: float
    recommendation: str

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'data_points': self.data_points,
            'average': round(self.average, 3),
            'unpl': round(self.unpl, 3),
            'lnl': round(self.lnl, 3),
            'average_moving_range': round(self.average_moving_range, 3),
            'unpl_mr': round(self.unpl_mr, 3),
            'is_predictable': self.is_predictable,
            'signals': self.signals,
            'points_beyond_limits': self.points_beyond_limits,
            'run_signals': self.run_signals,
            'trend_signals': self.trend_signals,
            'predictability_score': round(self.predictability_score, 2),
            'recommendation': self.recommendation,
            'interpretation': {
                'process_state': 'Predictable' if self.is_predictable else 'Unpredictable',
                'quality': self._get_quality_level(),
                'can_forecast': self.predictability_score >= 60
            }
        }

    def _get_quality_level(self) -> str:
        """Retorna nível de qualidade dos dados."""
        if self.predictability_score >= 90:
            return 'Excellent'
        elif self.predictability_score >= 75:
            return 'Good'
        elif self.predictability_score >= 60:
            return 'Fair'
        elif self.predictability_score >= 40:
            return 'Poor'
        else:
            return 'Very Poor'


class PBCAnalyzer:
    """
    Analisador de Process Behaviour Charts (XmR Charts).

    Implementa cálculo de limites naturais do processo e detecção de sinais
    de não-previsibilidade.
    """

    # Constantes de Wheeler para XmR charts
    UNPL_MULTIPLIER = 2.66  # Para Individual Chart (X)
    UNPL_MR_MULTIPLIER = 3.27  # Para Moving Range Chart (mR)

    def __init__(self, data: List[float]):
        """
        Inicializa o analisador com dados de throughput.

        Args:
            data: Lista de valores de throughput (ex: items/week)
        """
        if not data or len(data) < 2:
            raise ValueError("PBC requires at least 2 data points")

        self.data = np.array(data)
        self.n = len(data)

        # Cálculos básicos
        self.average = np.mean(self.data)
        self.moving_ranges = self._calculate_moving_ranges()
        self.average_mr = np.mean(self.moving_ranges)

        # Limites do processo
        self.unpl = self.average + (self.UNPL_MULTIPLIER * self.average_mr)
        self.lnl = max(0, self.average - (self.UNPL_MULTIPLIER * self.average_mr))
        self.unpl_mr = self.UNPL_MR_MULTIPLIER * self.average_mr

    def _calculate_moving_ranges(self) -> np.ndarray:
        """
        Calcula moving ranges (diferença absoluta entre pontos consecutivos).

        Returns:
            Array de moving ranges
        """
        mr = []
        for i in range(1, len(self.data)):
            mr.append(abs(self.data[i] - self.data[i-1]))
        return np.array(mr)

    def detect_points_beyond_limits(self) -> List[Dict]:
        """
        Detecta pontos além dos limites naturais (UNPL/LNL).

        Signal: Qualquer ponto além de UNPL ou abaixo de LNL indica
        processo não-previsível.

        Returns:
            Lista de pontos fora dos limites
        """
        beyond_limits = []

        for i, value in enumerate(self.data):
            if value > self.unpl:
                beyond_limits.append({
                    'index': i,
                    'value': float(value),
                    'type': 'above_unpl',
                    'limit': float(self.unpl),
                    'deviation': float(value - self.unpl)
                })
            elif value < self.lnl:
                beyond_limits.append({
                    'index': i,
                    'value': float(value),
                    'type': 'below_lnl',
                    'limit': float(self.lnl),
                    'deviation': float(self.lnl - value)
                })

        return beyond_limits

    def detect_runs(self, run_length: int = 8) -> List[Dict]:
        """
        Detecta runs (8+ pontos consecutivos no mesmo lado da média).

        Signal: 8 ou mais pontos consecutivos todos acima ou todos abaixo
        da média indicam mudança no processo.

        Args:
            run_length: Comprimento mínimo de run (default: 8)

        Returns:
            Lista de runs detectados
        """
        runs = []
        current_run_start = 0
        current_run_side = None
        current_run_length = 0

        for i, value in enumerate(self.data):
            side = 'above' if value > self.average else 'below'

            if side == current_run_side:
                current_run_length += 1
            else:
                # Check if previous run was long enough
                if current_run_length >= run_length:
                    runs.append({
                        'start_index': current_run_start,
                        'end_index': i - 1,
                        'length': current_run_length,
                        'side': current_run_side,
                        'type': 'run'
                    })

                # Start new run
                current_run_start = i
                current_run_side = side
                current_run_length = 1

        # Check final run
        if current_run_length >= run_length:
            runs.append({
                'start_index': current_run_start,
                'end_index': len(self.data) - 1,
                'length': current_run_length,
                'side': current_run_side,
                'type': 'run'
            })

        return runs

    def detect_trends(self, trend_length: int = 6) -> List[Dict]:
        """
        Detecta trends (6+ pontos consecutivos aumentando ou diminuindo).

        Signal: 6 ou mais pontos consecutivos todos aumentando ou todos
        diminuindo indicam drift no processo.

        Args:
            trend_length: Comprimento mínimo de trend (default: 6)

        Returns:
            Lista de trends detectados
        """
        trends = []

        if len(self.data) < trend_length:
            return trends

        current_trend_start = 0
        current_trend_direction = None
        current_trend_length = 1

        for i in range(1, len(self.data)):
            if self.data[i] > self.data[i-1]:
                direction = 'increasing'
            elif self.data[i] < self.data[i-1]:
                direction = 'decreasing'
            else:
                direction = 'flat'

            if direction == current_trend_direction and direction != 'flat':
                current_trend_length += 1
            else:
                # Check if previous trend was long enough
                if current_trend_length >= trend_length and current_trend_direction != 'flat':
                    trends.append({
                        'start_index': current_trend_start,
                        'end_index': i - 1,
                        'length': current_trend_length,
                        'direction': current_trend_direction,
                        'type': 'trend'
                    })

                # Start new trend
                current_trend_start = i - 1
                current_trend_direction = direction
                current_trend_length = 2 if direction != 'flat' else 1

        # Check final trend
        if current_trend_length >= trend_length and current_trend_direction != 'flat':
            trends.append({
                'start_index': current_trend_start,
                'end_index': len(self.data) - 1,
                'length': current_trend_length,
                'direction': current_trend_direction,
                'type': 'trend'
            })

        return trends

    def calculate_predictability_score(
        self,
        points_beyond: List[Dict],
        runs: List[Dict],
        trends: List[Dict]
    ) -> float:
        """
        Calcula score de previsibilidade (0-100).

        Score = 100 - (penalidades por sinais)

        Penalidades:
        - Ponto além dos limites: -15 pontos cada
        - Run detectado: -10 pontos cada
        - Trend detectado: -8 pontos cada

        Args:
            points_beyond: Pontos além dos limites
            runs: Runs detectados
            trends: Trends detectados

        Returns:
            Score de 0 a 100
        """
        score = 100.0

        # Penalidades
        score -= len(points_beyond) * 15  # Mais severo
        score -= len(runs) * 10
        score -= len(trends) * 8

        # Penalidade por poucos dados
        if self.n < 10:
            score -= 10
        elif self.n < 20:
            score -= 5

        # Score mínimo = 0
        return max(0.0, score)

    def generate_recommendation(
        self,
        is_predictable: bool,
        score: float,
        signals: List[str]
    ) -> str:
        """
        Gera recomendação baseada na análise.

        Args:
            is_predictable: Se o processo é previsível
            score: Score de previsibilidade
            signals: Sinais detectados

        Returns:
            Recomendação textual
        """
        if is_predictable and score >= 90:
            return (
                "✓ Excellent data quality. Process is highly predictable. "
                "Safe to use for forecasting with high confidence."
            )
        elif is_predictable and score >= 75:
            return (
                "✓ Good data quality. Process is predictable. "
                "Safe to use for forecasting."
            )
        elif score >= 60:
            return (
                "⚠️ Fair data quality. Process shows some variation but can be used "
                "for forecasting with caution. Monitor for process changes."
            )
        elif score >= 40:
            return (
                "⚠️ Poor data quality. Process shows significant variation. "
                "Forecasts may be unreliable. Consider: (1) Collecting more data, "
                "(2) Investigating special causes, (3) Using wider confidence intervals."
            )
        else:
            return (
                "❌ Very poor data quality. Process is unpredictable. "
                "DO NOT use for forecasting until process stabilizes. "
                f"Detected signals: {', '.join(signals[:3])}. "
                "Investigate and remove special causes before forecasting."
            )

    def analyze(self) -> PBCResult:
        """
        Executa análise completa de Process Behaviour Chart.

        Returns:
            Objeto PBCResult com todos os resultados
        """
        # Detecta sinais
        points_beyond = self.detect_points_beyond_limits()
        runs = self.detect_runs()
        trends = self.detect_trends()

        # Lista de sinais em texto
        signals = []

        if points_beyond:
            signals.append(
                f"{len(points_beyond)} point(s) beyond limits "
                f"(UNPL={self.unpl:.2f}, LNL={self.lnl:.2f})"
            )

        if runs:
            for run in runs:
                signals.append(
                    f"Run of {run['length']} points {run['side']} average "
                    f"(indices {run['start_index']}-{run['end_index']})"
                )

        if trends:
            for trend in trends:
                signals.append(
                    f"Trend of {trend['length']} points {trend['direction']} "
                    f"(indices {trend['start_index']}-{trend['end_index']})"
                )

        # Processo é previsível se não há sinais
        is_predictable = len(points_beyond) == 0 and len(runs) == 0 and len(trends) == 0

        # Calcula score
        score = self.calculate_predictability_score(points_beyond, runs, trends)

        # Gera recomendação
        recommendation = self.generate_recommendation(is_predictable, score, signals)

        return PBCResult(
            data_points=self.n,
            average=float(self.average),
            unpl=float(self.unpl),
            lnl=float(self.lnl),
            average_moving_range=float(self.average_mr),
            unpl_mr=float(self.unpl_mr),
            is_predictable=is_predictable,
            signals=signals,
            points_beyond_limits=points_beyond,
            run_signals=runs,
            trend_signals=trends,
            predictability_score=score,
            recommendation=recommendation
        )

    def get_chart_data(self) -> Dict:
        """
        Retorna dados formatados para visualização de charts.

        Returns:
            Dicionário com dados para X chart e mR chart
        """
        return {
            'x_chart': {
                'values': [float(x) for x in self.data],
                'average': float(self.average),
                'unpl': float(self.unpl),
                'lnl': float(self.lnl),
                'indices': list(range(len(self.data)))
            },
            'mr_chart': {
                'values': [float(mr) for mr in self.moving_ranges],
                'average': float(self.average_mr),
                'unpl': float(self.unpl_mr),
                'lnl': 0.0,  # LNL for mR is always 0
                'indices': list(range(1, len(self.data)))
            }
        }


def analyze_throughput_predictability(throughput_samples: List[float]) -> Dict:
    """
    Função helper para análise rápida de previsibilidade de throughput.

    Args:
        throughput_samples: Lista de valores de throughput

    Returns:
        Dicionário com análise completa e dados para charts
    """
    analyzer = PBCAnalyzer(throughput_samples)
    result = analyzer.analyze()
    chart_data = analyzer.get_chart_data()

    return {
        'analysis': result.to_dict(),
        'chart_data': chart_data,
        'raw_data': {
            'throughput_samples': throughput_samples,
            'n_samples': len(throughput_samples)
        }
    }


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo 1: Processo previsível (estável)
    print("=" * 80)
    print("EXEMPLO 1: Processo Previsível (Estável)")
    print("=" * 80)

    stable_data = [3.0, 2.8, 3.2, 2.9, 3.1, 3.0, 2.7, 3.3, 2.8, 3.0,
                   3.1, 2.9, 3.0, 3.2, 2.8, 3.1, 2.9, 3.0, 3.2, 2.8]

    analyzer1 = PBCAnalyzer(stable_data)
    result1 = analyzer1.analyze()

    print(f"\nData points: {result1.data_points}")
    print(f"Average: {result1.average:.2f}")
    print(f"UNPL: {result1.unpl:.2f}")
    print(f"LNL: {result1.lnl:.2f}")
    print(f"Is Predictable: {result1.is_predictable}")
    print(f"Predictability Score: {result1.predictability_score:.1f}/100")
    print(f"\nRecommendation: {result1.recommendation}")

    # Exemplo 2: Processo não-previsível (com outliers)
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Processo Não-Previsível (Com Outliers)")
    print("=" * 80)

    unstable_data = [3.0, 2.8, 3.2, 8.5, 3.1, 3.0, 2.7, 3.3, 0.5, 3.0,
                     3.1, 2.9, 7.2, 3.2, 2.8, 3.1, 2.9, 3.0, 3.2, 2.8]

    analyzer2 = PBCAnalyzer(unstable_data)
    result2 = analyzer2.analyze()

    print(f"\nData points: {result2.data_points}")
    print(f"Average: {result2.average:.2f}")
    print(f"UNPL: {result2.unpl:.2f}")
    print(f"LNL: {result2.lnl:.2f}")
    print(f"Is Predictable: {result2.is_predictable}")
    print(f"Predictability Score: {result2.predictability_score:.1f}/100")
    print(f"\nSignals detected: {len(result2.signals)}")
    for i, signal in enumerate(result2.signals, 1):
        print(f"  {i}. {signal}")
    print(f"\nRecommendation: {result2.recommendation}")

    # Exporta resultado para JSON
    print("\n" + "=" * 80)
    print("JSON Output:")
    print("=" * 80)
    print(json.dumps(result2.to_dict(), indent=2))
