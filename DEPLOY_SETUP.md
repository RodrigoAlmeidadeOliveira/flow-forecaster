# Configuração do Deploy Automático

O deploy automático no Fly.io foi configurado usando GitHub Actions. Agora, sempre que você fizer push para a branch `main`, o deploy será feito automaticamente.

## ⚠️ AÇÃO NECESSÁRIA: Configurar o Secret

**O deploy automático só funcionará após você configurar o `FLY_API_TOKEN` no GitHub!**

## Passo a Passo para Configurar

### 1. Obter o Token do Fly.io

Execute no seu terminal local:

```bash
flyctl auth token
```

Ou crie um novo token de deploy:

```bash
flyctl tokens create deploy
```

Copie o token gerado (começa com `FlyV1 ` ou `fm2_`).

### 2. ⭐ Adicionar o Secret no GitHub (OBRIGATÓRIO)

1. Acesse: https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/settings/secrets/actions

2. Clique em **"New repository secret"**

3. Configure:
   - **Name:** `FLY_API_TOKEN`
   - **Value:** Cole o token obtido no passo 1 (o token completo, incluindo `FlyV1 ` se houver)

4. Clique em **"Add secret"**

### ✅ Como Verificar se o Token Está Configurado

1. Acesse: https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/settings/secrets/actions

2. Você deve ver `FLY_API_TOKEN` na lista de secrets

3. Se não estiver lá, o deploy vai falhar com erro de autenticação

### 3. Verificar o Workflow

O arquivo `.github/workflows/fly-deploy.yml` já foi criado e configurado.

Ele será executado automaticamente sempre que você fizer push para a branch `main`.

### 4. Testar o Deploy Automático

Após configurar o secret, faça um commit e push:

```bash
git add .
git commit -m "fix: Corrigir cálculo de probabilidades e configurar deploy automático"
git push origin main
```

### 5. Acompanhar o Deploy

Acesse a aba **Actions** no GitHub para ver o progresso:
https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/actions

## Como Funciona

O workflow GitHub Actions:
- É acionado quando há push na branch `main`
- Faz checkout do código
- Instala o Fly CLI
- Executa `flyctl deploy --remote-only --app flow-forecaster`
- O build é feito no servidor do Fly.io (--remote-only)

## 🔧 Solução de Problemas

### Erro: "You must be authenticated to view this"

Se você vir este erro nos logs do GitHub Actions, significa que:
1. O secret `FLY_API_TOKEN` não foi configurado no GitHub, OU
2. O token está inválido/expirado

**Solução:**
1. Execute `flyctl auth token` no seu terminal local
2. Copie o token completo (pode ter vários tokens separados por vírgula - use o primeiro)
3. Adicione como secret no GitHub (veja passo 2 acima)

### Pular Deploy em um Commit

Para fazer commit sem acionar o deploy automático, adicione `[skip ci]` na mensagem:

```bash
git commit -m "docs: Atualizar README [skip ci]"
```

## Observações

- O deploy manual continua funcionando: `fly deploy --app flow-forecaster`
- O token tem validade longa, mas pode ser renovado se necessário
- Logs de deploy ficam disponíveis em: https://fly.io/apps/flow-forecaster/monitoring
- O arquivo `fly.toml` contém as configurações da app no Fly.io
