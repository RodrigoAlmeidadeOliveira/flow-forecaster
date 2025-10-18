# Configuração do Deploy Automático

O deploy automático no Fly.io foi configurado usando GitHub Actions. Agora, sempre que você fizer push para a branch `main`, o deploy será feito automaticamente.

## Passo a Passo para Configurar

### 1. Obter o Token do Fly.io

O token já foi gerado. Você pode visualizá-lo executando:

```bash
flyctl auth token
```

Ou criar um novo token:

```bash
flyctl tokens create deploy
```

### 2. Adicionar o Secret no GitHub

1. Acesse: https://github.com/RodrigoAlmeidadeOliveira/flow-forecaster/settings/secrets/actions

2. Clique em **"New repository secret"**

3. Configure:
   - **Name:** `FLY_API_TOKEN`
   - **Value:** Cole o token obtido no passo 1

4. Clique em **"Add secret"**

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

## Observações

- O deploy manual continua funcionando: `fly deploy --app flow-forecaster`
- O token tem validade longa, mas pode ser renovado se necessário
- Logs de deploy ficam disponíveis em: https://fly.io/apps/flow-forecaster/monitoring
