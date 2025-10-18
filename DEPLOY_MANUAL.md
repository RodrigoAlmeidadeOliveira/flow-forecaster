# Deploy Manual do Fly.io

## ⚠️ Status do Deploy Automático

O deploy automático via GitHub Actions está **temporariamente desabilitado** devido a um problema de permissões com tokens do Fly.io para CI/CD.

### Problema Identificado

O Fly.io usa diferentes tipos de tokens:
- **`fo1_`** - Token OAuth pessoal (funciona localmente, mas NÃO tem permissões para CI/CD)
- **`fm2_`** - Deploy tokens (deveriam funcionar para CI/CD, mas estão retornando erro de autenticação)

O erro que está ocorrendo:
```
Error: Not authorized to deploy this app
Error: Not authorized to manage this organization::feature
```

### Status da Aplicação

A aplicação `flow-forecaster` está atualmente **SUSPENDED** no Fly.io, com máquinas stopped.

## ✅ Solução Temporária: Deploy Manual

Enquanto o problema de permissões não é resolvido, faça deploy manualmente:

```bash
# Na pasta do projeto
cd flow-forecaster

# Fazer deploy
fly deploy --app flow-forecaster
```

O deploy manual funciona perfeitamente pois usa suas credenciais locais autenticadas.

## 🔧 Próximos Passos para Resolver

1. **Verificar status da conta Fly.io:**
   - Acessar: https://fly.io/dashboard
   - Verificar se há problemas de billing ou limites
   - Reativar a app se estiver suspensa

2. **Criar token com permissões corretas:**
   ```bash
   flyctl tokens create deploy --name "github-actions" --expiry 8760h
   ```

3. **Verificar permissões da organização:**
   - O app pertence à organização "personal"
   - Pode ser necessário criar o app em uma organização diferente ou ajustar permissões

4. **Alternativa: Usar Fly.io com autenticação OAuth:**
   - Configurar GitHub App do Fly.io
   - https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/

## 📝 Resumo

- ✅ **Deploy manual:** `fly deploy --app flow-forecaster` (FUNCIONA)
- ❌ **Deploy automático:** GitHub Actions (EM DESENVOLVIMENTO)
- 🔄 **Status:** Investigando problema de permissões de tokens

## Histórico de Tentativas

1. ✅ Workflow GitHub Actions configurado
2. ❌ Token `fm2_` (deploy token) - Erro de autenticação
3. ✅ Token `fo1_` (OAuth) - Autenticação OK
4. ❌ Token `fo1_` para deploy - Erro de permissões
5. ❌ Build remoto (--remote-only) - Erro de organização
6. ❌ Build local no Actions - Erro de permissões

**Última atualização:** 18/10/2025
