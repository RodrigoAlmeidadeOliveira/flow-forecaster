# 🚀 Production Deployment Guide - Flow Forecaster

Guia completo para deploy em produção da arquitetura assíncrona do Flow Forecaster.

---

## 📋 Pré-requisitos

- Git instalado
- Conta em uma plataforma cloud (Heroku, AWS, Azure, ou GCP)
- PostgreSQL e Redis disponíveis
- Código commitado no repositório

---

## 🎯 Opções de Deploy

### 1. Heroku (Mais Fácil - Recomendado para Início)
### 2. Docker Compose (Self-Hosted)
### 3. AWS (Escalável)
### 4. Azure (Enterprise)
### 5. Google Cloud Platform (Moderno)

---

## 🟣 Opção 1: Deploy no Heroku

### Passo 1: Instalar Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download: https://devcenter.heroku.com/articles/heroku-cli
```

### Passo 2: Login e Criar App

```bash
# Login no Heroku
heroku login

# Criar aplicação
heroku create flow-forecaster-prod

# Ou usar nome customizado
heroku create your-app-name
```

### Passo 3: Adicionar Add-ons (PostgreSQL + Redis)

```bash
# PostgreSQL (Essential - $5-15/mês)
heroku addons:create heroku-postgresql:essential-0

# Redis (Mini - $3-15/mês)
heroku addons:create heroku-redis:mini

# Verificar add-ons
heroku addons
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
# Secret key (gerar nova)
heroku config:set FLOW_FORECASTER_SECRET_KEY=$(openssl rand -hex 32)

# Celery usa Redis automaticamente
# Mas podemos configurar explicitamente:
heroku config:set CELERY_BROKER_URL=$(heroku config:get REDIS_URL)
heroku config:set CELERY_RESULT_BACKEND=$(heroku config:get REDIS_URL)

# Log level
heroku config:set LOG_LEVEL=INFO

# Worker concurrency
heroku config:set CELERY_WORKER_CONCURRENCY=4

# Verificar configuração
heroku config
```

### Passo 5: Deploy da Aplicação

```bash
# Adicionar remote do Heroku (se não adicionou com create)
heroku git:remote -a flow-forecaster-prod

# Push para Heroku
git push heroku main

# Ou se estiver em outra branch
git push heroku claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS:main
```

### Passo 6: Escalar Workers

```bash
# Escalar web dynos
heroku ps:scale web=2

# Escalar Celery workers
heroku ps:scale worker=4

# Opcional: Flower para monitoring
heroku ps:scale flower=1

# Verificar
heroku ps
```

### Passo 7: Ver Logs

```bash
# Logs em tempo real
heroku logs --tail

# Logs do web
heroku logs --tail --dyno=web

# Logs do worker
heroku logs --tail --dyno=worker

# Últimas 1000 linhas
heroku logs -n 1000
```

### Passo 8: Acessar Aplicação

```bash
# Abrir no browser
heroku open

# Ver URL
heroku info
```

### Passo 9: Executar Comandos

```bash
# Abrir console Python
heroku run python

# Executar migrations (se usar Alembic)
heroku run alembic upgrade head

# Ver banco de dados
heroku pg:info
heroku pg:psql

# Ver Redis
heroku redis:info
heroku redis:cli
```

### Custo Estimado (Heroku)

| Componente | Plano | Custo/Mês |
|------------|-------|-----------|
| Web Dyno (2x) | Basic | $14 |
| Worker Dyno (4x) | Basic | $28 |
| PostgreSQL | Essential-0 | $5 |
| Redis | Mini | $3 |
| **TOTAL** | | **$50/mês** |

---

## 🐳 Opção 2: Docker Compose (Self-Hosted)

### Servidor Requisitos

- Ubuntu 20.04+ / Debian 11+
- 2 CPU cores mínimo (4+ recomendado)
- 4GB RAM mínimo (8GB+ recomendado)
- 20GB disco

### Passo 1: Instalar Docker

```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin -y

# Verificar
docker --version
docker compose version
```

### Passo 2: Configurar Servidor

```bash
# Criar usuário para aplicação
sudo adduser flowapp
sudo usermod -aG docker flowapp

# Fazer login como flowapp
sudo su - flowapp

# Clonar repositório
git clone https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster.git
cd flow-forecaster
```

### Passo 3: Configurar Ambiente

```bash
# Criar arquivo .env
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://forecaster:CHANGE_ME_PASSWORD@postgres:5432/forecaster

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Flask
FLOW_FORECASTER_SECRET_KEY=CHANGE_ME_GENERATE_WITH_OPENSSL

# Celery
CELERY_WORKER_CONCURRENCY=4

# Nginx (se usar)
DOMAIN=your-domain.com
EOF

# IMPORTANTE: Gerar secret key
openssl rand -hex 32
# Copiar resultado e colar no .env

# Ajustar permissões
chmod 600 .env
```

### Passo 4: Configurar docker-compose.prod.yml

```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: forecaster
      POSTGRES_USER: forecaster
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U forecaster"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  web:
    build: .
    restart: always
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:application
    environment:
      DATABASE_URL: ${DATABASE_URL}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
      FLOW_FORECASTER_SECRET_KEY: ${FLOW_FORECASTER_SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
      - frontend
    ports:
      - "8000:8000"

  worker:
    build: .
    restart: always
    command: celery -A celery_app worker --loglevel=info --concurrency=${CELERY_WORKER_CONCURRENCY:-4}
    environment:
      DATABASE_URL: ${DATABASE_URL}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    deploy:
      replicas: 2

  flower:
    build: .
    restart: always
    command: celery -A celery_app flower --port=5555
    environment:
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
    depends_on:
      - redis
      - worker
    networks:
      - backend
      - frontend
    ports:
      - "5555:5555"

  nginx:
    image: nginx:alpine
    restart: always
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/usr/share/nginx/html/static:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    networks:
      - frontend

volumes:
  postgres_data:
  redis_data:

networks:
  backend:
  frontend:
EOF
```

### Passo 5: Deploy

```bash
# Build e start
docker compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Ver status
docker compose -f docker-compose.prod.yml ps

# Parar
docker compose -f docker-compose.prod.yml down

# Parar e remover volumes (CUIDADO!)
docker compose -f docker-compose.prod.yml down -v
```

### Custo Estimado (VPS)

| Provedor | Specs | Custo/Mês |
|----------|-------|-----------|
| DigitalOcean | 4GB, 2 CPU | $24 |
| Linode | 4GB, 2 CPU | $24 |
| Vultr | 4GB, 2 CPU | $24 |
| AWS Lightsail | 4GB, 2 CPU | $40 |

---

## ☁️ Opção 3: AWS (Amazon Web Services)

### Arquitetura AWS

```
┌─────────────────────────────────────────┐
│         Application Load Balancer        │
└────────────┬────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│   ECS    │    │   ECS    │   (Web)
│ Task 1   │    │ Task 2   │
└────┬─────┘    └────┬─────┘
     │                │
     └───────┬────────┘
             │
     ┌───────▼────────┐
     │   RDS          │   (PostgreSQL)
     │   ElastiCache  │   (Redis)
     └────────────────┘

     ┌────────────────┐
     │  ECS Workers   │   (Celery)
     │  (4 tasks)     │
     └────────────────┘
```

### Passo 1: Instalar AWS CLI

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure
# AWS Access Key ID: <your-key>
# AWS Secret Access Key: <your-secret>
# Default region: us-east-1
# Default output format: json
```

### Passo 2: Criar RDS (PostgreSQL)

```bash
# Via Console ou CLI
aws rds create-db-instance \
  --db-instance-identifier flow-forecaster-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 16.1 \
  --master-username forecaster \
  --master-user-password CHANGE_ME \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxx \
  --db-subnet-group-name default \
  --publicly-accessible \
  --backup-retention-period 7
```

### Passo 3: Criar ElastiCache (Redis)

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id flow-forecaster-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --cache-subnet-group-name default \
  --security-group-ids sg-xxxxxx
```

### Passo 4: Deploy com ECS

```bash
# Criar cluster
aws ecs create-cluster --cluster-name flow-forecaster

# Build e push imagem para ECR
aws ecr create-repository --repository-name flow-forecaster

# Get login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build e push
docker build -t flow-forecaster .
docker tag flow-forecaster:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/flow-forecaster:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/flow-forecaster:latest

# Criar task definition e service (via Console ou CloudFormation)
```

### Custo Estimado (AWS)

| Componente | Specs | Custo/Mês |
|------------|-------|-----------|
| ECS Fargate (web, 2 tasks) | 0.25 vCPU, 0.5GB | $15 |
| ECS Fargate (workers, 4) | 0.25 vCPU, 0.5GB | $30 |
| RDS PostgreSQL | db.t3.micro | $15 |
| ElastiCache | cache.t3.micro | $12 |
| ALB | Load balancer | $16 |
| Data transfer | ~100GB | $10 |
| **TOTAL** | | **~$98/mês** |

---

## 📊 Comparação de Plataformas

| Aspecto | Heroku | Docker (VPS) | AWS |
|---------|--------|--------------|-----|
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Custo (pequeno)** | $50/mês | $24/mês | $50/mês |
| **Custo (médio)** | $150/mês | $24/mês | $100/mês |
| **Custo (grande)** | $500+/mês | $100/mês | $200+/mês |
| **Escalabilidade** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Controle** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Manutenção** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Tempo de setup** | 15 min | 2-4 horas | 4-8 horas |

**Recomendação:**
- **Prototipação/MVP:** Heroku
- **Custo-efetivo:** Docker em VPS
- **Escala enterprise:** AWS/Azure/GCP

---

## 🔒 Checklist de Segurança

Antes de ir para produção:

- [ ] Gerar nova SECRET_KEY (nunca usar a de dev)
- [ ] Configurar HTTPS/SSL (Let's Encrypt ou CloudFlare)
- [ ] Configurar firewall (permitir apenas 80, 443, SSH)
- [ ] Habilitar backups automáticos (database)
- [ ] Configurar rate limiting
- [ ] Revisar permissões de usuários no banco
- [ ] Configurar CORS adequadamente
- [ ] Habilitar logging centralizado
- [ ] Configurar monitoring e alertas
- [ ] Testar disaster recovery
- [ ] Documentar credenciais (usar gerenciador de senhas)
- [ ] Configurar 2FA para acesso admin

---

## 📈 Monitoring & Health Checks

### Endpoints de Health Check

```python
# Já implementados no sistema
GET /api/health/celery      # Celery workers status
GET /health                  # Application health (adicionar)
GET /ready                   # Readiness probe (adicionar)
```

### Ferramentas Recomendadas

1. **Application Performance:**
   - New Relic
   - DataDog
   - AppDynamics

2. **Infrastructure:**
   - Prometheus + Grafana
   - CloudWatch (AWS)
   - Azure Monitor

3. **Logs:**
   - Papertrail
   - Loggly
   - ELK Stack

4. **Uptime:**
   - UptimeRobot
   - Pingdom
   - StatusCake

---

## 🚨 Troubleshooting Produção

### Problema: Workers não processam tasks

```bash
# Heroku
heroku ps:restart worker
heroku logs --tail --dyno=worker

# Docker
docker compose -f docker-compose.prod.yml restart worker
docker compose -f docker-compose.prod.yml logs worker
```

### Problema: Alto uso de memória

```bash
# Verificar
heroku ps -a flow-forecaster-prod

# Ajustar worker concurrency
heroku config:set CELERY_WORKER_CONCURRENCY=2
heroku ps:restart worker
```

### Problema: Database connection pool esgotado

```bash
# Aumentar pool size (database.py)
# pool_size=20 → pool_size=50

# Ou reduzir workers
heroku ps:scale web=2 worker=2
```

---

## 📝 Próximos Passos Pós-Deploy

1. **Configurar CI/CD**
   - GitHub Actions
   - GitLab CI
   - CircleCI

2. **Configurar Backups**
   - Database: daily backups com retenção de 30 dias
   - Redis: snapshots (se necessário)

3. **Load Testing**
   - Simular 100-500 usuários simultâneos
   - Validar response times < 500ms

4. **Documentação**
   - Runbook de operações
   - Procedimentos de rollback
   - Contatos de emergência

5. **Monitoring**
   - Alertas para erros > 5%
   - Alertas para latência > 2s
   - Alertas para uso de memória > 80%

---

**Deploy realizado com sucesso?** ✅

Documentação completa disponível em:
- ASYNC_ARCHITECTURE_GUIDE.md
- MONITORING_ALERTING_GUIDE.md (próximo)
- LOAD_TESTING_GUIDE.md (próximo)
