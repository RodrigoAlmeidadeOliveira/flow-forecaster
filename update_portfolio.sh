#!/bin/bash
# Script para atualizar valores de portfólio
# Requer que você esteja logado no site primeiro

echo "🎯 Atualizando valores de portfólio..."
echo ""
echo "IMPORTANTE: Este script requer seu cookie de sessão."
echo "Por favor, siga estes passos:"
echo ""
echo "1. Abra https://flow-forecaster.fly.dev no navegador"
echo "2. Faça login com sua conta de admin"
echo "3. Abra as Ferramentas do Desenvolvedor (F12)"
echo "4. Vá para Application > Cookies > https://flow-forecaster.fly.dev"
echo "5. Copie o valor do cookie 'session'"
echo ""
read -p "Cole o valor do cookie 'session' aqui: " SESSION_COOKIE

if [ -z "$SESSION_COOKIE" ]; then
    echo "❌ Cookie não fornecido. Abortando."
    exit 1
fi

echo ""
echo "🔄 Executando atualização..."

curl -X POST https://flow-forecaster.fly.dev/admin/update-portfolio-values \
  -H "Content-Type: application/json" \
  -H "Cookie: session=$SESSION_COOKIE" \
  -s | python3 -m json.tool

echo ""
echo "✅ Atualização concluída!"
echo "Acesse https://flow-forecaster.fly.dev → aba 'Portfólio' para ver a matriz atualizada."
