#!/usr/bin/env python3
"""
Teste para validar a correção dos bugs na análise de deadline
"""

from monte_carlo_unified import analyze_deadline, forecast_how_many, forecast_when

def test_deadline_analysis_with_user_data():
    """
    Teste usando os dados exatos fornecidos pelo usuário
    """
    print("=" * 80)
    print("TESTE DE VALIDAÇÃO DA CORREÇÃO DO BUG")
    print("=" * 80)

    # Dados do exemplo do usuário
    tp_samples = [5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 5, 7]  # Throughput histórico
    backlog = 25
    start_date = "21/10/2025"
    deadline_date = "21/11/2025"

    print(f"\n📋 Dados de entrada:")
    print(f"   Backlog: {backlog} itens")
    print(f"   Início: {start_date}")
    print(f"   Deadline: {deadline_date}")
    print(f"   Throughput histórico: {tp_samples}")

    # Executar análise
    print(f"\n🔍 Executando análise de deadline...")
    result = analyze_deadline(
        tp_samples=tp_samples,
        backlog=backlog,
        deadline_date=deadline_date,
        start_date=start_date,
        n_simulations=10000
    )

    # "Quantos?" - Capacidade sem limite de backlog
    print(f"\n📊 QUANTOS? (Capacidade no período)")
    how_many = forecast_how_many(tp_samples, start_date, deadline_date, 10000)
    print(f"   95% DE CONFIANÇA: {how_many['items_p95']} itens")
    print(f"   85% DE CONFIANÇA: {how_many['items_p85']} itens")
    print(f"   50% DE CONFIANÇA: {how_many['items_p50']} itens")

    # "Quando?" - Quando o backlog será completado
    print(f"\n📅 QUANDO? (Data de conclusão do backlog de {backlog})")
    when = forecast_when(tp_samples, backlog, start_date, 10000)
    print(f"   95% de confiança: {when['date_p95']}")
    print(f"   85% de confiança: {when['date_p85']}")
    print(f"   50% de confiança: {when['date_p50']}")

    # Validação dos resultados
    print(f"\n✅ VALIDAÇÃO DOS RESULTADOS:")
    print(f"   Semanas para deadline: {result['weeks_to_deadline']}")
    print(f"   Semanas projetadas (P85): {result['projected_weeks_p85']}")
    print(f"   Trabalho projetado (P85): {result['projected_work_p85']}")

    # Verificar lógica correta
    print(f"\n🔬 VERIFICAÇÃO DA LÓGICA:")

    # 1. Capacidade vs Backlog
    capacity_p85 = how_many['items_p85']
    print(f"\n   1. Capacidade (P85): {capacity_p85} itens")
    print(f"      Backlog: {backlog} itens")

    if capacity_p85 >= backlog:
        print(f"      ✅ Capacidade MAIOR que backlog → Consegue completar!")
    else:
        print(f"      ⚠️  Capacidade MENOR que backlog → NÃO consegue completar tudo")

    # 2. % do escopo que será cumprido
    scope_pct = (result['projected_work_p85'] / backlog * 100)
    print(f"\n   2. Escopo que será cumprido:")
    print(f"      {result['projected_work_p85']} de {backlog} itens = {scope_pct:.0f}%")

    # 3. Pode cumprir deadline?
    print(f"\n   3. Pode cumprir deadline?")
    print(f"      Tempo disponível: {result['weeks_to_deadline']} semanas")
    print(f"      Tempo necessário (P85): {result['projected_weeks_p85']} semanas")

    if result['can_meet_deadline']:
        print(f"      ✅ SIM - Tem tempo suficiente!")
    else:
        print(f"      ⚠️  NÃO - Precisa de mais tempo")

    # 4. Verificação de consistência
    print(f"\n🧪 TESTE DE CONSISTÊNCIA:")

    # Se capacidade >= backlog, então projected_work deve ser 100% do backlog
    if capacity_p85 >= backlog:
        expected_work = backlog
        actual_work = result['projected_work_p85']
        if actual_work == expected_work:
            print(f"   ✅ PASS: Trabalho projetado correto ({actual_work} = {expected_work})")
        else:
            print(f"   ❌ FAIL: Trabalho projetado incorreto ({actual_work} != {expected_work})")

    # scope_completion_pct deve ser calculado corretamente
    expected_scope_pct = (result['projected_work_p85'] / backlog * 100)
    actual_scope_pct = result['scope_completion_pct']

    print(f"\n   Escopo completion %:")
    print(f"   Esperado: {expected_scope_pct:.0f}%")
    print(f"   Atual: {actual_scope_pct}%")

    if abs(expected_scope_pct - actual_scope_pct) <= 1:
        print(f"   ✅ PASS: Cálculo de scope_completion_pct correto")
    else:
        print(f"   ❌ FAIL: Cálculo de scope_completion_pct incorreto")

    # Conclusão final
    print(f"\n🎯 CONCLUSÃO FINAL:")

    if capacity_p85 >= backlog:
        print(f"   ✅ Você CONSEGUIRÁ completar os {backlog} itens!")
        print(f"   📊 Capacidade P85: {capacity_p85} itens > Backlog: {backlog} itens")
        print(f"   ⏱️  Conclusão esperada em: {when['date_p85']} (P85)")

        if result['can_meet_deadline']:
            print(f"   🎉 E conseguirá cumprir o deadline de {deadline_date}!")
        else:
            print(f"   ⚠️  Mas pode não cumprir o deadline de {deadline_date}")
            print(f"      (precisa de {result['projected_weeks_p85']} semanas, tem {result['weeks_to_deadline']})")
    else:
        print(f"   ⚠️  Você NÃO conseguirá completar todos os {backlog} itens no prazo")
        print(f"   📊 Capacidade P85: {capacity_p85} itens < Backlog: {backlog} itens")
        print(f"   ✅ Mas entregará {result['projected_work_p85']} itens ({scope_pct:.0f}% do backlog)")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_deadline_analysis_with_user_data()
