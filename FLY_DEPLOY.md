# Deploy no Fly.io (GRATUITO)

## Por que Fly.io?
- ✅ 100% Gratuito (3 VMs pequenas)
- ✅ Sem limite de tamanho de dependências
- ✅ Muito confiável e rápido
- ✅ Deploy simples via CLI

## Passo a Passo

### 1. Instalar Fly CLI

**macOS:**
```bash
brew install flyctl
```

**Linux/WSL:**
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Login no Fly.io

```bash
fly auth login
```

Isso vai abrir o navegador para você criar conta (gratuita) ou fazer login.

### 3. Fazer Deploy (na pasta do projeto)

```bash
cd /caminho/para/flow-forecaster
fly launch
```

O Fly vai:
- Detectar que é Python
- Criar Dockerfile automaticamente
- Perguntar nome do app
- Perguntar região (escolha a mais próxima)
- Fazer deploy automático

### 4. Configurações durante o launch

```
? Choose an app name: flow-forecaster (ou deixe vazio para gerar automático)
? Choose a region: gru (São Paulo) ou mia (Miami)
? Would you like to set up a Postgresql database? No
? Would you like to set up an Upstash Redis database? No
? Create .dockerignore? Yes
? Would you like to deploy now? Yes
```

### 5. Após deploy

Seu site estará em: `https://flow-forecaster.fly.dev`

### 6. Deploy futuro (após mudanças)

```bash
fly deploy
```

## Troubleshooting

Se der erro de build:
```bash
fly logs
```

Se precisar restart:
```bash
fly apps restart flow-forecaster
```

## Custos

- **Free tier**: 3 VMs compartilhadas (256MB RAM cada)
- **Suficiente** para seu projeto
- Só paga se passar dos limites gratuitos

## Alternativa ao Fly CLI: Fly.io Dashboard

1. Acesse https://fly.io/dashboard
2. New App
3. Deploy from GitHub
4. Selecione repositório flow-forecaster
5. Deploy automático

---

**Desenvolvido por**: Rodrigo Almeida de Oliveira
**Projeto**: Flow Forecasting
