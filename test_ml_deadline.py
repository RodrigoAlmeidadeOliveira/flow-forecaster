"""
Test ML Deadline Analysis with Team Dynamics
Demonstrates ML forecasting with S-curve, team size, split rates, and lead times
"""

import sys
sys.path.insert(0, '.')

from ml_deadline_forecaster import (
    ml_analyze_deadline,
    ml_forecast_how_many,
    ml_forecast_when
)


def test_ml_simple_scenario():
    """Test ML with simple scenario (no team dynamics)"""

    print("="*80)
    print("TESTE 1: ML SIMPLES (Sem dinâmica de equipe)")
    print("="*80)
    print()

    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]
    backlog = 20
    start_date = "01/10/2025"
    deadline_date = "16/10/2025"

    print(f"Throughput histórico: {tp_samples}")
    print(f"Média: {sum(tp_samples)/len(tp_samples):.1f} items/semana")
    print(f"Backlog: {backlog} items")
    print(f"Deadline: {deadline_date}")
    print()

    result = ml_analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        team_size=1,  # Equipe simples
        n_simulations=1000
    )

    print("RESULTADOS ML (Simples)")
    print("─" * 80)
    print(f"Deadline:                        {result['deadline_date']}")
    print(f"Semanas até deadline:            {result['weeks_to_deadline']:.1f}")
    print(f"Semanas projetadas (P85):        {result['projected_weeks_p85']:.1f}")
    print(f"Trabalho entregue (P85):         {result['projected_work_p85']}")
    print(f"Pode cumprir deadline?           {'Sim' if result['can_meet_deadline'] else 'Não'}")
    print(f"% escopo completado:             {result['scope_completion_pct']}%")
    print()
    print("Modelos ML usados:")
    for model in result['ml_models']:
        print(f"  - {model['model']}: MAE = {model['mae']:.2f}, RMSE = {model['rmse']:.2f}")
    print()


def test_ml_with_team_dynamics():
    """Test ML with team S-curve"""

    print("="*80)
    print("TESTE 2: ML COM DINÂMICA DE EQUIPE (S-curve)")
    print("="*80)
    print()

    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]
    backlog = 50
    start_date = "01/11/2025"
    deadline_date = "20/12/2025"

    print(f"Throughput histórico: {tp_samples}")
    print(f"Backlog: {backlog} items")
    print(f"Equipe: 10 pessoas (2-5 ativas, S-curve 20%)")
    print(f"Deadline: {deadline_date}")
    print()

    result = ml_analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        team_size=10,
        min_contributors=2,
        max_contributors=5,
        s_curve_size=20,
        n_simulations=1000
    )

    print("RESULTADOS ML (Com S-curve)")
    print("─" * 80)
    print(f"Deadline:                        {result['deadline_date']}")
    print(f"Semanas até deadline:            {result['weeks_to_deadline']:.1f}")
    print(f"Semanas projetadas (P85):        {result['projected_weeks_p85']:.1f}")
    print(f"Trabalho entregue (P85):         {result['projected_work_p85']}")
    print(f"Esforço estimado (P85):          {result['projected_effort_p85']} person-weeks")
    print(f"Pode cumprir deadline?           {'Sim' if result['can_meet_deadline'] else 'Não'}")
    print(f"% escopo completado:             {result['scope_completion_pct']}%")
    print()


def test_ml_with_all_parameters():
    """Test ML with all project parameters"""

    print("="*80)
    print("TESTE 3: ML COM TODOS OS PARÂMETROS")
    print("="*80)
    print()

    tp_samples = [3, 5, 4, 6, 5, 7, 4, 5, 6, 5, 4, 6]
    backlog = 30
    start_date = "01/11/2025"
    deadline_date = "20/12/2025"

    # Lead times (em dias)
    lt_samples = [1, 2, 3, 2, 1, 2, 3, 2]

    # Split rates (multiplicadores de escopo)
    split_rate_samples = [1.0, 1.1, 1.2, 1.0, 1.1]

    print(f"Throughput histórico: {tp_samples}")
    print(f"Média TP: {sum(tp_samples)/len(tp_samples):.1f} items/semana")
    print(f"Backlog: {backlog} items")
    print(f"Equipe: 8 pessoas (2-4 ativas)")
    print(f"S-curve: 15%")
    print(f"Lead times: {lt_samples} dias")
    print(f"Split rates: {split_rate_samples}")
    print(f"Deadline: {deadline_date}")
    print()

    # Análise de deadline
    deadline_result = ml_analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        team_size=8,
        min_contributors=2,
        max_contributors=4,
        s_curve_size=15,
        lt_samples=lt_samples,
        split_rate_samples=split_rate_samples,
        n_simulations=1000
    )

    print("┌" + "─"*78 + "┐")
    print("│ ANÁLISE DE DEADLINE (ML)                                                   │")
    print("└" + "─"*78 + "┘")
    print(f"  Semanas disponíveis:          {deadline_result['weeks_to_deadline']:.1f}")
    print(f"  Semanas necessárias (P85):    {deadline_result['projected_weeks_p85']:.1f}")
    print(f"  Esforço estimado (P85):       {deadline_result['projected_effort_p85']} person-weeks")
    print(f"  Status:                       {'✓ Viável' if deadline_result['can_meet_deadline'] else '✗ Em risco'}")
    print(f"  % escopo entregue:            {deadline_result['scope_completion_pct']}%")
    print()

    # Quantos?
    how_many_result = ml_forecast_how_many(
        tp_samples=tp_samples,
        start_date=start_date,
        end_date=deadline_date,
        team_size=8,
        min_contributors=2,
        max_contributors=4,
        s_curve_size=15,
        lt_samples=lt_samples,
        n_simulations=1000
    )

    print("┌" + "─"*78 + "┐")
    print("│ QUANTOS ITEMS ATÉ O DEADLINE? (ML)                                         │")
    print("└" + "─"*78 + "┘")
    print(f"  Período: {how_many_result['weeks']} semanas")
    print(f"  Items esperados (P50):        {how_many_result['items_p50']}")
    print(f"  Items conservador (P85):      {how_many_result['items_p85']}")
    print(f"  Items otimista (P95):         {how_many_result['items_p95']}")
    print()

    # Quando?
    when_result = ml_forecast_when(
        tp_samples=tp_samples,
        backlog=backlog,
        start_date=start_date,
        team_size=8,
        min_contributors=2,
        max_contributors=4,
        s_curve_size=15,
        lt_samples=lt_samples,
        split_rate_samples=split_rate_samples,
        n_simulations=1000
    )

    print("┌" + "─"*78 + "┐")
    print("│ QUANDO O BACKLOG ESTARÁ COMPLETO? (ML)                                     │")
    print("└" + "─"*78 + "┘")
    print(f"  Data provável (P50):          {when_result['date_p50']}")
    print(f"  Data conservadora (P85):      {when_result['date_p85']}")
    print(f"  Data pessimista (P95):        {when_result['date_p95']}")
    print(f"  Esforço estimado (P85):       {when_result['effort_p85']} person-weeks")
    print()

    print("MODELOS ML:")
    for model in deadline_result['ml_models']:
        print(f"  {model['model']:<25} MAE: {model['mae']:>6.2f}  RMSE: {model['rmse']:>6.2f}  Erro%: {model['mae_percent']:>5.1f}%")
    print()


def test_ml_vs_monte_carlo_comparison():
    """Compare ML and Monte Carlo approaches"""

    print("="*80)
    print("TESTE 4: COMPARAÇÃO ML vs MONTE CARLO")
    print("="*80)
    print()

    from monte_carlo_unified import analyze_deadline as mc_analyze_deadline
    from datetime import datetime

    tp_samples = [4, 5, 6, 7, 5, 6, 7, 8, 5, 6, 4, 7]
    backlog = 20
    start_date = "01/10/2025"
    deadline_date = "01/11/2025"

    print(f"Cenário:")
    print(f"  Throughput: {tp_samples}")
    print(f"  Backlog: {backlog} items")
    print(f"  Deadline: {deadline_date} ({(datetime.strptime(deadline_date, '%d/%m/%Y') - datetime.strptime(start_date, '%d/%m/%Y')).days / 7:.1f} semanas)")
    print()

    # Monte Carlo
    mc_result = mc_analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    # Machine Learning
    ml_result = ml_analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        team_size=1,
        n_simulations=1000
    )

    from datetime import datetime

    print("┌" + "─"*78 + "┐")
    print("│ MONTE CARLO                                                                │")
    print("└" + "─"*78 + "┘")
    print(f"  Semanas projetadas (P85):     {mc_result['projected_weeks_p85']:.1f}")
    print(f"  Trabalho entregue (P85):      {mc_result['projected_work_p85']}")
    print(f"  Pode cumprir deadline?        {'✓ Sim' if mc_result['can_meet_deadline'] else '✗ Não'}")
    print(f"  Método: Weibull Distribution")
    print()

    print("┌" + "─"*78 + "┐")
    print("│ MACHINE LEARNING                                                           │")
    print("└" + "─"*78 + "┘")
    print(f"  Semanas projetadas (P85):     {ml_result['projected_weeks_p85']:.1f}")
    print(f"  Trabalho entregue (P85):      {ml_result['projected_work_p85']}")
    print(f"  Pode cumprir deadline?        {'✓ Sim' if ml_result['can_meet_deadline'] else '✗ Não'}")
    print(f"  Método: {ml_result['forecast_method']}")
    print()

    print("ANÁLISE:")
    print(f"  Diferença P85: {abs(mc_result['projected_weeks_p85'] - ml_result['projected_weeks_p85']):.1f} semanas")
    print(f"  Consenso: {'✓ Ambos concordam' if mc_result['can_meet_deadline'] == ml_result['can_meet_deadline'] else '✗ Resultados divergentes'}")
    print()


if __name__ == "__main__":
    print()
    print("╔" + "═"*78 + "╗")
    print("║" + " "*15 + "TESTES DE DEADLINE E FORECAST - MACHINE LEARNING" + " "*15 + "║")
    print("╚" + "═"*78 + "╝")
    print()

    # Teste 1: Simples
    test_ml_simple_scenario()

    print()

    # Teste 2: Com S-curve
    test_ml_with_team_dynamics()

    print()

    # Teste 3: Com todos os parâmetros
    test_ml_with_all_parameters()

    print()

    # Teste 4: ML vs Monte Carlo
    test_ml_vs_monte_carlo_comparison()

    print("="*80)
    print("✓ TODOS OS TESTES ML CONCLUÍDOS")
    print("="*80)
    print()
    print("FUNCIONALIDADES IMPLEMENTADAS:")
    print("  ✓ ml_analyze_deadline() - Análise de deadline com ML")
    print("  ✓ ml_forecast_how_many() - Previsão de itens com ML")
    print("  ✓ ml_forecast_when() - Previsão de datas com ML")
    print("  ✓ Suporte a equipe variável (team_size, min/max contributors)")
    print("  ✓ Suporte a S-curve (ramp-up/down)")
    print("  ✓ Suporte a split rates")
    print("  ✓ Suporte a lead times")
    print()
