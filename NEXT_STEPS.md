# 🚀 Próximos Passos - Deploy no Fly.io

## ✅ Já Feito

1. ✅ PostgreSQL criado e attached
   - DATABASE_URL já configurado automaticamente
2. ✅ Redis (Upstash) criado
   - URL: `redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379`

## 📋 Execute Agora (3 comandos)

### 1. Configurar Secrets do Celery

Cole estes comandos no terminal:

```bash
# SECRET_KEY para Flask
fly secrets set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app flow-forecaster

# Ambiente de produção
fly secrets set FLASK_ENV=production --app flow-forecaster

# Redis URL para Celery (BROKER)
fly secrets set CELERY_BROKER_URL="redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster

# Redis URL para Celery (RESULT BACKEND)
fly secrets set CELERY_RESULT_BACKEND="redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster
```

### 2. Fazer o Deploy

```bash
# Deploy completo
./fly_deploy.sh full

# Ou manual:
fly deploy --ha=false
fly scale count web=1 worker=1 --app flow-forecaster
```

### 3. Verificar

```bash
# Ver status
fly status --app flow-forecaster

# Ver logs
fly logs --app flow-forecaster

# Testar health check
curl https://flow-forecaster.fly.dev/api/async/health
```

## 📊 Após Deploy

Acesse a aplicação:
- **URL**: https://flow-forecaster.fly.dev
- **Health Check**: https://flow-forecaster.fly.dev/api/async/health

## 🔍 Monitoramento

```bash
# Logs em tempo real
fly logs --app flow-forecaster --follow

# Status das máquinas
fly vm status --app flow-forecaster

# Dashboard de métricas
fly dashboard metrics --app flow-forecaster
```

## ⚙️ Scaling (quando necessário)

```bash
# Escalar para 2 web + 2 workers
fly scale count web=2 worker=2 --app flow-forecaster

# Ver configuração atual
fly scale show --app flow-forecaster
```

## 📝 Resumo de Credenciais

**PostgreSQL**:
```
DATABASE_URL=postgres://flow_forecaster:4ZRplUZglrnfO3Y@flow-forecaster-db.flycast:5432/flow_forecaster?sslmode=disable
```

**Redis**:
```
redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379
```

## 💰 Custos Estimados

Com 1 web + 1 worker:
- Web machine: ~$5/mês
- Worker machine: ~$10/mês
- PostgreSQL: $0 (free tier, até 1GB)
- Redis: $0.20 por 100k comandos

**Total inicial: ~$15/mês**

## 📚 Documentação

- [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) - Guia rápido
- [FLY_IO_DEPLOYMENT.md](FLY_IO_DEPLOYMENT.md) - Guia completo
- [MONITORING_ALERTING_GUIDE.md](MONITORING_ALERTING_GUIDE.md) - Monitoramento
- [LOAD_TESTING_GUIDE.md](LOAD_TESTING_GUIDE.md) - Testes de carga

## 🆘 Problemas?

Ver logs detalhados:
```bash
fly logs --app flow-forecaster | grep ERROR
```

SSH no container:
```bash
fly ssh console --app flow-forecaster
```

---

**Quando o deploy estiver funcionando, você pode:**
1. ✅ Testar simulações assíncronas
2. ✅ Rodar load tests contra flow-forecaster.fly.dev
3. ✅ Configurar domínio customizado (opcional)
4. ✅ Configurar monitoramento externo
