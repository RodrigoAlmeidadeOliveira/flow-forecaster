# 🚀 Guia de Deploy - Project Forecaster

## ✅ Arquivos Preparados

O projeto está pronto para deploy com os seguintes arquivos:

- ✅ **Procfile** - Configuração do servidor Gunicorn
- ✅ **requirements.txt** - Dependências Python (incluindo gunicorn)
- ✅ **render.yaml** - Configuração automática do Render
- ✅ **runtime.txt** - Versão Python 3.11
- ✅ **.gitignore** - Arquivos a ignorar no Git
- ✅ **README.md** - Documentação completa

## 📝 Passo 1: Criar Repositório no GitHub

### 1.1. Acesse GitHub
Vá para: https://github.com/new

### 1.2. Preencha os dados
- **Repository name**: `project-forecaster-py`
- **Description**: `Previsão probabilística de projetos usando Machine Learning e Monte Carlo`
- **Visibilidade**: ✅ Public (necessário para Render gratuito)
- **NÃO marque**: README, .gitignore ou license (já temos)

### 1.3. Clique em "Create repository"

## 🔗 Passo 2: Conectar e Fazer Push

Abra o terminal e execute:

```bash
# Navegue até o diretório do projeto
cd '/Users/rodrigoalmeidadeoliveira/Library/CloudStorage/GoogleDrive-rodrigoalmeidadeoliveira@gmail.com/Outros computadores/Notebook/__Kanban/metricas/Fontes-Forecaster/project-forecaster-py'

# Adicione o remote do GitHub (SUBSTITUA rodrigoalmeidadeoliveira pelo seu username)
git remote add origin https://github.com/rodrigoalmeidadeoliveira/project-forecaster-py.git

# Renomeie a branch para main
git branch -M main

# Faça o push
git push -u origin main
```

### Verificação
Acesse `https://github.com/SEU-USUARIO/project-forecaster-py` e verifique se todos os arquivos estão lá.

## 🌐 Passo 3: Deploy no Render

### 3.1. Criar Conta no Render
1. Acesse: https://render.com/
2. Clique em "Get Started"
3. Faça login com GitHub (recomendado)

### 3.2. Criar Novo Web Service
1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**

### 3.3. Conectar Repositório
1. Clique em **"Connect a repository"**
2. Autorize o Render a acessar seus repositórios
3. Encontre e selecione **project-forecaster-py**

### 3.4. Configurar o Deploy

O Render detectará automaticamente o `render.yaml`, mas você pode configurar manualmente:

**Configurações:**
- **Name**: `project-forecaster` (ou qualquer nome)
- **Region**: Escolha o mais próximo (ex: Oregon para EUA)
- **Branch**: `main`
- **Root Directory**: deixe em branco
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --timeout 120 --workers 2`
- **Plan**: `Free` (0 GB RAM, 750h/mês grátis)

### 3.5. Variáveis de Ambiente (Opcional)
Adicione se necessário:
- `PYTHON_VERSION`: `3.11.0`
- `PORT`: será definido automaticamente pelo Render

### 3.6. Deploy
1. Clique em **"Create Web Service"**
2. Aguarde o build (5-10 minutos na primeira vez)
3. Acompanhe os logs em tempo real

## ✨ Passo 4: Aplicação Online!

Após o deploy bem-sucedido:

### URL da Aplicação
Sua aplicação estará disponível em:
```
https://project-forecaster.onrender.com
```
(ou o nome que você escolheu)

### Funcionalidades Disponíveis
- ✅ **Página Principal**: `/`
  - Monte Carlo tradicional

- ✅ **Forecast Avançado**: `/advanced`
  - ML + Monte Carlo combinado

### APIs REST
- `POST /api/simulate` - Monte Carlo
- `POST /api/ml-forecast` - ML Forecast
- `POST /api/mc-throughput` - MC Throughput
- `POST /api/combined-forecast` - Combinado

## 🔄 Atualizações Futuras

### Deploy Automático
Qualquer push para a branch `main` no GitHub irá automaticamente:
1. Trigger um novo build no Render
2. Executar testes (se houver)
3. Deploy da nova versão
4. Zero downtime

### Como Atualizar
```bash
# Faça suas modificações
# ...

# Commit e push
git add .
git commit -m "Sua mensagem de commit"
git push origin main

# Render fará o deploy automaticamente!
```

## ⚠️ Limitações do Plano Free

- **Sleep após 15 min de inatividade**: Primeira requisição após sleep demora 30-60s
- **750 horas/mês**: Suficiente se não usado 24/7
- **512 MB RAM**: Suficiente para esta aplicação
- **Disco limitado**: Sem persistência de dados

### Solução para Sleep
Se quiser evitar o sleep, use um serviço como:
- **UptimeRobot**: Pinga sua aplicação a cada 5 minutos (grátis)
- URL: https://uptimerobot.com/

## 📊 Monitoramento

### Logs em Tempo Real
No dashboard do Render:
1. Clique no seu serviço
2. Vá em **"Logs"**
3. Veja logs em tempo real

### Métricas
- CPU usage
- Memory usage
- Request count
- Response times

## 🐛 Troubleshooting

### Build Falha
**Erro**: `Failed to install requirements`
- Verifique `requirements.txt`
- Certifique-se que todas as versões são compatíveis

### Aplicação não Inicia
**Erro**: `Web service failed to start`
- Verifique o `Procfile`
- Teste localmente: `gunicorn app:app`

### Timeout Errors
**Erro**: `Request timeout`
- Aumente timeout no `Procfile`: `--timeout 180`
- Reduza `numberOfSimulations` nas requisições

### Memory Issues
**Erro**: `Out of memory`
- Reduza `--workers` para 1
- Otimize código para usar menos memória
- Considere upgrade de plano

## 🎉 Pronto!

Sua aplicação está online e acessível mundialmente!

### Próximos Passos
1. ✅ Compartilhe a URL com usuários
2. ✅ Adicione a URL ao README do GitHub
3. ✅ Configure domínio customizado (opcional)
4. ✅ Monitore uso e performance

### Suporte
- **Render Docs**: https://render.com/docs
- **GitHub Issues**: Para bugs e sugestões
- **Community**: Render Community Forum

---

**Criado com** ❤️ **usando Claude Code**
