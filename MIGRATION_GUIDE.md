# Guia de Migração SQLite → PostgreSQL

Guia completo para migrar dados do SQLite local para PostgreSQL no Fly.io.

## 🎯 Visão Geral

### O que será migrado

- ✅ **Users** - Todos os usuários e senhas
- ✅ **Projects** - Projetos e suas configurações  
- ✅ **Forecasts** - Previsões salvas com resultados
- ✅ **Actuals** - Dados reais para backtesting

### Tempo estimado

- Poucos registros (<100): **~2 minutos**
- Muitos registros (>1000): **~10-15 minutos**

---

## 🚀 Método Recomendado: Via Fly Proxy

Este é o método mais simples e seguro.

### Passo 1: Backup do SQLite

```bash
# Criar backup antes da migração
cp forecaster.db forecaster.db.backup.$(date +%Y%m%d_%H%M%S)

# Verificar backup
ls -lh forecaster.db*
```

### Passo 2: Criar Proxy para PostgreSQL

```bash
# Terminal 1: Criar proxy (deixar rodando)
fly proxy 15432:5432 -a flow-forecaster-db

# Output:
# Proxying local port 15432 to remote [flow-forecaster-db.internal]:5432
```

**⚠️ Deixe este terminal aberto!** O proxy precisa ficar ativo durante a migração.

### Passo 3: Preparar Connection String

```bash
# Em outro terminal (Terminal 2)
# Usar suas credenciais do PostgreSQL
export DATABASE_URL="postgresql://postgres:zvgK6kProVGys5w@localhost:15432/flow_forecaster?sslmode=disable"

# Verificar
echo $DATABASE_URL
```

**Credenciais do seu PostgreSQL**:
- Username: `postgres`
- Password: `zvgK6kProVGys5w`
- Host: `localhost` (via proxy)
- Port: `15432` (porta local do proxy)
- Database: `flow_forecaster`

### Passo 4: Dry Run (Teste)

```bash
# Teste sem escrever dados
python migrate_to_postgres.py --dry-run

# Output esperado:
# ======================================================================
# SQLite to PostgreSQL Migration
# ======================================================================
#
# 📂 Source (SQLite): forecaster.db
# 🐘 Destination (PostgreSQL): postgresql://...
#
# ⚠️  DRY RUN MODE - No data will be written
#
# 🔌 Connecting to databases...
#    ✅ Connected to SQLite
#    ✅ Connected to PostgreSQL
#
# 📊 Counting records in SQLite...
#    👥 Users: 5
#    📁 Projects: 12
#    📈 Forecasts: 45
#    ✓  Actuals: 120
#    📦 Total records: 182
```

### Passo 5: Migração Real

```bash
# Migração real (vai pedir confirmação)
python migrate_to_postgres.py

# Digite 'yes' quando perguntar:
# Continue? (yes/no): yes

# Output:
# 👥 Migrating 5 users...
#    ✅ 5 users migrated
#
# 📁 Migrating 12 projects...
#    ✅ 12 projects migrated
#
# 📈 Migrating 45 forecasts...
#    ✅ 45 forecasts migrated
#
# ✓  Migrating 120 actuals...
#    ✅ 120 actuals migrated
#
# ======================================================================
# 🎉 MIGRATION COMPLETE!
# ======================================================================
#
# 🔍 Verifying migration...
#    PostgreSQL Users: 5 (expected 5)
#    PostgreSQL Projects: 12 (expected 12)
#    PostgreSQL Forecasts: 45 (expected 45)
#    PostgreSQL Actuals: 120 (expected 120)
#    ✅ Verification passed!
```

### Passo 6: Parar Proxy

```bash
# No Terminal 1 (onde o proxy está rodando)
# Pressione Ctrl+C
```

### Passo 7: Verificar no Fly.io

```bash
# Conectar ao PostgreSQL
fly postgres connect -a flow-forecaster-db

# No psql:
\c flow_forecaster

-- Contar registros
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Projects', COUNT(*) FROM projects
UNION ALL
SELECT 'Forecasts', COUNT(*) FROM forecasts
UNION ALL
SELECT 'Actuals', COUNT(*) FROM actuals;

\q
```

✅ **Migração completa!**

---

## 🔍 Validação

### Comparar Contagens

```bash
# Local (SQLite)
sqlite3 forecaster.db "SELECT COUNT(*) FROM users;"
sqlite3 forecaster.db "SELECT COUNT(*) FROM projects;"
sqlite3 forecaster.db "SELECT COUNT(*) FROM forecasts;"

# Fly.io (PostgreSQL) - via proxy
fly proxy 15432:5432 -a flow-forecaster-db

# Outro terminal:
psql postgresql://postgres:zvgK6kProVGys5w@localhost:15432/flow_forecaster \
  -c "SELECT COUNT(*) FROM users;"
```

**Os números devem ser iguais!**

---

## ⚠️ Troubleshooting

### Erro: "Failed to connect to PostgreSQL"

**Solução**: Verificar se o proxy está rodando

```bash
# Ver processos do proxy
ps aux | grep "fly proxy"

# Reiniciar proxy
fly proxy 15432:5432 -a flow-forecaster-db
```

### Erro: "database does not exist"

**Solução**: Criar database

```bash
fly postgres connect -a flow-forecaster-db

# No psql:
CREATE DATABASE flow_forecaster;
\q
```

### Erro: "relation 'users' does not exist"

**Solução**: Criar tabelas

```bash
# Via proxy
export DATABASE_URL="postgresql://postgres:zvgK6kProVGys5w@localhost:15432/flow_forecaster?sslmode=disable"
python -c "from database import init_db; init_db()"
```

### Migração parcialmente completada

**Solução**: Limpar e tentar novamente

```bash
fly postgres connect -a flow-forecaster-db

\c flow_forecaster
TRUNCATE TABLE actuals, forecasts, projects, users CASCADE;
\q

# Executar migração novamente
python migrate_to_postgres.py
```

---

## 📋 Checklist

### Antes
- [ ] Backup do SQLite criado
- [ ] PostgreSQL criado no Fly.io
- [ ] Fly CLI instalado e autenticado

### Durante
- [ ] Proxy rodando
- [ ] Dry run passou
- [ ] Migração executada
- [ ] Verificação passou

### Depois
- [ ] Contagens conferidas
- [ ] Login testado
- [ ] Deploy feito com PostgreSQL

---

## 💡 Comandos Úteis

```bash
# Ver tamanho do SQLite
ls -lh forecaster.db

# Contar registros SQLite
sqlite3 forecaster.db "SELECT COUNT(*) FROM users;"

# Conectar PostgreSQL Fly.io
fly postgres connect -a flow-forecaster-db

# Ver databases
fly postgres connect -a flow-forecaster-db -c "\l"

# Backup PostgreSQL
fly postgres backup create -a flow-forecaster-db
fly postgres backup list -a flow-forecaster-db
```

---

## 🆘 Precisa de Ajuda?

1. Ver logs do script: `python migrate_to_postgres.py --dry-run`
2. Testar conexão: `fly postgres connect -a flow-forecaster-db`
3. Ver documentação: [Fly PostgreSQL Docs](https://fly.io/docs/postgres/)

---

**Criado por**: Claude (Anthropic AI Assistant)
**Última atualização**: 2025-01-06
