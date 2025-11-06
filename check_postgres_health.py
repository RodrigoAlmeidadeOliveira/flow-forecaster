#!/usr/bin/env python3
"""
Script de diagnóstico PostgreSQL
Verifica se o PostgreSQL está online e funcionando corretamente
"""
import os
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print('=' * 60)
print('DIAGNÓSTICO COMPLETO DO POSTGRESQL')
print('=' * 60)

# 1. Verificar URL de conexão (mascarar senha)
print('\n[1] String de Conexão:')
if '@' in db_url:
    masked_url = db_url.split('@')[1]
    host_part = masked_url.split('/')[0] if '/' in masked_url else masked_url
    print(f'    Host: {host_part}')
else:
    print('    ❌ URL de conexão inválida')

# 2. Conectar e testar
engine = create_engine(db_url, pool_pre_ping=True)
try:
    with engine.connect() as conn:
        print('\n[2] Status da Conexão:')
        print('    ✅ CONECTADO com sucesso!')

        # 3. Versão do PostgreSQL
        print('\n[3] Versão do PostgreSQL:')
        version = conn.execute(text('SELECT version()')).scalar()
        print(f'    {version.split(",")[0]}')

        # 4. Informações do banco atual
        print('\n[4] Informações do Banco:')
        db_name = conn.execute(text('SELECT current_database()')).scalar()
        db_user = conn.execute(text('SELECT current_user')).scalar()
        db_size = conn.execute(text(
            "SELECT pg_size_pretty(pg_database_size(current_database()))"
        )).scalar()

        print(f'    Database: {db_name}')
        print(f'    Usuário:  {db_user}')
        print(f'    Tamanho:  {db_size}')

        # 5. Listar tabelas
        print('\n[5] Tabelas Existentes:')
        tables = conn.execute(text(
            """
            SELECT table_name,
                   pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )).fetchall()

        for table, size in tables:
            print(f'    - {table:20s} ({size})')

        # 6. Contar registros
        print('\n[6] Contagem de Registros:')
        for table, _ in tables:
            count = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
            print(f'    - {table:20s}: {count:4d} registros')

        # 7. Teste de escrita
        print('\n[7] Teste de Escrita/Leitura:')
        test_table = 'pg_health_check_test'
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {test_table}'))
            conn.execute(text(f'CREATE TABLE {test_table} (id INT, ts TIMESTAMP)'))
            conn.execute(text(f"INSERT INTO {test_table} VALUES (1, NOW())"))
            result = conn.execute(text(f'SELECT * FROM {test_table}')).fetchone()
            conn.execute(text(f'DROP TABLE {test_table}'))
            conn.commit()
            print(f'    ✅ Escrita OK - ID: {result[0]}, Timestamp: {result[1]}')
        except Exception as e:
            print(f'    ❌ Erro: {e}')

        # 8. Conexões ativas
        print('\n[8] Conexões Ativas:')
        connections = conn.execute(text(
            """
            SELECT count(*) as total,
                   count(*) FILTER (WHERE state = 'active') as active,
                   count(*) FILTER (WHERE state = 'idle') as idle
            FROM pg_stat_activity
            WHERE datname = current_database()
            """
        )).fetchone()
        print(f'    Total: {connections[0]} | Ativas: {connections[1]} | Idle: {connections[2]}')

        # 9. Uptime
        print('\n[9] Uptime do PostgreSQL:')
        uptime = conn.execute(text(
            "SELECT DATE_TRUNC('second', NOW() - pg_postmaster_start_time()) as uptime"
        )).scalar()
        print(f'    {uptime}')

        # 10. Cluster Info (se aplicável)
        print('\n[10] Informações do Cluster:')
        try:
            is_replica = conn.execute(text("SELECT pg_is_in_recovery()")).scalar()
            if is_replica:
                print('    Tipo: REPLICA')
            else:
                print('    Tipo: PRIMARY')
        except:
            print('    Tipo: Standalone')

        print('\n' + '=' * 60)
        print('✅ PostgreSQL está ONLINE e FUNCIONAL!')
        print('=' * 60)

except Exception as e:
    print(f'\n❌ ERRO: {e}')
    print('\nPostgreSQL pode estar offline ou inacessível.')
    exit(1)
