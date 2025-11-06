#!/usr/bin/env python3
"""
Migração do SQLite local completo para PostgreSQL no Fly.io
Requer: flyctl proxy 15432:5432 --app flow-forecaster-db
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta

# Configuração
SQLITE_DB = 'forecaster_from_flyio_vol2.db'
PG_CONFIG = {
    'host': 'localhost',
    'port': 15432,
    'database': 'flow_forecaster',
    'user': 'flow_forecaster',
    'password': '4ZRplUZglrnfO3Y'
}

def main():
    print("="*60)
    print("Migração SQLite → PostgreSQL")
    print("="*60)

    # Conectar ao SQLite
    print("\n[1/4] Conectando ao SQLite...")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        print(f"    ✓ Conectado: {SQLITE_DB}")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return

    # Conectar ao PostgreSQL
    print("\n[2/4] Conectando ao PostgreSQL...")
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor()
        print("    ✓ Conectado ao PostgreSQL")
    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return

    # Extrair dados do SQLite
    print("\n[3/4] Extraindo dados do SQLite...")
    sqlite_cursor = sqlite_conn.cursor()

    data = {}
    for table in ['users', 'projects', 'forecasts', 'actuals']:
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        data[table] = [dict(row) for row in sqlite_cursor.fetchall()]
        print(f"    - {table}: {len(data[table])} registros")

    # Migrar para PostgreSQL
    print("\n[4/4] Migrando dados para PostgreSQL...")

    try:
        # Limpar tabelas (ordem reversa por causa das FKs)
        print("\n    Limpando tabelas...")
        for table in ['actuals', 'forecasts', 'projects', 'users']:
            pg_cursor.execute(f"DELETE FROM {table}")
            print(f"      ✓ {table} limpa")
        pg_conn.commit()

        # Migrar users
        print("\n    Migrando users...")
        for user in data['users']:
            pg_cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, created_at, access_expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user['id'],
                user['name'],
                user['email'],
                user.get('password_hash', 'legacy'),
                user.get('created_at', datetime.now()),
                datetime.now() + timedelta(days=365)  # 1 ano de acesso
            ))
        pg_conn.commit()
        print(f"      ✓ {len(data['users'])} users migrados")

        # Migrar projects
        print("\n    Migrando projects...")
        for proj in data['projects']:
            pg_cursor.execute("""
                INSERT INTO projects (
                    id, name, user_id, description, team_size, status, priority,
                    business_value, risk_level, capacity_allocated,
                    strategic_importance, start_date, target_end_date,
                    owner, stakeholder, tags, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                proj['id'], proj['name'], proj.get('user_id'),
                proj.get('description'), proj.get('team_size'), proj.get('status'),
                proj.get('priority'), proj.get('business_value'), proj.get('risk_level'),
                proj.get('capacity_allocated'), proj.get('strategic_importance'),
                proj.get('start_date'), proj.get('target_end_date'),
                proj.get('owner'), proj.get('stakeholder'), proj.get('tags'),
                proj.get('created_at', datetime.now()), proj.get('updated_at')
            ))
        pg_conn.commit()
        print(f"      ✓ {len(data['projects'])} projects migrados")

        # Migrar forecasts
        print("\n    Migrando forecasts...")
        for fc in data['forecasts']:
            # Converter boolean (SQLite armazena como 0/1)
            can_meet = fc.get('can_meet_deadline')
            can_meet_bool = bool(can_meet) if can_meet is not None else None

            pg_cursor.execute("""
                INSERT INTO forecasts (
                    id, project_id, user_id, name, description, forecast_type,
                    forecast_data, input_data, backlog, deadline_date, start_date,
                    weeks_to_deadline, projected_weeks_p85, can_meet_deadline,
                    scope_completion_pct, created_at, created_by, version, parent_forecast_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                fc['id'], fc['project_id'], fc.get('user_id'), fc['name'],
                fc.get('description'), fc.get('forecast_type'),
                fc['forecast_data'], fc['input_data'], fc.get('backlog'),
                fc.get('deadline_date'), fc.get('start_date'),
                fc.get('weeks_to_deadline'), fc.get('projected_weeks_p85'),
                can_meet_bool, fc.get('scope_completion_pct'),
                fc.get('created_at', datetime.now()), fc.get('created_by'),
                fc.get('version'), fc.get('parent_forecast_id')
            ))
        pg_conn.commit()
        print(f"      ✓ {len(data['forecasts'])} forecasts migrados")

        # Migrar actuals
        print("\n    Migrando actuals...")
        for act in data['actuals']:
            pg_cursor.execute("""
                INSERT INTO actuals (
                    id, forecast_id, actual_completion_date, actual_weeks_taken,
                    actual_items_completed, actual_scope_delivered_pct,
                    weeks_error, weeks_error_pct, scope_error_pct,
                    notes, recorded_at, recorded_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                act['id'], act['forecast_id'], act.get('actual_completion_date'),
                act.get('actual_weeks_taken'), act.get('actual_items_completed'),
                act.get('actual_scope_delivered_pct'), act.get('weeks_error'),
                act.get('weeks_error_pct'), act.get('scope_error_pct'),
                act.get('notes'), act.get('recorded_at', datetime.now()),
                act.get('recorded_by')
            ))
        pg_conn.commit()
        print(f"      ✓ {len(data['actuals'])} actuals migrados")

        # Verificação
        print("\n" + "="*60)
        print("Verificação Final")
        print("="*60)
        for table in ['users', 'projects', 'forecasts', 'actuals']:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = pg_cursor.fetchone()[0]
            print(f"  {table:15s}: {count} registros")

        print("\n✅ Migração concluída com sucesso!")

    except Exception as e:
        pg_conn.rollback()
        print(f"\n✗ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    main()
