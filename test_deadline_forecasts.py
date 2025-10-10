"""
Test and demonstration of deadline analysis and forecast functions
"""

import sys
sys.path.insert(0, '.')

from monte_carlo_unified import (
    analyze_deadline,
    forecast_how_many,
    forecast_when
)

def test_deadline_analysis():
    """Test deadline analysis matching the example provided"""

    print("="*80)
    print("TESTE: ANÁLISE DE DEADLINE")
    print("="*80)

    # Dados do exemplo
    tp_samples = [10, 10, 10, 10, 10, 10, 10, 10]  # Throughput constante de 10
    backlog = 20
    start_date = "01/10/2025"
    deadline_date = "16/10/2025"

    # Executar análise
    result = analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"\nRESULTADOS DA SIMULAÇÃO")
    print(f"DEAD LINE:                       {result['deadline_date']}")
    print(f"Semanas para Dead Line:          {result['weeks_to_deadline']:.1f}")
    print(f"Semanas Projetadas (P85):        {result['projected_weeks_p85']:.1f}")
    print(f"")
    print(f"Trabalho a ser entregue (projetado) (P85): {result['projected_work_p85']}")
    print(f"")
    print(f"Tem chance de cumprir o Dead Line?  {'Sim' if result['can_meet_deadline'] else 'Não'}")
    print(f"")
    print(f"% que será cumprido do escopo:   {result['scope_completion_pct']}%")
    print(f"")
    print(f"% do prazo que será cumprido:    {result['deadline_completion_pct']}%")
    print("")

    return result


def test_how_many():
    """Test 'How many?' forecast - items in a time period"""

    print("="*80)
    print("TESTE: QUANTOS? (Throughput-based)")
    print("="*80)

    # Dados do exemplo
    tp_samples = [10, 10, 10, 10, 10, 10, 10, 10]  # Throughput constante de 10
    start_date = "01/10/2025"
    end_date = "16/10/2025"

    # Executar forecast
    result = forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=end_date,
        n_simulations=10000
    )

    print(f"\nQuantos?")
    print(f"Considerando que tenho um período de tempo, quantos itens de trabalho")
    print(f"provavelmente serão concluídos neste período?")
    print(f"")
    print(f"INÍCIO:              {result['start_date']}")
    print(f"FIM:                 {result['end_date']}")
    print(f"DIAS:                {result['days']}")
    print(f"SEMANAS:             {result['weeks']}")
    print(f"95% DE CONFIANÇA:    {result['items_p95']}")
    print(f"85% DE CONFIANÇA:    {result['items_p85']}")
    print(f"50% DE CONFIANÇA:    {result['items_p50']}")
    print("")

    return result


def test_when():
    """Test 'When?' forecast - completion date for backlog"""

    print("="*80)
    print("TESTE: QUANDO?")
    print("="*80)

    # Dados do exemplo
    tp_samples = [10, 10, 10, 10, 10, 10, 10, 10]  # Throughput constante de 10
    backlog = 20
    start_date = "01/10/25"

    # Executar forecast
    result = forecast_when(
        tp_samples=tp_samples,
        backlog=backlog,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"\nQuando?")
    print(f'"Dado que tenho um lote de trabalho, quando é provável que seja feito?"')
    print(f"")
    print(f"BACKLOG:             {result['backlog']}")
    print(f"INÍCIO:              {result['start_date']}")
    print(f"95% de confiança:    {result['date_p95']} ({result['weeks_p95']:.1f} semanas)")
    print(f"85% de confiança:    {result['date_p85']} ({result['weeks_p85']:.1f} semanas)")
    print(f"50% de confiança:    {result['date_p50']} ({result['weeks_p50']:.1f} semanas)")
    print("")

    return result


def test_realistic_scenario():
    """Test with more realistic variable throughput"""

    print("="*80)
    print("TESTE: CENÁRIO REALISTA (Throughput Variável)")
    print("="*80)

    # Throughput variável mais realista
    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]
    backlog = 50
    start_date = "01/10/2025"
    deadline_date = "01/12/2025"

    print(f"\nThroughput samples: {tp_samples}")
    print(f"Média: {sum(tp_samples)/len(tp_samples):.1f} items/semana")
    print(f"Backlog: {backlog} items")
    print("")

    # Análise de deadline
    deadline_result = analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"ANÁLISE DE DEADLINE:")
    print(f"  Dead Line:                    {deadline_result['deadline_date']}")
    print(f"  Semanas disponíveis:          {deadline_result['weeks_to_deadline']:.1f}")
    print(f"  Semanas necessárias (P85):    {deadline_result['projected_weeks_p85']:.1f}")
    print(f"  Consegue cumprir?             {'✓ Sim' if deadline_result['can_meet_deadline'] else '✗ Não'}")
    print(f"  % escopo completado:          {deadline_result['scope_completion_pct']}%")
    print("")

    # Quando?
    when_result = forecast_when(
        tp_samples=tp_samples,
        backlog=backlog,
        start_date=start_date,
        n_simulations=10000
    )

    print(f"QUANDO VAI TERMINAR?")
    print(f"  50% confiança (mediana):  {when_result['date_p50']}")
    print(f"  85% confiança:            {when_result['date_p85']}")
    print(f"  95% confiança:            {when_result['date_p95']}")
    print("")

    # Quantos em 2 meses?
    how_many_result = forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=deadline_date,
        n_simulations=10000
    )

    print(f"QUANTOS EM 2 MESES?")
    print(f"  Período: {how_many_result['weeks']} semanas")
    print(f"  50% confiança:    {how_many_result['items_p50']} items")
    print(f"  85% confiança:    {how_many_result['items_p85']} items")
    print(f"  95% confiança:    {how_many_result['items_p95']} items")
    print("")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "TESTES DE DEADLINE E FORECAST" + " "*29 + "║")
    print("╚" + "═"*78 + "╝")
    print("")

    # Teste 1: Análise de deadline (exemplo fornecido)
    test_deadline_analysis()

    # Teste 2: Quantos? (exemplo fornecido)
    test_how_many()

    # Teste 3: Quando? (exemplo fornecido)
    test_when()

    # Teste 4: Cenário realista
    test_realistic_scenario()

    print("="*80)
    print("✓ TODOS OS TESTES CONCLUÍDOS")
    print("="*80)
