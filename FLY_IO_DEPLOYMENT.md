# Flow Forecaster - Fly.io Deployment Guide

Guia completo para fazer deploy da arquitetura assíncrona do Flow Forecaster no Fly.io.

## Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Configuração Inicial](#configuração-inicial)
- [Deploy](#deploy)
- [Pós-Deploy](#pós-deploy)
- [Operações](#operações)
- [Troubleshooting](#troubleshooting)
- [Custos](#custos)

## Visão Geral

### Arquitetura no Fly.io

```
┌─────────────────────────────────────────────────────────────┐
│                     Fly.io Infrastructure                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Web Machine │         │Worker Machine│                  │
│  │  (512MB RAM) │         │  (1GB RAM)   │                  │
│  │              │         │              │                  │
│  │  Gunicorn    │◄────────┤   Celery     │                  │
│  │  + Flask     │         │   Worker     │                  │
│  └───────┬──────┘         └──────┬───────┘                  │
│          │                       │                           │
│          ▼                       ▼                           │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  PostgreSQL  │         │    Redis     │                  │
│  │   Database   │         │  (Upstash)   │                  │
│  │flow-forecaster-db│     │              │                  │
│  └──────────────┘         └──────────────┘                  │
│                                                               │
│  Internet → https://flow-forecaster.fly.dev                  │
└─────────────────────────────────────────────────────────────┘
```

### O que será criado

- **1 Web Machine**: Flask + Gunicorn (512MB RAM, 1 CPU)
- **1 Worker Machine**: Celery worker (1GB RAM, 1 CPU)
- **PostgreSQL Database**: flow-forecaster-db (já criado)
- **Redis**: Upstash Redis para broker/backend do Celery
- **Auto-scaling**: Máquinas podem escalar baseado em tráfego

## Pré-requisitos

### 1. Fly CLI Instalado

```bash
# Verificar se já está instalado
fly version

# Se não estiver, instalar
curl -L https://fly.io/install.sh | sh

# Adicionar ao PATH (Linux/macOS)
export PATH="$HOME/.fly/bin:$PATH"
```

### 2. Conta Fly.io Autenticada

```bash
# Login
fly auth login

# Verificar autenticação
fly auth whoami
```

### 3. PostgreSQL Criado

✅ **Você já criou**: `flow-forecaster-db`

Credenciais:
```
Username: postgres
Password: zvgK6kProVGys5w
Hostname: flow-forecaster-db.internal
Connection string: postgres://postgres:zvgK6kProVGys5w@flow-forecaster-db.flycast:5432
```

### 4. Código Atualizado

```bash
# Certifique-se de estar no branch com as mudanças
git checkout claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS

# Ou faça merge para main
git checkout main
git merge claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS
```

## Configuração Inicial

### Passo 1: Attach PostgreSQL

```bash
# Conectar o banco de dados ao app
fly postgres attach flow-forecaster-db --app flow-forecaster
```

**Output esperado:**
```
Postgres cluster flow-forecaster-db is now attached to flow-forecaster
The following secret was added to flow-forecaster:
  DATABASE_URL=postgres://...
```

### Passo 2: Criar Redis (Upstash)

**Opção A - Via Fly Redis (Recomendado)**:

```bash
# Criar Redis via Upstash (integrado no Fly.io)
fly redis create --name flow-forecaster-redis --region gru
```

**Opção B - Upstash Dashboard**:

1. Acesse https://console.upstash.com/
2. Crie um novo Redis database
3. Região: São Paulo (GRU) ou mais próxima
4. Copie a connection string

### Passo 3: Configurar Secrets

```bash
# SECRET_KEY para Flask
fly secrets set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app flow-forecaster

# Ambiente de produção
fly secrets set FLASK_ENV=production --app flow-forecaster

# Redis URLs (substituir com suas credenciais)
# Formato: redis://default:PASSWORD@HOST:PORT
fly secrets set CELERY_BROKER_URL="redis://default:YOUR_PASSWORD@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster

fly secrets set CELERY_RESULT_BACKEND="redis://default:YOUR_PASSWORD@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster
```

**⚠️ Importante**: Substitua `YOUR_PASSWORD` e o hostname com os valores reais do seu Redis.

**Se usar Upstash Redis criado via Fly CLI**, o formato é:
```bash
fly secrets set CELERY_BROKER_URL="redis://default:PASSWORD@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster

fly secrets set CELERY_RESULT_BACKEND="redis://default:PASSWORD@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster
```

### Passo 4: Verificar Secrets

```bash
# Listar secrets configurados (valores não são exibidos)
fly secrets list --app flow-forecaster
```

**Output esperado:**
```
NAME                      DIGEST             UPDATED AT
DATABASE_URL              xxx                xxx
SECRET_KEY                xxx                xxx
FLASK_ENV                 xxx                xxx
CELERY_BROKER_URL         xxx                xxx
CELERY_RESULT_BACKEND     xxx                xxx
```

## Deploy

### Método 1: Script Automatizado (Recomendado)

```bash
# Deploy completo (deploy + migrate + status)
./fly_deploy.sh full

# Ou passo a passo:
./fly_deploy.sh deploy     # Deploy da aplicação
./fly_deploy.sh migrate    # Inicializar banco de dados
./fly_deploy.sh status     # Ver status
```

### Método 2: Manual

```bash
# 1. Deploy da aplicação
fly deploy --ha=false

# 2. Escalar máquinas
fly scale count web=1 worker=1 --app flow-forecaster

# 3. Inicializar banco de dados
fly ssh console --app flow-forecaster -C "python -c 'from database import init_db; init_db()'"

# 4. Ver status
fly status --app flow-forecaster
```

### O que acontece durante o deploy

1. **Build**: Fly.io constrói a imagem Docker
2. **Deploy**: Cria máquinas web e worker
3. **Health Check**: Verifica `/api/async/health` endpoint
4. **Routing**: Configura DNS para flow-forecaster.fly.dev

**Tempo estimado**: 3-5 minutos

## Pós-Deploy

### Verificar Deployment

```bash
# Status das máquinas
fly vm status --app flow-forecaster

# Logs em tempo real
fly logs --app flow-forecaster

# Verificar health check
curl https://flow-forecaster.fly.dev/api/async/health
```

**Output esperado do health check**:
```json
{
  "status": "healthy",
  "redis": "connected",
  "database": "connected",
  "celery_workers": 1,
  "timestamp": "2025-01-06T12:00:00"
}
```

### Testar Funcionalidades

```bash
# 1. Acessar aplicação
open https://flow-forecaster.fly.dev

# 2. Testar simulação assíncrona
curl -X POST https://flow-forecaster.fly.dev/api/async/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "targetOutcome": 100,
    "pBest": 10,
    "pWorst": 50,
    "pLikely": 25,
    "sCurveSize": 3,
    "nSimulations": 1000,
    "confidence": 0.85
  }'

# Response: {"task_id": "xxx-xxx-xxx", "status": "PENDING"}

# 3. Verificar status da tarefa
curl https://flow-forecaster.fly.dev/api/tasks/TASK_ID
```

### Monitorar Celery Workers

```bash
# Ver logs dos workers
fly logs --app flow-forecaster | grep worker

# SSH para verificar workers
fly ssh console --app flow-forecaster

# Dentro do container:
celery -A celery_app inspect active
celery -A celery_app inspect stats
```

## Operações

### Ver Logs

```bash
# Logs em tempo real
fly logs --app flow-forecaster

# Últimas 100 linhas
fly logs --app flow-forecaster -n 100

# Filtrar por processo
fly logs --app flow-forecaster | grep web
fly logs --app flow-forecaster | grep worker
```

### Escalar Aplicação

```bash
# Escalar para 2 web + 2 workers
fly scale count web=2 worker=2 --app flow-forecaster

# Escalar apenas web
fly scale count web=3 --app flow-forecaster

# Aumentar recursos (memória)
fly scale vm shared-cpu-2x --app flow-forecaster

# Ver configuração atual
fly scale show --app flow-forecaster
```

### Acessar Container via SSH

```bash
# Console interativo
fly ssh console --app flow-forecaster

# Executar comando específico
fly ssh console --app flow-forecaster -C "python manage.py shell"

# Ver variáveis de ambiente
fly ssh console --app flow-forecaster -C "env | grep CELERY"
```

### Restart da Aplicação

```bash
# Restart de todas as máquinas
fly apps restart flow-forecaster

# Restart de máquinas específicas
fly machine restart MACHINE_ID --app flow-forecaster
```

### Migrations de Banco

```bash
# Via SSH
fly ssh console --app flow-forecaster -C "python -c 'from database import init_db; init_db()'"

# Ou com Alembic (se configurado)
fly ssh console --app flow-forecaster -C "alembic upgrade head"
```

### Backup do Banco de Dados

```bash
# Criar snapshot do PostgreSQL
fly postgres backup create --app flow-forecaster-db

# Listar backups
fly postgres backup list --app flow-forecaster-db

# Restaurar backup
fly postgres backup restore <backup-id> --app flow-forecaster-db
```

### Atualizar Secrets

```bash
# Atualizar um secret
fly secrets set SECRET_KEY=new-value --app flow-forecaster

# Remover um secret
fly secrets unset SECRET_NAME --app flow-forecaster

# Listar secrets
fly secrets list --app flow-forecaster
```

## Troubleshooting

### Máquinas não iniciam

**Sintoma**: Máquinas ficam em estado `starting` ou `failed`

**Verificar**:

```bash
# Ver logs de erro
fly logs --app flow-forecaster

# Ver status das máquinas
fly vm status --app flow-forecaster

# Ver health check
fly checks list --app flow-forecaster
```

**Soluções comuns**:

1. **Secrets faltando**: Verificar se todos os secrets estão configurados
   ```bash
   fly secrets list --app flow-forecaster
   ```

2. **Health check falhando**: Verificar endpoint `/api/async/health`
   ```bash
   fly ssh console --app flow-forecaster -C "curl localhost:8080/api/async/health"
   ```

3. **Porta errada**: Verificar se app usa porta 8080
   ```bash
   # No fly.toml deve ter:
   internal_port = 8080
   ```

### Celery Workers não processam tarefas

**Sintoma**: Tarefas ficam em `PENDING` indefinidamente

**Verificar**:

```bash
# Ver se worker está rodando
fly vm status --app flow-forecaster | grep worker

# Ver logs do worker
fly logs --app flow-forecaster | grep worker

# Verificar conexão Redis
fly ssh console --app flow-forecaster -C "celery -A celery_app inspect ping"
```

**Soluções**:

1. **Redis não conectado**: Verificar `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND`
   ```bash
   fly secrets list --app flow-forecaster | grep CELERY
   ```

2. **Worker não escalado**: Garantir que worker machine existe
   ```bash
   fly scale count worker=1 --app flow-forecaster
   ```

3. **Restart do worker**:
   ```bash
   fly machine restart WORKER_MACHINE_ID --app flow-forecaster
   ```

### Erros de Banco de Dados

**Sintoma**: `FATAL: database "forecaster" does not exist`

**Solução**:

```bash
# Criar database
fly postgres connect --app flow-forecaster-db

# No psql:
CREATE DATABASE forecaster;
\q

# Inicializar tabelas
fly ssh console --app flow-forecaster -C "python -c 'from database import init_db; init_db()'"
```

### Performance Lenta

**Verificar recursos**:

```bash
# Ver uso de recursos
fly vm status --app flow-forecaster

# Métricas de performance
fly dashboard metrics --app flow-forecaster
```

**Soluções**:

1. **Escalar horizontalmente** (mais máquinas):
   ```bash
   fly scale count web=2 worker=2 --app flow-forecaster
   ```

2. **Escalar verticalmente** (mais recursos):
   ```bash
   fly scale vm shared-cpu-2x --memory 1024 --app flow-forecaster
   ```

3. **Otimizar PostgreSQL**:
   ```bash
   # Aumentar plan do Postgres
   fly postgres update --app flow-forecaster-db
   ```

### Erros de Memória

**Sintoma**: `MemoryError` ou OOM (Out of Memory)

**Verificar**:

```bash
# Ver uso de memória
fly ssh console --app flow-forecaster -C "free -h"

# Ver processos
fly ssh console --app flow-forecaster -C "ps aux --sort=-%mem | head"
```

**Soluções**:

1. **Aumentar memória das máquinas**:
   ```bash
   # Web: 512MB → 1GB
   fly scale vm shared-cpu-1x --memory 1024 --app flow-forecaster

   # Worker: 1GB → 2GB
   fly scale vm shared-cpu-1x --memory 2048 --app flow-forecaster
   ```

2. **Limitar workers do Celery**:
   ```bash
   # Editar fly.toml, reduzir concurrency:
   worker = "celery -A celery_app worker --concurrency=2"
   ```

3. **Limitar simulações**:
   ```python
   # app_async_endpoints.py
   MAX_SIMULATIONS = 5000  # Reduzir de 10000
   ```

### SSL/TLS Errors

**Sintoma**: Certificado inválido ou erro HTTPS

**Verificar**:

```bash
# Ver certificados
fly certs list --app flow-forecaster

# Ver status do certificado
fly certs show flow-forecaster.fly.dev --app flow-forecaster
```

**Soluções**:

1. **Aguardar provisioning**: Certificados podem levar alguns minutos
2. **Forçar HTTPS**: Já configurado em `fly.toml` (`force_https = true`)

### Ver Logs de Erro Detalhados

```bash
# Logs com stack traces
fly logs --app flow-forecaster | grep -A 20 "ERROR"

# Logs do Gunicorn
fly logs --app flow-forecaster | grep gunicorn

# Logs do Celery
fly logs --app flow-forecaster | grep celery
```

## Custos

### Estimativa Mensal (Fly.io)

**Configuração Mínima** (1 web + 1 worker):

| Recurso | Configuração | Custo/mês |
|---------|-------------|-----------|
| Web Machine | shared-cpu-1x, 512MB | ~$5 |
| Worker Machine | shared-cpu-1x, 1GB | ~$10 |
| PostgreSQL | Hobby tier | $0 (1GB grátis) |
| Redis (Upstash) | Free tier | $0 (10k reqs/dia) |
| **Total** | | **~$15/mês** |

**Configuração Produção** (2 web + 2 workers):

| Recurso | Configuração | Custo/mês |
|---------|-------------|-----------|
| Web Machines (2x) | shared-cpu-1x, 512MB | ~$10 |
| Worker Machines (2x) | shared-cpu-1x, 1GB | ~$20 |
| PostgreSQL | Standard tier | ~$15 |
| Redis (Upstash) | Pro tier | ~$10 |
| **Total** | | **~$55/mês** |

**Configuração Enterprise** (4 web + 4 workers + HA):

| Recurso | Configuração | Custo/mês |
|---------|-------------|-----------|
| Web Machines (4x) | shared-cpu-2x, 1GB | ~$40 |
| Worker Machines (4x) | shared-cpu-2x, 2GB | ~$80 |
| PostgreSQL | HA cluster | ~$40 |
| Redis (Upstash) | Enterprise | ~$30 |
| **Total** | | **~$190/mês** |

### Otimizar Custos

1. **Auto-stop/start**: Já configurado em `fly.toml`
   ```toml
   auto_stop_machines = "stop"
   auto_start_machines = true
   min_machines_running = 0
   ```

2. **Usar free tier**: PostgreSQL e Redis têm tiers gratuitos

3. **Escalar conforme necessário**: Começar pequeno, escalar sob demanda

4. **Monitorar uso**:
   ```bash
   fly dashboard metrics --app flow-forecaster
   ```

## Comandos Úteis

```bash
# Status geral
fly status --app flow-forecaster

# Máquinas
fly vm status --app flow-forecaster
fly machine list --app flow-forecaster

# Logs
fly logs --app flow-forecaster
fly logs -a flow-forecaster --follow

# Scaling
fly scale show --app flow-forecaster
fly scale count web=2 worker=2 --app flow-forecaster

# SSH
fly ssh console --app flow-forecaster
fly ssh issue --app flow-forecaster

# Secrets
fly secrets list --app flow-forecaster
fly secrets set KEY=VALUE --app flow-forecaster

# PostgreSQL
fly postgres connect --app flow-forecaster-db
fly postgres backup list --app flow-forecaster-db

# Deploy
fly deploy
fly deploy --ha=false  # Sem high availability

# Dashboard
fly dashboard --app flow-forecaster

# Monitoring
fly dashboard metrics --app flow-forecaster
```

## Próximos Passos

Após deployment bem-sucedido:

1. ✅ **Configurar domínio customizado** (opcional):
   ```bash
   fly certs add seu-dominio.com --app flow-forecaster
   ```

2. ✅ **Configurar monitoramento externo**:
   - UptimeRobot
   - Better Stack
   - Pingdom

3. ✅ **Configurar backups automáticos**:
   ```bash
   # PostgreSQL backups automáticos (já ativo)
   fly postgres backup list --app flow-forecaster-db
   ```

4. ✅ **Testes de carga**:
   ```bash
   # Do seu computador local
   HOST=https://flow-forecaster.fly.dev ./run_load_tests.sh baseline
   ```

5. ✅ **Configurar CI/CD**:
   - GitHub Actions para deploy automático
   - Ver: `.github/workflows/fly-deploy.yml` (criar)

## Recursos

- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io PostgreSQL](https://fly.io/docs/postgres/)
- [Fly.io Redis](https://fly.io/docs/reference/redis/)
- [Upstash Redis](https://upstash.com/)
- [Celery Documentation](https://docs.celeryq.dev/)

## Suporte

- Fly.io Community: https://community.fly.io/
- Flow Forecaster Issues: https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/issues
