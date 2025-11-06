#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para PostgreSQL
Uso: python migrate_sqlite_to_postgres.py
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Configuração
SQLITE_PATH = 'sqlite:////data/forecaster.db'
POSTGRES_URL = os.environ.get('DATABASE_URL', '')

# Fix postgres:// to postgresql://
if POSTGRES_URL.startswith('postgres://'):
    POSTGRES_URL = POSTGRES_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 60)
print("Migração SQLite → PostgreSQL")
print("=" * 60)

# Validações
if not POSTGRES_URL or not POSTGRES_URL.startswith('postgresql://'):
    print("❌ DATABASE_URL não configurada ou inválida")
    print(f"   DATABASE_URL: {POSTGRES_URL[:50] if POSTGRES_URL else 'não definida'}")
    sys.exit(1)

# Conectar aos bancos
try:
    print("\n[1/5] Conectando ao SQLite...")
    sqlite_engine = create_engine(SQLITE_PATH, echo=False)
    sqlite_conn = sqlite_engine.connect()
    print("    ✓ Conectado ao SQLite")
except Exception as e:
    print(f"    ❌ Erro ao conectar SQLite: {e}")
    sys.exit(1)

try:
    print("\n[2/5] Conectando ao PostgreSQL...")
    pg_engine = create_engine(
        POSTGRES_URL,
        pool_pre_ping=True,
        echo=False
    )
    pg_conn = pg_engine.connect()
    print("    ✓ Conectado ao PostgreSQL")
except Exception as e:
    print(f"    ❌ Erro ao conectar PostgreSQL: {e}")
    sys.exit(1)

# Verificar tabelas no SQLite
print("\n[3/5] Analisando dados no SQLite...")
sqlite_inspector = inspect(sqlite_engine)
sqlite_tables = sqlite_inspector.get_table_names()

if not sqlite_tables:
    print("    ⚠ Nenhuma tabela encontrada no SQLite")
    sys.exit(0)

print(f"    Tabelas encontradas: {', '.join(sqlite_tables)}")

# Contagem de registros
data_summary = {}
for table in sqlite_tables:
    try:
        result = sqlite_conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        data_summary[table] = count
        print(f"    - {table}: {count} registros")
    except Exception as e:
        print(f"    ⚠ Erro ao contar {table}: {e}")
        data_summary[table] = 0

# Confirmar migração
total_records = sum(data_summary.values())
if total_records == 0:
    print("\n    ℹ Nenhum dado para migrar")
    sys.exit(0)

print(f"\n    Total: {total_records} registros para migrar")
print("\n[4/5] Iniciando migração...")

# Ordem de migração (respeitar foreign keys)
migration_order = ['users', 'projects', 'forecasts', 'actuals']

# Tabelas a migrar (apenas as que existem em ambos os bancos)
pg_inspector = inspect(pg_engine)
pg_tables = set(pg_inspector.get_table_names())
tables_to_migrate = [t for t in migration_order if t in sqlite_tables and t in pg_tables]

# Adicionar tabelas que não estão na ordem especificada
for table in sqlite_tables:
    if table not in tables_to_migrate and table in pg_tables:
        tables_to_migrate.append(table)

migrated_counts = {}

for table in tables_to_migrate:
    count = data_summary.get(table, 0)
    if count == 0:
        print(f"\n    [{table}] Pulando (vazio)")
        continue

    print(f"\n    [{table}] Migrando {count} registros...")

    try:
        # Obter colunas da tabela
        columns = [col['name'] for col in sqlite_inspector.get_columns(table)]
        columns_str = ', '.join(columns)
        placeholders = ', '.join([f':{col}' for col in columns])

        # Ler dados do SQLite
        rows = sqlite_conn.execute(text(f"SELECT {columns_str} FROM {table}")).fetchall()

        if not rows:
            print(f"    [{table}] Nenhum dado encontrado")
            continue

        # Começar transação PostgreSQL
        trans = pg_conn.begin()

        try:
            # Inserir no PostgreSQL (ignorar duplicatas se houver)
            migrated = 0
            for row in rows:
                row_dict = dict(zip(columns, row))
                try:
                    # Tentar inserir
                    pg_conn.execute(
                        text(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"),
                        row_dict
                    )
                    migrated += 1
                except Exception as insert_error:
                    # Se falhar (ex: duplicata), continuar
                    if 'duplicate' in str(insert_error).lower() or 'unique' in str(insert_error).lower():
                        pass  # Ignorar duplicatas
                    else:
                        print(f"      ⚠ Erro ao inserir registro: {insert_error}")

            trans.commit()
            migrated_counts[table] = migrated
            print(f"    [{table}] ✓ {migrated} registros migrados")

        except Exception as e:
            trans.rollback()
            print(f"    [{table}] ❌ Erro: {e}")
            migrated_counts[table] = 0

    except Exception as e:
        print(f"    [{table}] ❌ Erro ao processar: {e}")
        migrated_counts[table] = 0

# Fechar conexões
sqlite_conn.close()
pg_conn.close()

# Resumo
print("\n" + "=" * 60)
print("[5/5] Resumo da Migração")
print("=" * 60)

total_migrated = sum(migrated_counts.values())
for table, count in migrated_counts.items():
    print(f"  {table:20s}: {count:4d} registros migrados")

print(f"\n  Total migrado: {total_migrated}/{total_records} registros")

if total_migrated == total_records:
    print("\n✅ Migração concluída com sucesso!")
    sys.exit(0)
elif total_migrated > 0:
    print("\n⚠ Migração parcial - alguns registros podem ter sido ignorados (duplicatas)")
    sys.exit(0)
else:
    print("\n❌ Nenhum registro foi migrado")
    sys.exit(1)
