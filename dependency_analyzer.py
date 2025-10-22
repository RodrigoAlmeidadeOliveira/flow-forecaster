"""
Dependency Analyzer for Project Forecasting

Este módulo implementa a análise de impacto de dependências entre projetos e demandas
no forecasting de entregas, baseado no modelo probabilístico de 2^n.

Fundamento Teórico:
- Para cada dependência (n), a probabilidade de todas serem entregues no prazo é 1/2^n
- Isso significa que a probabilidade de PELO MENOS UMA estar atrasada é (2^n - 1)/2^n
- Cada dependência removida DOBRA as chances de sucesso na entrega no prazo

Exemplo:
- 0 dependências: 100% de chance (1/1)
- 1 dependência: 50% de chance (1/2)
- 2 dependências: 25% de chance (1/4)
- 3 dependências: 12.5% de chance (1/8)
- 7 dependências: 0.78% de chance (1/128)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class Dependency:
    """
    Representa uma dependência entre projetos/demandas.

    Attributes:
        id: Identificador único da dependência
        name: Nome descritivo da dependência
        source_project: Projeto que depende (bloqueado)
        target_project: Projeto do qual depende (bloqueador)
        on_time_probability: Probabilidade da dependência ser entregue no prazo (0-1)
        delay_impact_days: Impacto em dias caso a dependência atrase
        delay_impact_distribution: Distribuição do impacto (para Monte Carlo)
        criticality: Nível de criticidade ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    """
    id: str
    name: str
    source_project: str
    target_project: str
    on_time_probability: float = 0.5  # Default: 50% chance de estar no prazo
    delay_impact_days: float = 0.0
    delay_impact_distribution: Optional[List[float]] = None
    criticality: str = 'MEDIUM'

    def __post_init__(self):
        """Valida os dados após inicialização."""
        if not 0 <= self.on_time_probability <= 1:
            raise ValueError(f"on_time_probability deve estar entre 0 e 1, recebido: {self.on_time_probability}")

        if self.criticality not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            raise ValueError(f"criticality deve ser LOW, MEDIUM, HIGH ou CRITICAL, recebido: {self.criticality}")


@dataclass
class DependencyAnalysisResult:
    """
    Resultado da análise de dependências.

    Attributes:
        total_dependencies: Número total de dependências
        on_time_probability: Probabilidade de todas as dependências estarem no prazo
        at_least_one_delayed_probability: Probabilidade de pelo menos uma estar atrasada
        expected_delay_days: Atraso esperado em dias (média ponderada)
        delay_percentiles: Percentis de atraso (p10, p50, p90, etc.)
        critical_path: Lista de dependências no caminho crítico
        risk_score: Score de risco (0-100)
        risk_level: Nível de risco ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        recommendations: Lista de recomendações
    """
    total_dependencies: int
    on_time_probability: float
    at_least_one_delayed_probability: float
    expected_delay_days: float
    delay_percentiles: Dict[str, float]
    critical_path: List[str]
    risk_score: float
    risk_level: str
    recommendations: List[str]

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            'total_dependencies': self.total_dependencies,
            'on_time_probability': self.on_time_probability,
            'on_time_probability_percentage': round(self.on_time_probability * 100, 2),
            'at_least_one_delayed_probability': self.at_least_one_delayed_probability,
            'at_least_one_delayed_probability_percentage': round(self.at_least_one_delayed_probability * 100, 2),
            'odds_ratio': f"1 in {int(1/self.on_time_probability)}" if self.on_time_probability > 0 else "0",
            'expected_delay_days': round(self.expected_delay_days, 2),
            'delay_percentiles': {k: round(v, 2) for k, v in self.delay_percentiles.items()},
            'critical_path': self.critical_path,
            'risk_score': round(self.risk_score, 2),
            'risk_level': self.risk_level,
            'recommendations': self.recommendations
        }


class DependencyAnalyzer:
    """
    Analisador de impacto de dependências para forecasting de projetos.

    Implementa o modelo probabilístico 2^n e simulação Monte Carlo para
    estimar o impacto de dependências entre projetos nas previsões de entrega.
    """

    def __init__(self, dependencies: List[Dependency]):
        """
        Inicializa o analisador com uma lista de dependências.

        Args:
            dependencies: Lista de objetos Dependency
        """
        self.dependencies = dependencies
        self.dependency_graph = self._build_dependency_graph()

    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Constrói um grafo de dependências.

        Returns:
            Dicionário mapeando projeto -> lista de projetos dos quais depende
        """
        graph = {}
        for dep in self.dependencies:
            if dep.source_project not in graph:
                graph[dep.source_project] = []
            graph[dep.source_project].append(dep.target_project)
        return graph

    def calculate_on_time_probability(
        self,
        use_individual_probabilities: bool = True
    ) -> Tuple[float, float]:
        """
        Calcula a probabilidade de entrega no prazo considerando dependências.

        Args:
            use_individual_probabilities: Se True, usa probabilidades individuais de cada dependência.
                                         Se False, assume 50% para todas (modelo simplificado 2^n).

        Returns:
            Tupla (probabilidade de todas no prazo, probabilidade de pelo menos uma atrasada)
        """
        if len(self.dependencies) == 0:
            return 1.0, 0.0

        if use_individual_probabilities:
            # Modelo sofisticado: considera probabilidades individuais
            # P(todas no prazo) = P(dep1) * P(dep2) * ... * P(depN)
            on_time_prob = 1.0
            for dep in self.dependencies:
                on_time_prob *= dep.on_time_probability
        else:
            # Modelo simplificado: assume 50% para todas
            # P(todas no prazo) = 0.5^n = 1/2^n
            n = len(self.dependencies)
            on_time_prob = 0.5 ** n

        at_least_one_delayed = 1.0 - on_time_prob

        return on_time_prob, at_least_one_delayed

    def simulate_dependency_delays(
        self,
        num_simulations: int = 10000
    ) -> Dict[str, any]:
        """
        Simula os atrasos causados por dependências usando Monte Carlo.

        Args:
            num_simulations: Número de simulações a executar

        Returns:
            Dicionário com resultados da simulação:
            - simulated_delays: Array de atrasos simulados
            - on_time_count: Número de simulações sem atraso
            - delayed_count: Número de simulações com atraso
            - percentiles: Percentis dos atrasos
        """
        simulated_delays = []
        on_time_count = 0
        delayed_count = 0

        for _ in range(num_simulations):
            total_delay = 0.0

            for dep in self.dependencies:
                # Simula se esta dependência atrasa
                is_on_time = np.random.random() < dep.on_time_probability

                if not is_on_time:
                    # Dependência atrasada - calcular impacto
                    if dep.delay_impact_distribution and len(dep.delay_impact_distribution) > 0:
                        # Usa distribuição fornecida
                        delay = np.random.choice(dep.delay_impact_distribution)
                    elif dep.delay_impact_days > 0:
                        # Usa valor fixo com variação (± 30%)
                        delay = np.random.uniform(
                            dep.delay_impact_days * 0.7,
                            dep.delay_impact_days * 1.3
                        )
                    else:
                        # Atraso padrão de 5-15 dias
                        delay = np.random.uniform(5, 15)

                    total_delay += delay

            simulated_delays.append(total_delay)

            if total_delay == 0:
                on_time_count += 1
            else:
                delayed_count += 1

        simulated_delays = np.array(simulated_delays)

        # Calcula percentis dos atrasos (apenas nos casos com atraso)
        delays_only = simulated_delays[simulated_delays > 0]

        percentiles = {}
        if len(delays_only) > 0:
            percentiles = {
                'p10': np.percentile(delays_only, 10),
                'p25': np.percentile(delays_only, 25),
                'p50': np.percentile(delays_only, 50),
                'p75': np.percentile(delays_only, 75),
                'p85': np.percentile(delays_only, 85),
                'p90': np.percentile(delays_only, 90),
                'p95': np.percentile(delays_only, 95)
            }
        else:
            percentiles = {p: 0.0 for p in ['p10', 'p25', 'p50', 'p75', 'p85', 'p90', 'p95']}

        return {
            'simulated_delays': simulated_delays,
            'on_time_count': on_time_count,
            'delayed_count': delayed_count,
            'on_time_probability': on_time_count / num_simulations,
            'delayed_probability': delayed_count / num_simulations,
            'mean_delay': np.mean(simulated_delays),
            'median_delay': np.median(simulated_delays),
            'std_delay': np.std(simulated_delays),
            'percentiles': percentiles
        }

    def find_critical_path(self) -> List[str]:
        """
        Identifica o caminho crítico de dependências.

        Returns:
            Lista de IDs das dependências no caminho crítico (maior impacto esperado)
        """
        # Calcula score de criticidade para cada dependência
        # Score = (1 - on_time_probability) * delay_impact_days * criticality_weight

        criticality_weights = {
            'LOW': 0.5,
            'MEDIUM': 1.0,
            'HIGH': 2.0,
            'CRITICAL': 3.0
        }

        scored_dependencies = []

        for dep in self.dependencies:
            delay_impact = dep.delay_impact_days if dep.delay_impact_days > 0 else 10.0  # Default 10 dias
            criticality_weight = criticality_weights.get(dep.criticality, 1.0)

            score = (1 - dep.on_time_probability) * delay_impact * criticality_weight
            scored_dependencies.append((dep.id, score, dep.name))

        # Ordena por score (maior primeiro)
        scored_dependencies.sort(key=lambda x: x[1], reverse=True)

        # Retorna IDs e nomes das dependências críticas
        return [f"{dep_id} ({name})" for dep_id, score, name in scored_dependencies[:5]]  # Top 5

    def calculate_risk_score(
        self,
        simulation_results: Dict[str, any]
    ) -> Tuple[float, str]:
        """
        Calcula um score de risco (0-100) e nível de risco.

        Args:
            simulation_results: Resultados da simulação Monte Carlo

        Returns:
            Tupla (risk_score, risk_level)
        """
        # Componentes do score:
        # 1. Probabilidade de atraso (peso 40%)
        # 2. Impacto médio do atraso (peso 30%)
        # 3. Variabilidade (desvio padrão) (peso 20%)
        # 4. Número de dependências (peso 10%)

        delayed_prob = simulation_results['delayed_probability']
        mean_delay = simulation_results['mean_delay']
        std_delay = simulation_results['std_delay']
        num_deps = len(self.dependencies)

        # Normaliza cada componente para 0-100
        prob_score = delayed_prob * 100

        # Impacto: considera até 30 dias como máximo (100 pontos)
        impact_score = min((mean_delay / 30) * 100, 100)

        # Variabilidade: CV (coeficiente de variação) até 1.0 como máximo
        cv = (std_delay / mean_delay) if mean_delay > 0 else 0
        variability_score = min(cv * 100, 100)

        # Número de dependências: até 10 como máximo
        deps_score = min((num_deps / 10) * 100, 100)

        # Score ponderado
        risk_score = (
            prob_score * 0.4 +
            impact_score * 0.3 +
            variability_score * 0.2 +
            deps_score * 0.1
        )

        # Define nível de risco
        if risk_score < 25:
            risk_level = 'LOW'
        elif risk_score < 50:
            risk_level = 'MEDIUM'
        elif risk_score < 75:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'

        return risk_score, risk_level

    def generate_recommendations(
        self,
        risk_score: float,
        on_time_prob: float,
        simulation_results: Dict[str, any]
    ) -> List[str]:
        """
        Gera recomendações baseadas na análise de dependências.

        Args:
            risk_score: Score de risco calculado
            on_time_prob: Probabilidade de entrega no prazo
            simulation_results: Resultados da simulação

        Returns:
            Lista de recomendações
        """
        recommendations = []

        # Recomendação baseada na probabilidade
        if on_time_prob < 0.1:
            recommendations.append(
                f"⚠️ CRÍTICO: Probabilidade de entrega no prazo muito baixa ({on_time_prob*100:.1f}%). "
                "Considere replanejar o projeto ou remover dependências."
            )
        elif on_time_prob < 0.3:
            recommendations.append(
                f"⚠️ Probabilidade de entrega no prazo baixa ({on_time_prob*100:.1f}%). "
                "Recomenda-se revisar as dependências críticas e criar planos de contingência."
            )
        elif on_time_prob < 0.6:
            recommendations.append(
                f"ℹ️ Probabilidade moderada de entrega no prazo ({on_time_prob*100:.1f}%). "
                "Monitore de perto as dependências do caminho crítico."
            )
        else:
            recommendations.append(
                f"✓ Boa probabilidade de entrega no prazo ({on_time_prob*100:.1f}%)."
            )

        # Recomendação baseada no número de dependências
        num_deps = len(self.dependencies)
        if num_deps >= 7:
            recommendations.append(
                f"Número alto de dependências ({num_deps}). Cada dependência removida DOBRA suas chances de sucesso. "
                "Priorize a remoção de dependências não-críticas."
            )
        elif num_deps >= 4:
            recommendations.append(
                f"Número moderado de dependências ({num_deps}). Considere possibilidades de paralelização."
            )

        # Recomendação baseada no impacto
        mean_delay = simulation_results['mean_delay']
        if mean_delay > 20:
            recommendations.append(
                f"Impacto médio de atraso significativo ({mean_delay:.1f} dias). "
                "Adicione buffer no planejamento e considere começar dependências antecipadamente."
            )
        elif mean_delay > 10:
            recommendations.append(
                f"Impacto médio de atraso moderado ({mean_delay:.1f} dias). "
                "Recomenda-se adicionar margem de segurança no cronograma."
            )

        # Recomendação baseada na variabilidade
        cv = (simulation_results['std_delay'] / mean_delay) if mean_delay > 0 else 0
        if cv > 0.5:
            recommendations.append(
                "Alta variabilidade nos atrasos. Crie múltiplos cenários de contingência e monitore frequentemente."
            )

        # Recomendação sobre uso de Monte Carlo
        if risk_score > 50:
            recommendations.append(
                "Recomenda-se usar simulação Monte Carlo com análise de dependências para previsões mais precisas."
            )

        return recommendations

    def analyze(
        self,
        num_simulations: int = 10000,
        use_individual_probabilities: bool = True
    ) -> DependencyAnalysisResult:
        """
        Executa análise completa de dependências.

        Args:
            num_simulations: Número de simulações Monte Carlo
            use_individual_probabilities: Se deve usar probabilidades individuais

        Returns:
            Objeto DependencyAnalysisResult com resultados completos
        """
        # 1. Calcula probabilidades teóricas
        on_time_prob, at_least_one_delayed = self.calculate_on_time_probability(
            use_individual_probabilities
        )

        # 2. Simula atrasos
        simulation_results = self.simulate_dependency_delays(num_simulations)

        # 3. Identifica caminho crítico
        critical_path = self.find_critical_path()

        # 4. Calcula score de risco
        risk_score, risk_level = self.calculate_risk_score(simulation_results)

        # 5. Gera recomendações
        recommendations = self.generate_recommendations(
            risk_score,
            on_time_prob,
            simulation_results
        )

        return DependencyAnalysisResult(
            total_dependencies=len(self.dependencies),
            on_time_probability=on_time_prob,
            at_least_one_delayed_probability=at_least_one_delayed,
            expected_delay_days=simulation_results['mean_delay'],
            delay_percentiles=simulation_results['percentiles'],
            critical_path=critical_path,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations
        )


def create_dependencies_from_dict(dependencies_data: List[Dict]) -> List[Dependency]:
    """
    Cria lista de objetos Dependency a partir de dados em formato dict.

    Args:
        dependencies_data: Lista de dicionários com dados de dependências

    Returns:
        Lista de objetos Dependency
    """
    dependencies = []

    for dep_data in dependencies_data:
        dep = Dependency(
            id=dep_data.get('id', ''),
            name=dep_data.get('name', ''),
            source_project=dep_data.get('source_project', ''),
            target_project=dep_data.get('target_project', ''),
            on_time_probability=dep_data.get('on_time_probability', 0.5),
            delay_impact_days=dep_data.get('delay_impact_days', 0.0),
            delay_impact_distribution=dep_data.get('delay_impact_distribution'),
            criticality=dep_data.get('criticality', 'MEDIUM')
        )
        dependencies.append(dep)

    return dependencies


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo com 7 dependências (caso do artigo)
    example_dependencies = [
        Dependency(
            id="DEP-001",
            name="API Authentication Service",
            source_project="Mobile App",
            target_project="Backend Team",
            on_time_probability=0.6,
            delay_impact_days=10,
            criticality='HIGH'
        ),
        Dependency(
            id="DEP-002",
            name="Database Schema Updates",
            source_project="Mobile App",
            target_project="DBA Team",
            on_time_probability=0.7,
            delay_impact_days=5,
            criticality='MEDIUM'
        ),
        Dependency(
            id="DEP-003",
            name="Payment Gateway Integration",
            source_project="Mobile App",
            target_project="External Vendor",
            on_time_probability=0.4,
            delay_impact_days=15,
            criticality='CRITICAL'
        ),
        Dependency(
            id="DEP-004",
            name="UI Design Approval",
            source_project="Mobile App",
            target_project="Design Team",
            on_time_probability=0.8,
            delay_impact_days=3,
            criticality='LOW'
        ),
        Dependency(
            id="DEP-005",
            name="Security Audit",
            source_project="Mobile App",
            target_project="Security Team",
            on_time_probability=0.5,
            delay_impact_days=12,
            criticality='HIGH'
        ),
        Dependency(
            id="DEP-006",
            name="Infrastructure Provisioning",
            source_project="Mobile App",
            target_project="DevOps Team",
            on_time_probability=0.6,
            delay_impact_days=8,
            criticality='HIGH'
        ),
        Dependency(
            id="DEP-007",
            name="Legal Compliance Review",
            source_project="Mobile App",
            target_project="Legal Team",
            on_time_probability=0.5,
            delay_impact_days=20,
            criticality='CRITICAL'
        )
    ]

    # Cria analisador
    analyzer = DependencyAnalyzer(example_dependencies)

    # Executa análise
    result = analyzer.analyze(num_simulations=10000)

    # Exibe resultados
    print("=" * 80)
    print("ANÁLISE DE IMPACTO DE DEPENDÊNCIAS")
    print("=" * 80)
    print(f"\nNúmero total de dependências: {result.total_dependencies}")
    print(f"Probabilidade de entrega no prazo: {result.on_time_probability*100:.2f}%")
    print(f"  -> Odds: 1 em {int(1/result.on_time_probability)}")
    print(f"\nProbabilidade de PELO MENOS UMA dependência atrasar: {result.at_least_one_delayed_probability*100:.2f}%")
    print(f"  -> {int(1/result.on_time_probability) - 1} vezes MAIS provável que atrasar vs. não atrasar")
    print(f"\nAtraso esperado (se houver atraso): {result.expected_delay_days:.1f} dias")

    print("\nPercentis de atraso:")
    for p, value in result.delay_percentiles.items():
        print(f"  {p}: {value:.1f} dias")

    print(f"\nScore de risco: {result.risk_score:.1f}/100")
    print(f"Nível de risco: {result.risk_level}")

    print("\nCaminho crítico (top 5 dependências):")
    for i, dep in enumerate(result.critical_path, 1):
        print(f"  {i}. {dep}")

    print("\nRecomendações:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 80)

    # Exporta para JSON
    result_dict = result.to_dict()
    print("\nResultado em JSON:")
    print(json.dumps(result_dict, indent=2))
