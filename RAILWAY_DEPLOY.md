# Deploy do Flow Forecasting no Railway

Este guia mostra como fazer deploy do **Flow Forecasting** no Railway.app com integração ao GitHub.

## 📋 Pré-requisitos

✅ Seu projeto já está configurado com:
- `requirements.txt` - Todas as dependências Python
- `Procfile` - Comando para iniciar o app com Gunicorn
- `app.py` - Configurado para usar variável de ambiente PORT
- `.gitignore` - Arquivos ignorados pelo Git
- Repositório GitHub: `https://github.com/RodrigoAlmeidadeOliveira/project-forecaster-py.git`

## 🚀 Passo a Passo para Deploy

### 1. Criar conta no Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em **"Start a New Project"** ou **"Login with GitHub"**
3. Autorize o Railway a acessar sua conta GitHub

### 2. Criar novo projeto

1. No dashboard do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Procure e selecione o repositório: `project-forecaster-py`
4. Clique em **"Deploy Now"**

### 3. Configurar variáveis de ambiente (opcional)

Se seu app precisar de variáveis de ambiente:

1. No projeto Railway, clique na aba **"Variables"**
2. Adicione as variáveis necessárias:
   - Exemplo: `FLASK_ENV=production`
   - Exemplo: `SECRET_KEY=sua-chave-secreta`

Para este projeto básico, não é necessário configurar variáveis adicionais.

### 4. Aguardar o deploy

O Railway irá:
1. ✅ Detectar que é um projeto Python
2. ✅ Instalar as dependências do `requirements.txt`
3. ✅ Usar o `Procfile` para iniciar o app
4. ✅ Gerar uma URL pública para seu site

O processo leva cerca de 2-5 minutos.

### 5. Acessar seu site

1. Após o deploy, você verá **"Success"** no Railway
2. Clique em **"View Logs"** para ver os logs do servidor
3. Clique no botão **"Settings"** → **"Domains"**
4. Railway gera automaticamente uma URL como: `https://seu-projeto.up.railway.app`
5. Você pode adicionar um domínio customizado se quiser

## 🔄 Deploy Automático

Qualquer push para o branch `main` do GitHub irá automaticamente:
- Fazer rebuild no Railway
- Deploy da nova versão
- Sem necessidade de comandos manuais

## 📊 Monitoramento

No dashboard do Railway você pode:
- Ver logs em tempo real
- Monitorar uso de recursos (CPU, memória)
- Ver métricas de requisições
- Restart manual do serviço

## 💰 Planos do Railway

- **Hobby Plan** (Gratuito): $5 de crédito mensal (~500 horas de execução)
- **Developer Plan**: $5/mês + uso adicional
- **Team Plan**: $20/mês + uso adicional

Para desenvolvimento e projetos pequenos, o plano gratuito é suficiente.

## ⚙️ Arquivos de Configuração

### Procfile
```
web: gunicorn app:app --timeout 120 --workers 2
```

### app.py (linhas importantes)
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
```

### requirements.txt
```
Flask==3.0.0
numpy==1.26.2
pandas==2.1.4
matplotlib==3.8.2
seaborn==0.13.0
scikit-learn==1.3.2
xgboost==2.0.3
scipy==1.11.4
python-dateutil==2.8.2
gunicorn==21.2.0
```

## 🔧 Troubleshooting

### Problema: App não inicia
**Solução**: Verifique os logs no Railway. Geralmente é por:
- Dependência faltando no `requirements.txt`
- Erro no código Python
- Porta não configurada corretamente

### Problema: Timeout no build
**Solução**:
- Aumente o timeout no `Procfile`: `--timeout 300`
- Ou simplifique as dependências

### Problema: Deploy falhou
**Solução**:
1. Verifique se o último commit no GitHub está correto
2. Veja os logs de build no Railway
3. Teste localmente: `gunicorn app:app --bind 0.0.0.0:8080`

## 🎯 Próximos Passos

Após o deploy bem-sucedido:
1. ✅ Teste todas as funcionalidades do Flow Forecasting
2. ✅ Configure domínio customizado (opcional)
3. ✅ Configure SSL/HTTPS (Railway faz isso automaticamente)
4. ✅ Monitore uso e performance

## 📚 Links Úteis

- [Documentação Railway](https://docs.railway.app/)
- [Railway Python Template](https://docs.railway.app/guides/python)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Seu repositório GitHub](https://github.com/RodrigoAlmeidadeOliveira/project-forecaster-py)

---

**Desenvolvido por**: Rodrigo Almeida de Oliveira
**Projeto**: Flow Forecasting
**Plataforma**: Railway.app
