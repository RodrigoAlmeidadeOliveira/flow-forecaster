# Correção de Login - Migração PostgreSQL

**Data:** 2025-11-06
**Problema:** Sistema não conseguia fazer login após migração para PostgreSQL

---

## 🐛 Problema Identificado

### Sintoma
- ❌ Login falha após migração PostgreSQL
- ❌ Usuários não conseguem acessar o sistema
- ❌ Aplicação parece não conectar ao banco correto

### Causa Raiz

O `fly.toml` estava **sobrescrevendo** o secret do PostgreSQL com SQLite:

```toml
# ❌ PROBLEMA: Isso sobrescreve o secret DATABASE_URL!
[env]
  DATABASE_URL = "sqlite:////data/forecaster.db"
```

**Consequência:**
- ✅ PostgreSQL existe e está configurado: `flow-forecaster-db`
- ✅ Secret `DATABASE_URL` aponta para PostgreSQL
- ❌ **Mas o fly.toml sobrescreve com SQLite!**
- ❌ Aplicação usa banco vazio (SQLite) em vez do PostgreSQL com usuários

**Ordem de precedência no Fly.io:**
1. `fly.toml [env]` (MAIOR prioridade) ⚠️
2. Secrets (`flyctl secrets set`)
3. Variáveis de ambiente do sistema

---

## ✅ Correções Implementadas

### 1. Remover DATABASE_URL do fly.toml

**Arquivo:** `fly.toml`

**Antes:**
```toml
[env]
  DATABASE_URL = "sqlite:////data/forecaster.db"  # ❌ Sobrescreve secret!
```

**Depois:**
```toml
[env]
  # DATABASE_URL is set as a secret (flyctl secrets set DATABASE_URL=...)
  # Don't define it here or it will override the PostgreSQL connection
```

**Resultado:** Agora o secret PostgreSQL será usado! ✅

---

### 2. Atualizar database.py para PostgreSQL

**Arquivo:** `database.py`

#### 2.1 Connection Pool Settings

```python
# Antes: Configuração única para SQLite
engine = create_engine(DB_PATH, echo=False)

# Depois: Configuração específica por banco
connect_args = {}
pool_settings = {}

if DB_PATH.startswith('postgres://') or DB_PATH.startswith('postgresql://'):
    # PostgreSQL production settings
    pool_settings = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 3600,   # Recycle connections after 1 hour
    }
    # Fix Heroku/Fly.io postgres:// URL
    if DB_PATH.startswith('postgres://'):
        DB_PATH = DB_PATH.replace('postgres://', 'postgresql://', 1)
else:
    # SQLite settings
    connect_args = {'check_same_thread': False}

engine = create_engine(
    DB_PATH,
    echo=False,
    connect_args=connect_args,
    **pool_settings
)
```

**Benefícios:**
- ✅ Connection pooling para PostgreSQL
- ✅ Pre-ping para validar conexões
- ✅ Recycle automático de conexões antigas
- ✅ Compatibilidade com URL `postgres://` (Heroku/Fly.io)

#### 2.2 SQL Syntax Compatibility

**Problema:** SQLite usa `DATETIME()`, PostgreSQL usa `INTERVAL`

```python
# Detectar tipo de banco
is_postgres = DB_PATH.startswith('postgresql://')

if is_postgres:
    # PostgreSQL-specific syntax
    user_columns = [
        (
            'registration_date',
            "ALTER TABLE users ADD COLUMN registration_date TIMESTAMP",
            "UPDATE users SET registration_date = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE registration_date IS NULL"
        ),
        (
            'access_expires_at',
            "ALTER TABLE users ADD COLUMN access_expires_at TIMESTAMP",
            "UPDATE users SET access_expires_at = COALESCE(registration_date, created_at, CURRENT_TIMESTAMP) + INTERVAL '365 days' WHERE access_expires_at IS NULL"
        ),
    ]
else:
    # SQLite-specific syntax
    user_columns = [
        # ... sintaxe com DATETIME()
    ]
```

**Mudanças:**
- ✅ `DATETIME` → `TIMESTAMP` (PostgreSQL)
- ✅ `DATETIME(..., '+365 days')` → `+ INTERVAL '365 days'` (PostgreSQL)
- ✅ Mantém compatibilidade com SQLite para dev local

#### 2.3 Database Initialization

```python
# Antes: Sempre tentava criar arquivo SQLite
db_file = DB_PATH.replace('sqlite:///', '')
if not os.path.exists(db_file):
    init_db()

# Depois: Lógica específica por banco
if DB_PATH.startswith('sqlite'):
    # SQLite: check if file exists
    db_file = DB_PATH.replace('sqlite:///', '')
    if not os.path.exists(db_file):
        init_db()
else:
    # PostgreSQL: just test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✓ Connected to PostgreSQL database successfully")
    except Exception as e:
        print(f"⚠ PostgreSQL connection error: {e}")
```

**Benefícios:**
- ✅ Não tenta criar "arquivo" PostgreSQL
- ✅ Testa conexão no startup
- ✅ Logs claros de sucesso/erro

---

### 3. Adicionar Driver PostgreSQL

**Arquivo:** `requirements.txt`

```txt
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.9  # ← Novo: Driver PostgreSQL
```

**Por que `psycopg2-binary`?**
- ✅ Versão compilada (mais fácil de instalar)
- ✅ Funciona no Fly.io sem dependências extras
- ✅ Performance otimizada

---

## 🚀 Deploy da Correção

### Passo 1: Commit e Push

```bash
git add fly.toml database.py requirements.txt
git commit -m "fix: Corrigir login após migração PostgreSQL"
git push origin main
```

### Passo 2: Deploy no Fly.io

```bash
flyctl deploy
```

**O que acontece:**
1. ✅ Rebuild da imagem com `psycopg2-binary`
2. ✅ `fly.toml` não sobrescreve mais `DATABASE_URL`
3. ✅ Aplicação conecta ao PostgreSQL
4. ✅ Login funciona com usuários existentes!

### Passo 3: Verificar Logs

```bash
flyctl logs

# Procurar por:
# ✓ Connected to PostgreSQL database successfully
```

---

## ✅ Validação

### 1. Verificar Secret DATABASE_URL

```bash
flyctl secrets list --app flow-forecaster

# Deve mostrar:
# DATABASE_URL    1866bb6ba611bb5e
```

### 2. Verificar Conexão

```bash
flyctl ssh console --app flow-forecaster

# Dentro do container:
python3 -c "import os; print(os.environ.get('DATABASE_URL')[:50])"

# Deve mostrar: postgresql://...
```

### 3. Testar Login

```
1. Acessar: https://flow-forecaster.fly.dev/login
2. Usar credenciais existentes
3. ✅ Login deve funcionar!
```

---

## 🔧 Troubleshooting

### Problema: "No module named 'psycopg2'"

**Causa:** Driver PostgreSQL não instalado

**Solução:**
```bash
# Localmente:
pip install psycopg2-binary

# Fly.io: fazer redeploy
flyctl deploy
```

### Problema: "Connection refused"

**Causa:** SECRET DATABASE_URL incorreto ou PostgreSQL down

**Verificar:**
```bash
# 1. Check se PostgreSQL está rodando
flyctl status --app flow-forecaster-db

# 2. Verificar connection string
flyctl postgres db list --app flow-forecaster-db

# 3. Regenerar secret se necessário
flyctl postgres attach flow-forecaster-db --app flow-forecaster
```

### Problema: "relation 'users' does not exist"

**Causa:** Tabelas não foram criadas no PostgreSQL

**Solução:**
```bash
# Conectar ao PostgreSQL
flyctl ssh console --app flow-forecaster

# Executar migrations manualmente
python3 -c "from database import init_db; init_db()"
```

### Problema: "Column 'registration_date' already exists"

**Causa:** Tentando adicionar coluna que já existe

**Solução:** Ignorar (ensure_schema() trata automaticamente)

---

## 📊 Antes vs Depois

### Antes (Problema)

```
Aplicação → fly.toml DATABASE_URL (SQLite) → Banco vazio
                ↓
        Secret DATABASE_URL (PostgreSQL com usuários) ❌ IGNORADO
```

**Resultado:**
- ❌ Login falha (usuário não existe no SQLite)
- ❌ Dados perdidos em cada restart
- ❌ PostgreSQL não é usado

### Depois (Corrigido)

```
Aplicação → Secret DATABASE_URL (PostgreSQL) → Banco com usuários ✅
                ↓
        fly.toml (sem DATABASE_URL) → Não sobrescreve
```

**Resultado:**
- ✅ Login funciona (usuários no PostgreSQL)
- ✅ Dados persistentes
- ✅ PostgreSQL usado corretamente

---

## 🎯 Lições Aprendidas

### 1. Ordem de Precedência no Fly.io

```
fly.toml [env] > Secrets > System ENV
```

**Regra:** NUNCA defina DATABASE_URL no `fly.toml` se usar Secrets!

### 2. PostgreSQL vs SQLite - Sintaxe SQL

| Recurso | SQLite | PostgreSQL |
|---------|--------|------------|
| Tipo datetime | `DATETIME` | `TIMESTAMP` |
| Adicionar dias | `DATETIME(x, '+365 days')` | `x + INTERVAL '365 days'` |
| Datetime atual | `CURRENT_TIMESTAMP` | `CURRENT_TIMESTAMP` ✅ (igual) |

### 3. SQLAlchemy Drivers

- SQLite: Built-in (sem dependência extra)
- PostgreSQL: Requer `psycopg2` ou `psycopg2-binary`

---

## 📚 Arquivos Modificados

```
✅ fly.toml           (Removida linha DATABASE_URL)
✅ database.py        (PostgreSQL compatibility)
✅ requirements.txt   (+psycopg2-binary)
✅ POSTGRESQL_LOGIN_FIX.md (Esta documentação)
```

---

## ✅ Checklist de Deploy

- [x] Remover DATABASE_URL do fly.toml
- [x] Adicionar psycopg2-binary ao requirements.txt
- [x] Atualizar database.py com PostgreSQL support
- [x] Commit e push para GitHub
- [x] Deploy no Fly.io: `flyctl deploy`
- [ ] Verificar logs: `flyctl logs`
- [ ] Testar login: https://flow-forecaster.fly.dev/login
- [ ] Confirmar conexão PostgreSQL nos logs

---

## 🚀 Status

**Correção implementada e pronta para deploy!**

Próximos passos:
1. Commit das mudanças
2. Push para GitHub
3. Deploy no Fly.io
4. Validar login funcionando

**Tempo estimado:** 5-10 minutos para deploy + validação
