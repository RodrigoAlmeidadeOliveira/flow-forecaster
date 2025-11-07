#!/bin/bash

# 🚨 SCRIPT DE EMERGÊNCIA - Deploy Fly.io
# Execute: bash emergency_deploy.sh

set -e

echo "🚨 EMERGÊNCIA - Restaurando Sistema"
echo "===================================="
echo ""

# 1. Salvar mudanças locais
echo "📦 Salvando mudanças locais..."
git stash push -m "Emergency stash" 2>/dev/null || true

# 2. Mudar para branch correto
echo "🔀 Mudando para branch de deploy..."
git fetch origin
git checkout -B claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS origin/claude/evaluate-architecture-performance-011CUqm9VcBC6T6f2K3weHdS

# 3. Verificar branch
CURRENT_BRANCH=$(git branch --show-current)
echo "✓ Branch atual: $CURRENT_BRANCH"
echo ""

# 4. Configurar secrets
echo "🔐 Configurando secrets..."

fly secrets set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') --app flow-forecaster --stage

fly secrets set FLASK_ENV=production --app flow-forecaster --stage

fly secrets set CELERY_BROKER_URL="redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster --stage

fly secrets set CELERY_RESULT_BACKEND="redis://default:c33726412e754cf3b0ead4109c277da2@fly-flow-forecaster-redis.upstash.io:6379" --app flow-forecaster --stage

echo "✓ Secrets configurados"
echo ""

# 5. Deploy IMEDIATO
echo "🚀 Fazendo deploy AGORA..."
fly deploy --ha=false --now

# 6. Escalar máquinas
echo "⚡ Escalando máquinas..."
fly scale count web=1 worker=1 --app flow-forecaster --yes

# 7. Verificar status
echo ""
echo "🔍 Verificando status..."
fly status --app flow-forecaster

echo ""
echo "✅ DEPLOY COMPLETO!"
echo "==================="
echo ""
echo "Seu sistema está disponível em:"
echo "👉 https://flow-forecaster.fly.dev"
echo ""
echo "Verificar logs:"
echo "fly logs --app flow-forecaster"
