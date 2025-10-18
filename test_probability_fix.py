"""
Test script to validate probability calculation fix
"""

from monte_carlo_unified import forecast_how_many, forecast_when, percentile as mc_percentile
from datetime import datetime, timedelta

# Sample throughput data (assumed from the report)
# Let's reverse-engineer: If 31 days (4.4 weeks) gives P85=33 items
# Then average throughput ≈ 7.5 items/week
# This suggests samples around: [5, 6, 7, 8, 9, 10] items/week

tp_samples = [5, 6, 7, 8, 9, 10, 7, 8, 6, 7, 8, 9]

print("=" * 80)
print("TESTE DE VALIDAÇÃO DO CÁLCULO DE PROBABILIDADES")
print("=" * 80)

# Test 1: "Quantos?" - How many items in 31 days?
print("\n📊 TESTE 1: 'Quantos?' - Capacidade em 31 dias")
print("-" * 80)

start_date = "17/10/2025"
end_date = "17/11/2025"

result_quantos = forecast_how_many(
    tp_samples=tp_samples,
    start_date=start_date,
    end_date=end_date,
    n_simulations=10000
)

print(f"Período: {start_date} → {end_date}")
print(f"Dias: {result_quantos['days']}")
print(f"Semanas: {result_quantos['weeks']}")
print(f"\nCapacidade (sem limite de backlog):")
print(f"  95% de confiança: {result_quantos['items_p95']} itens")
print(f"  85% de confiança: {result_quantos['items_p85']} itens")
print(f"  50% de confiança: {result_quantos['items_p50']} itens")
print(f"  Média: {result_quantos['items_mean']} itens")

# Test 2: "Quando?" - When will 50 items be completed?
print("\n📊 TESTE 2: 'Quando?' - Completar 50 itens")
print("-" * 80)

backlog = 50

result_quando = forecast_when(
    tp_samples=tp_samples,
    backlog=backlog,
    start_date=start_date,
    n_simulations=10000
)

print(f"Backlog: {backlog} itens")
print(f"Início: {result_quando['start_date']}")
print(f"\nPrevisão de conclusão:")
print(f"  95% de confiança: {result_quando['date_p95']} ({result_quando['weeks_p95']:.1f} semanas)")
print(f"  85% de confiança: {result_quando['date_p85']} ({result_quando['weeks_p85']:.1f} semanas)")
print(f"  50% de confiança: {result_quando['date_p50']} ({result_quando['weeks_p50']:.1f} semanas)")

# Test 3: Consistency check
print("\n📊 TESTE 3: Verificação de Consistência")
print("-" * 80)

weeks_available = result_quantos['weeks']
items_p85_in_period = result_quantos['items_p85']
throughput_p85 = items_p85_in_period / weeks_available

weeks_needed_for_50_calculated = backlog / throughput_p85
weeks_needed_for_50_reported = result_quando['weeks_p85']

print(f"Throughput P85: {throughput_p85:.2f} itens/semana")
print(f"Semanas disponíveis: {weeks_available}")
print(f"Itens completados (P85): {items_p85_in_period}")
print(f"\nPara completar {backlog} itens:")
print(f"  Calculado: {weeks_needed_for_50_calculated:.1f} semanas")
print(f"  Reportado: {weeks_needed_for_50_reported:.1f} semanas")
print(f"  Diferença: {abs(weeks_needed_for_50_calculated - weeks_needed_for_50_reported):.1f} semanas")

if abs(weeks_needed_for_50_calculated - weeks_needed_for_50_reported) < 1:
    print("\n✅ CONSISTENTE: Os cálculos estão alinhados!")
else:
    print(f"\n⚠️ DIVERGÊNCIA: Diferença de {abs(weeks_needed_for_50_calculated - weeks_needed_for_50_reported):.1f} semanas")
    print("   Isso pode indicar que estão sendo usados parâmetros diferentes nas simulações")

# Test 4: Validate probability table (30-day forecast)
print("\n📊 TESTE 4: Tabela de Probabilidades (30 dias)")
print("-" * 80)

start_dt = datetime.strptime(start_date, '%d/%m/%Y')
horizon_30_dt = start_dt + timedelta(days=30)
horizon_30_str = horizon_30_dt.strftime('%d/%m/%Y')

result_30_days = forecast_how_many(
    tp_samples=tp_samples,
    start_date=start_date,
    end_date=horizon_30_str,
    n_simulations=10000
)

distribution_30 = result_30_days.get('distribution', [])

print(f"Horizonte: {start_date} → {horizon_30_str} ({result_30_days['days']} dias)")
print(f"\nItens estimados em {result_30_days['days']} dias")
print("Probabilidade    Itens em 30 dias")

# Calculate probability table (CORRECTED VERSION)
for prob in [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 1]:
    # FIXED: probability interpretation
    # 100% probability = percentile 0 (minimum value that occurs in 100% of cases)
    # 1% probability = percentile 99 (value that only 1% of cases exceed)
    percentile_value = mc_percentile(distribution_30, (100 - prob) / 100)
    print(f"{prob}%\t{int(round(percentile_value))}")

print("\n" + "=" * 80)
print("INTERPRETAÇÃO:")
print("- 100% de probabilidade = valor mínimo (ocorre em 100% dos casos)")
print("- 50% de probabilidade = mediana (ocorre em 50% dos casos)")
print("- 1% de probabilidade = valor muito alto (apenas 1% dos casos supera)")
print("=" * 80)
