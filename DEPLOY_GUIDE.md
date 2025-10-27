# 🚀 Guia de Deploy - Flow Forecaster no Fly.io

Este guia consolida os passos necessários para publicar a aplicação diretamente no Fly.io, que é o provedor oficial usado no projeto.

## ✅ Arquivos e estrutura prontos para o Fly.io

- ✅ **fly.toml** – Configuração da aplicação `flow-forecaster`
- ✅ **Dockerfile** – Build otimizado para a plataforma
- ✅ **requirements.txt** e **runtime.txt** – Dependências e versão do Python
- ✅ **Procfile** – Comando de execução com Gunicorn (referência local)
- ✅ **DEPLOY_SETUP.md / DEPLOY_MANUAL.md / FLY_DEPLOY.md** – Guias complementares específicos do Fly.io
- ✅ **Monta** `/data` com volume persistente (`flow_forecaster_data`) para o banco SQLite

## 📝 Passo 1 – Preparar repositório no GitHub

1. Crie um repositório vazio em <https://github.com/new>.
2. Execute os comandos abaixo substituindo pelo caminho local do projeto e seu usuário GitHub:

```bash
cd '/Users/rodrigoalmeidadeoliveira/Library/CloudStorage/GoogleDrive-rodrigoalmeidadeoliveira@gmail.com/Outros computadores/Notebook/__Kanban/metricas/Fontes-Forecaster/flow-forecaster'
git init
git remote add origin https://github.com/SEU-USUARIO/flow-forecaster.git
git branch -M main
git add .
git commit -m "Initial import"
git push -u origin main
```

> Se o repositório já existe, garanta apenas que a branch `main` esteja sincronizada.

## 🛠️ Passo 2 – Configurar o Fly CLI localmente

1. Instale a CLI: `curl -L https://fly.io/install.sh | sh`
2. Faça login: `fly auth login`
3. Valide o arquivo `fly.toml` (app `flow-forecaster`, região `gru`, volume `flow_forecaster_data`). Ajuste o nome se estiver usando outra conta.

## ☁️ Passo 3 – Provisionar a aplicação

```bash
# Criar app se ainda não existir
fly apps create flow-forecaster

# Criar volume persistente para o banco SQLite
fly volumes create flow_forecaster_data --size 1 --region gru
```

Se a app já existir, garanta que o volume esteja associado ao mesmo nome configurado em `fly.toml`.

## 🚀 Passo 4 – Deploy manual

```bash
fly deploy --remote-only
```

O processo utiliza o Dockerfile do repositório, aplica as variáveis definidas em `[env]` e monta `/data` para persistir o `forecaster.db`. Ao final, verifique a URL pública exibida pela CLI.

### Testes pós-deploy

- Acesse `https://flow-forecaster.fly.dev/health` para confirmar status `200`.
- Use `/register` para criar o primeiro usuário (ou importe um banco existente para `/data/forecaster.db`).

## 🔄 Passo 5 – Deploy contínuo com GitHub Actions (opcional)

O workflow em `.github/workflows/fly-deploy.yml` usa o token Fly.io salvo em `FLY_API_TOKEN`. Para reativar:

1. Gere um token com `fly auth token`.
2. No GitHub, adicione em *Settings → Secrets and variables → Actions → New secret* o valor `FLY_API_TOKEN`.
3. Cada push na `main` executará automaticamente `fly deploy --remote-only`.

## 🧰 Troubleshooting no Fly.io

- **Build falhou:** rode `fly deploy --remote-only --build-only` para inspecionar a imagem.
- **Banco vazio após reboot:** confirme se o volume `flow_forecaster_data` está `attached` e se `DATABASE_URL` aponta para `sqlite:////data/forecaster.db`.
- **Erro de memória:** ajuste `[[vm]]` em `fly.toml` (ex.: `memory = "2gb"`) e redeploy.
- **Aplicação off:** use `fly status`, `fly apps restart flow-forecaster` ou `fly logs -a flow-forecaster` para investigar.

## ✅ Checklist final

- [ ] Repositório atualizado no GitHub
- [ ] Token do Fly configurado (local e/ou GitHub Actions)
- [ ] App e volume criados na conta correta
- [ ] Deploy concluído com `fly deploy`
- [ ] Endpoint `/health` respondendo `200`
- [ ] Primeiro usuário registrado ou banco importado

> Para detalhes adicionais (automações, tokens e operações diárias), consulte `FLY_DEPLOY.md`, `DEPLOY_SETUP.md` e `DEPLOY_MANUAL.md`.
