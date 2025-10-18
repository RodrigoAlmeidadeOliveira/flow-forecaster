# 🔑 Guia Rápido: Configurar Token do Fly.io

## ⚡ Passo a Passo (5 minutos)

### 1️⃣ Obter o Token do Fly.io

Abra seu terminal e execute:

```bash
flyctl auth token
```

**Exemplo de saída:**
```
fm2_lJPECAAAAAAACm1txBBm5l7NP2wZgfNK4gSqQ6sHwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJL...,fm2_lJPEThYcUfcM1qam03BuSSCjB94moXmKpU7Ff5I0SkIrtaIfA6FTI/YkbS6ef4k3vA...,fo1_QiiG_4wKuzcyIQoU1raN61xlovOUCfRsJkkvTAyXK3Q
```

✅ **Copie APENAS o primeiro token** (tudo antes da primeira vírgula)

Exemplo: `fm2_lJPECAAAAAAACm1txBBm5l7NP2wZgfNK4gSqQ6sHwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJL...`

---

### 2️⃣ Adicionar Secret no GitHub

#### Opção A: Via Interface Web (RECOMENDADO)

1. **Acesse a página de secrets:**
   https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/settings/secrets/actions

2. **Clique em:** "New repository secret" (botão verde no canto superior direito)

3. **Preencha:**
   - Name: `FLY_API_TOKEN`
   - Secret: Cole o token copiado no passo 1

4. **Clique em:** "Add secret"

5. **✅ Confirme:** Você deve ver `FLY_API_TOKEN` na lista

#### Opção B: Via GitHub CLI

```bash
# Certifique-se de ter o gh CLI instalado e autenticado
gh secret set FLY_API_TOKEN --body "seu-token-aqui" --repo RodrigoAlmeidadeOliveira/flow-forecaster
```

---

### 3️⃣ Testar o Deploy Automático

Agora faça um push para testar:

```bash
git push origin main
```

Acompanhe o deploy em:
https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/actions

---

## ✅ Como Verificar se Funcionou

Após o push, você deve ver:

1. **GitHub Actions:** Uma nova execução em andamento
2. **Status:** ✅ Deploy bem-sucedido (em ~2-3 minutos)
3. **App:** https://flow-forecaster.fly.dev deve estar atualizada

---

## ❌ Problemas Comuns

### Erro: "You must be authenticated to view this"

**Causa:** Token não configurado ou inválido

**Solução:**
1. Verifique se o secret existe: https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/settings/secrets/actions
2. Se não existir, volte ao Passo 2
3. Se existir mas não funciona, delete e crie novamente com um token novo

### Erro: "failed with exit code 128"

**Causa:** Problema com git/submodules (warning apenas, não afeta deploy)

**Solução:** Pode ignorar, não impacta o deploy

---

## 📝 Resumo

✅ **Antes:** `fly deploy --app flow-forecaster` (manual)
✅ **Depois:** `git push origin main` (automático!)

O deploy será feito automaticamente sempre que você fizer push para `main`.

Para pular o deploy em um commit específico, use `[skip ci]`:
```bash
git commit -m "docs: Atualizar README [skip ci]"
```
