"""
Exemplo de uso das funções de análise de deadline
Demonstra os três tipos de análise:
1. Análise de Deadline - Posso cumprir o prazo?
2. Quantos? - Quantos items posso entregar no período?
3. Quando? - Quando vou terminar o backlog?
"""

import sys
sys.path.insert(0, '.')

from monte_carlo_unified import (
    analyze_deadline,
    forecast_how_many,
    forecast_when
)

def example_deadline_analysis():
    """
    Exemplo: Análise de Deadline

    Cenário:
    - Throughput histórico variável (média ~6 items/semana)
    - Backlog de 20 items
    - Deadline: 16/10/2025
    - Início: 01/10/2025
    """

    print("="*80)
    print("EXEMPLO 1: ANÁLISE DE DEADLINE")
    print("="*80)
    print()

    # Throughput histórico (items por semana)
    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]  # Média ~5.8/semana

    # Configuração
    backlog = 20  # items para entregar
    start_date = "01/10/2025"
    deadline_date = "16/10/2025"  # 15 dias = ~2 semanas

    print(f"Throughput histórico (items/semana): {tp_samples}")
    print(f"Média: {sum(tp_samples)/len(tp_samples):.1f} items/semana")
    print(f"Backlog: {backlog} items")
    print(f"Início: {start_date}")
    print(f"Deadline: {deadline_date}")
    print()

    # Executar análise
    result = analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    # Exibir resultados formatados
    print("─" * 80)
    print("RESULTADOS DA SIMULAÇÃO")
    print("─" * 80)
    print(f"DEAD LINE                                    {result['deadline_date']}")
    print(f"Semanas para Dead Line                       {result['weeks_to_deadline']:.1f}")
    print(f"Semanas Projetadas (P85)                     {result['projected_weeks_p85']:.1f}")
    print()
    print(f"Trabalho a ser entregue (projetado) (P85)    {result['projected_work_p85']}")
    print()
    print(f"Tem chance de cumprir o Dead Line?           {'Sim' if result['can_meet_deadline'] else 'Não'}")
    print()
    print(f"% que será cumprido do escopo                {result['scope_completion_pct']}%")
    print()
    print(f"% do prazo que será cumprido                 {result['deadline_completion_pct']}%")
    print()


def example_how_many():
    """
    Exemplo: Quantos?

    Pergunta: "Dado um período de tempo, quantos items serão entregues?"
    """

    print("="*80)
    print("EXEMPLO 2: QUANTOS?")
    print("="*80)
    print()

    # Throughput histórico
    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]

    # Período de análise
    start_date = "01/10/2025"
    end_date = "16/10/2025"

    print("Considerando que tenho um período de tempo, quantos itens de trabalho")
    print("provavelmente serão concluídos neste período?")
    print()

    # Executar forecast
    result = forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=end_date,
        n_simulations=10000
    )

    # Exibir resultados formatados
    print("─" * 80)
    print("RESPOSTAS BASEADAS NO THROUGHPUT")
    print("─" * 80)
    print(f"INÍCIO                           {start_date}")
    print(f"FIM                              {end_date}")
    print(f"DIAS                             {result['days']}")
    print(f"SEMANAS                          {result['weeks']}")
    print()
    print(f"95% DE CONFIANÇA                 {result['items_p95']}")
    print(f"85% DE CONFIANÇA                 {result['items_p85']}")
    print(f"50% DE CONFIANÇA                 {result['items_p50']}")
    print()


def example_when():
    """
    Exemplo: Quando?

    Pergunta: "Dado um backlog, quando será concluído?"
    """

    print("="*80)
    print("EXEMPLO 3: QUANDO?")
    print("="*80)
    print()

    # Throughput histórico
    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]

    # Configuração
    backlog = 20
    start_date = "01/10/25"

    print('"Dado que tenho um lote de trabalho, quando é provável que seja feito?"')
    print()

    # Executar forecast
    result = forecast_when(
        tp_samples=tp_samples,
        backlog=backlog,
        start_date=start_date,
        n_simulations=10000
    )

    # Exibir resultados formatados
    print("─" * 80)
    print("PREVISÃO DE CONCLUSÃO")
    print("─" * 80)
    print(f"BACKLOG                          {result['backlog']}")
    print(f"INÍCIO                           {result['start_date']}")
    print()
    print(f"95% de confiança                 {result['date_p95']}")
    print(f"85% de confiança                 {result['date_p85']}")
    print(f"50% de confiança                 {result['date_p50']}")
    print()


def example_complete_scenario():
    """
    Exemplo completo: Análise de um projeto real
    """

    print("="*80)
    print("EXEMPLO 4: CENÁRIO COMPLETO - PROJETO REAL")
    print("="*80)
    print()

    # Dados reais de throughput (últimas 12 semanas)
    tp_samples = [3, 5, 4, 6, 5, 7, 4, 5, 6, 5, 4, 6]

    # Projeto
    backlog = 30
    start_date = "01/11/2025"
    deadline_date = "20/12/2025"  # 7 semanas

    print("CONTEXTO DO PROJETO:")
    print(f"  Throughput médio: {sum(tp_samples)/len(tp_samples):.1f} items/semana")
    print(f"  Backlog total: {backlog} items")
    print(f"  Início: {start_date}")
    print(f"  Deadline: {deadline_date}")
    print()

    # 1. Análise de Deadline
    print("┌" + "─"*78 + "┐")
    print("│ 1. ANÁLISE DE DEADLINE                                                     │")
    print("└" + "─"*78 + "┘")

    deadline_result = analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"  Semanas disponíveis:          {deadline_result['weeks_to_deadline']:.1f}")
    print(f"  Semanas necessárias (P85):    {deadline_result['projected_weeks_p85']:.1f}")
    print(f"  Status:                       {'✓ Viável' if deadline_result['can_meet_deadline'] else '✗ Em risco'}")
    print(f"  % do escopo entregue:         {deadline_result['scope_completion_pct']}%")
    print()

    # 2. Quantos items até o deadline?
    print("┌" + "─"*78 + "┐")
    print("│ 2. QUANTOS ITEMS ATÉ O DEADLINE?                                           │")
    print("└" + "─"*78 + "┘")

    how_many_result = forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=deadline_date,
        n_simulations=10000
    )

    print(f"  Período: {how_many_result['weeks']} semanas")
    print(f"  Items esperados (P50):        {how_many_result['items_p50']}")
    print(f"  Items conservador (P85):      {how_many_result['items_p85']}")
    print(f"  Items otimista (P95):         {how_many_result['items_p95']}")
    print()

    # 3. Quando terminará?
    print("┌" + "─"*78 + "┐")
    print("│ 3. QUANDO O BACKLOG ESTARÁ COMPLETO?                                       │")
    print("└" + "─"*78 + "┘")

    when_result = forecast_when(
        tp_samples=tp_samples,
        backlog=backlog,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"  Data provável (P50):          {when_result['date_p50']}")
    print(f"  Data conservadora (P85):      {when_result['date_p85']}")
    print(f"  Data pessimista (P95):        {when_result['date_p95']}")
    print()

    # 4. Recomendação
    print("┌" + "─"*78 + "┐")
    print("│ 4. RECOMENDAÇÃO                                                            │")
    print("└" + "─"*78 + "┘")

    if deadline_result['can_meet_deadline']:
        print("  ✓ O deadline pode ser cumprido com 85% de confiança.")
        print(f"  ✓ Espera-se entregar {how_many_result['items_p85']} items até {deadline_date}.")
    else:
        print("  ✗ O deadline está em risco!")
        print(f"  ✗ Apenas {deadline_result['scope_completion_pct']}% do escopo será entregue.")
        print(f"  → Sugestão: Reduzir escopo para {how_many_result['items_p85']} items")
        print(f"  → Ou estender deadline para {when_result['date_p85']}")
    print()


if __name__ == "__main__":
    print()
    print("╔" + "═"*78 + "╗")
    print("║" + " "*18 + "ANÁLISES DE DEADLINE E FORECAST - MONTE CARLO" + " "*15 + "║")
    print("╚" + "═"*78 + "╝")
    print()

    # Exemplo 1: Análise de deadline
    example_deadline_analysis()

    print()

    # Exemplo 2: Quantos?
    example_how_many()

    print()

    # Exemplo 3: Quando?
    example_when()

    print()

    # Exemplo 4: Cenário completo
    example_complete_scenario()

    print("="*80)
    print("✓ EXEMPLOS CONCLUÍDOS")
    print("="*80)
    print()
    print("PRÓXIMOS PASSOS:")
    print("  1. Use analyze_deadline() para verificar viabilidade de deadlines")
    print("  2. Use forecast_how_many() para estimar entregas em um período")
    print("  3. Use forecast_when() para prever datas de conclusão")
    print()
