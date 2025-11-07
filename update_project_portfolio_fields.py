#!/usr/bin/env python3
"""
Script para atualizar campos de portfólio dos projetos (business_value e risk_level)
que estavam com valores default após a migração.

Distribui os projetos de forma mais balanceada entre os quadrantes da matriz de priorização.
"""

import psycopg2
import os

# Conectar ao banco PostgreSQL no Fly.io
conn = psycopg2.connect(
    host="localhost",
    port=15432,
    database="flow_forecaster_db",
    user="postgres",
    password=os.environ.get("PGPASSWORD", "4ZRplUZglrnfO3Y")
)

cur = conn.cursor()

# Buscar todos os projetos
cur.execute("SELECT id, name FROM projects ORDER BY id")
projects = cur.fetchall()

print(f"Encontrados {len(projects)} projetos")
print("\nAtualizando valores de business_value e risk_level...")
print("="*70)

# Distribuir projetos entre os quadrantes de forma variada
# Para demonstração, vou alternar entre os quadrantes
updates = [
    # (id, business_value, risk_level, quadrante_esperado)
    # Alto Valor / Baixo Risco (Quick Wins) - business_value >= 60, risk in ['low', 'medium']
    (projects[0][0], 75, 'low', 'Quick Wins'),
    (projects[1][0], 80, 'medium', 'Quick Wins'),

    # Alto Valor / Alto Risco (Strategic Bets) - business_value >= 60, risk in ['high', 'critical']
    (projects[2][0], 70, 'high', 'Strategic Bets'),
    (projects[3][0], 85, 'critical', 'Strategic Bets'),

    # Baixo Valor / Baixo Risco (Fill-ins) - business_value < 60, risk in ['low', 'medium']
    (projects[4][0], 40, 'low', 'Fill-ins'),
    (projects[5][0], 50, 'medium', 'Fill-ins'),

    # Baixo Valor / Alto Risco (Avoid) - business_value < 60, risk in ['high', 'critical']
    (projects[6][0], 30, 'high', 'Avoid'),
]

# Adicionar os projetos restantes como Fill-ins (se houver mais de 7)
if len(projects) > 7:
    for i in range(7, len(projects)):
        updates.append((projects[i][0], 45, 'medium', 'Fill-ins'))

for project_id, biz_value, risk_level, quadrant in updates:
    project_name = next(p[1] for p in projects if p[0] == project_id)

    cur.execute("""
        UPDATE projects
        SET business_value = %s,
            risk_level = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (biz_value, risk_level, project_id))

    print(f"✓ {project_name:40} → Valor: {biz_value:3}, Risco: {risk_level:10} [{quadrant}]")

conn.commit()

print("="*70)
print(f"\n✅ {len(updates)} projetos atualizados com sucesso!")
print("\nDistribuição esperada na matriz:")
print("  - Quick Wins (Alto Valor/Baixo Risco): ~2 projetos")
print("  - Strategic Bets (Alto Valor/Alto Risco): ~2 projetos")
print("  - Fill-ins (Baixo Valor/Baixo Risco): ~3+ projetos")
print("  - Avoid (Baixo Valor/Alto Risco): ~1 projeto")

print("\nPróximos passos:")
print("  1. Acesse https://flow-forecaster.fly.dev e vá para a aba 'Portfólio'")
print("  2. A matriz deve mostrar os projetos distribuídos nos 4 quadrantes")
print("  3. Você pode ajustar individualmente os valores de cada projeto depois")

cur.close()
conn.close()
