# Flow Forecaster - Deploy Quickstart

Guia rápido para fazer deploy no Fly.io em 5 minutos.

## ⚡ Pré-requisitos

✅ PostgreSQL criado: `flow-forecaster-db`
✅ Código atualizado no branch: `claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS`

## 🚀 Deploy em 5 Passos

### 1. Instalar Fly CLI (se necessário)

```bash
# Linux/macOS
curl -L https://fly.io/install.sh | sh

# Adicionar ao PATH
export PATH="$HOME/.fly/bin:$PATH"

# Verificar instalação
fly version
```

### 2. Login no Fly.io

```bash
fly auth login
```

### 3. Configurar Serviços

```bash
# A. Attach PostgreSQL (já criado)
fly postgres attach flow-forecaster-db --app flow-forecaster

# B. Criar Redis (Upstash)
fly redis create --name flow-forecaster-redis --region gru

# Anote a connection string que aparece!
# Formato: redis://default:PASSWORD@HOST:6379
```

### 4. Configurar Secrets

```bash
# Secret Key
fly secrets set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app flow-forecaster

# Flask Environment
fly secrets set FLASK_ENV=production --app flow-forecaster

# Redis URLs (SUBSTITUIR com suas credenciais do passo 3)
fly secrets set CELERY_BROKER_URL="redis://default:SUA_SENHA@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster

fly secrets set CELERY_RESULT_BACKEND="redis://default:SUA_SENHA@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster
```

**⚠️ Importante**: Substituir `SUA_SENHA` e o hostname com os valores reais do Redis!

### 5. Deploy!

```bash
# Opção A: Script automatizado (recomendado)
./fly_deploy.sh full

# Opção B: Manual
fly deploy --ha=false
fly scale count web=1 worker=1 --app flow-forecaster
```

## ✅ Verificar Deployment

```bash
# Ver status
fly status --app flow-forecaster

# Ver logs
fly logs --app flow-forecaster

# Testar health check
curl https://flow-forecaster.fly.dev/api/async/health
```

**Output esperado**:
```json
{
  "status": "healthy",
  "redis": "connected",
  "database": "connected",
  "celery_workers": 1
}
```

## 🎯 Acessar Aplicação

🌐 **URL**: https://flow-forecaster.fly.dev

## 📊 Comandos Úteis

```bash
# Ver logs em tempo real
fly logs --app flow-forecaster --follow

# SSH no container
fly ssh console --app flow-forecaster

# Escalar para 2 web + 2 workers
fly scale count web=2 worker=2 --app flow-forecaster

# Restart
fly apps restart flow-forecaster

# Ver métricas
fly dashboard metrics --app flow-forecaster
```

## ⚠️ Troubleshooting Rápido

### Redis não conecta

```bash
# Verificar secrets
fly secrets list --app flow-forecaster | grep CELERY

# Deve mostrar:
# CELERY_BROKER_URL
# CELERY_RESULT_BACKEND
```

Se não aparecer, configure novamente (passo 4).

### Workers não processam tarefas

```bash
# Ver se worker está rodando
fly vm status --app flow-forecaster | grep worker

# Se não aparecer, escalar:
fly scale count worker=1 --app flow-forecaster
```

### Erro 503 ou 500

```bash
# Ver logs de erro
fly logs --app flow-forecaster | grep ERROR

# Verificar health check
fly checks list --app flow-forecaster
```

## 💰 Custo

**Configuração básica** (1 web + 1 worker):
- Web: ~$5/mês
- Worker: ~$10/mês
- PostgreSQL: $0 (free tier)
- Redis: $0 (free tier)

**Total: ~$15/mês**

## 📚 Documentação Completa

Para mais detalhes, ver:
- [FLY_IO_DEPLOYMENT.md](FLY_IO_DEPLOYMENT.md) - Guia completo
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Outras opções de deploy

## 🆘 Precisa de Ajuda?

1. Ver logs: `fly logs --app flow-forecaster`
2. Ver status: `fly status --app flow-forecaster`
3. SSH: `fly ssh console --app flow-forecaster`
4. Documentação: https://fly.io/docs/

---

**Criado por**: Claude (Anthropic AI Assistant)
**Última atualização**: 2025-01-06
