# Portfolio Phases 4, 5 e 6 - Verificação de Deploy

## ✅ Checklist de Verificação

### 1. Commits Verificados
```bash
✅ Phase 4 commits: 85c63c8, e8b8d9c, 3c742d7, 2f5f87a, db542de
✅ Phase 5 commits: ace3dd5, e64160e, db1087d
✅ Phase 6 commit: 799dea3, f074fc8
✅ Todos commits foram pushed para origin/claude/add-fold-stride-backtesting-011CUqfJiLhi5Gv73CdaHrKU
```

### 2. Arquivos Verificados
```bash
✅ templates/portfolio_risks.html - EXISTS and TRACKED
✅ templates/portfolio_optimization.html - EXISTS and TRACKED
✅ templates/portfolio_executive.html - EXISTS and TRACKED
✅ static/js/portfolio_risks.js - EXISTS and TRACKED
✅ static/js/portfolio_optimization.js - EXISTS and TRACKED
✅ static/js/portfolio_executive.js - EXISTS and TRACKED
✅ portfolio_risk_manager.py - EXISTS and TRACKED
✅ portfolio_optimizer.py - EXISTS and TRACKED
✅ portfolio_export.py - EXISTS and TRACKED
```

### 3. Rotas Verificadas no app.py
```bash
✅ @app.route('/portfolio/risks') - Line 3935
✅ @app.route('/portfolio/optimize') - Line 3953
✅ @app.route('/portfolio/executive') - Line 3971
✅ /api/portfolios/<id>/risks - Multiple endpoints
✅ /api/portfolios/<id>/optimize - POST endpoint
✅ /api/portfolios/<id>/export/excel - GET endpoint
✅ /api/portfolios/<id>/export/pdf - GET endpoint
```

### 4. Links de Navegação Verificados
```bash
✅ index.html tem link para /portfolio/risks
✅ index.html tem link para /portfolio/optimize
✅ index.html tem link para /portfolio/executive
```

## 🔧 Passos para Deploy no Servidor

### Passo 1: Atualizar o código do servidor
```bash
cd /caminho/para/flow-forecaster
git fetch origin
git checkout claude/add-fold-stride-backtesting-011CUqfJiLhi5Gv73CdaHrKU
git pull origin claude/add-fold-stride-backtesting-011CUqfJiLhi5Gv73CdaHrKU
```

### Passo 2: Instalar dependências necessárias
```bash
# Instalar bibliotecas de export (Phase 6)
pip install openpyxl reportlab

# Verificar instalação de PuLP (Phase 5)
pip install pulp
```

### Passo 3: Reiniciar o servidor web
```bash
# Se usando systemd
sudo systemctl restart flow-forecaster

# OU se usando supervisord
sudo supervisorctl restart flow-forecaster

# OU se rodando manualmente
# Pressione Ctrl+C no terminal atual e rode:
python3 app.py
```

### Passo 4: Verificar se o servidor iniciou corretamente
```bash
# Verificar logs
tail -f /var/log/flow-forecaster/error.log

# OU verificar no terminal se não houver erros
# Deve mostrar algo como:
# * Running on http://0.0.0.0:8080/
```

## 🧪 Testes de Verificação

### Teste 1: Acessar Portfolio Risks
1. Acesse: http://seu-servidor:8080/portfolio/risks
2. Deve mostrar a página de Portfolio Risk Management
3. Selecione um portfolio no dropdown
4. Deve carregar o heatmap 5×5 de riscos

### Teste 2: Acessar Portfolio Optimization
1. Acesse: http://seu-servidor:8080/portfolio/optimize
2. Deve mostrar a página de Portfolio Optimization
3. Selecione um portfolio no dropdown
4. Configure restrições (budget, capacity)
5. Clique em "Run Optimization"
6. Deve mostrar projetos selecionados pelo algoritmo

### Teste 3: Acessar Executive Dashboard
1. Acesse: http://seu-servidor:8080/portfolio/executive
2. Deve mostrar o Executive Dashboard
3. Selecione um portfolio
4. Deve mostrar 4 KPIs no topo
5. Deve mostrar executive summary e gráficos

### Teste 4: Testar Exports
1. Acesse: http://seu-servidor:8080/portfolio/dashboard
2. Selecione um portfolio
3. Clique no botão "Excel"
4. Deve fazer download de arquivo .xlsx
5. Clique no botão "PDF"
6. Deve fazer download de arquivo .pdf

## 🐛 Troubleshooting

### Problema: Página não carrega (404)
**Causa**: Servidor não foi reiniciado após o pull
**Solução**: Reinicie o servidor web (Passo 3)

### Problema: Erro 500 ao acessar /portfolio/optimize
**Causa**: Biblioteca PuLP não instalada
**Solução**:
```bash
pip install pulp
sudo systemctl restart flow-forecaster
```

### Problema: Erro ao exportar para Excel/PDF
**Causa**: Bibliotecas openpyxl ou reportlab não instaladas
**Solução**:
```bash
pip install openpyxl reportlab
sudo systemctl restart flow-forecaster
```

### Problema: Portfolio Risks mostra "No data"
**Causa**: Sem riscos cadastrados no portfolio
**Solução**:
1. Cadastre riscos usando o botão "Add Risk"
2. OU use o botão "Suggest Risks" para gerar sugestões automáticas

### Problema: Optimization retorna "Service Unavailable"
**Causa**: PuLP não está instalado ou não está disponível
**Solução**:
```bash
python3 -c "import pulp; print('PuLP OK')"
# Se der erro, instale: pip install pulp
```

## 📋 Comandos de Verificação Rápida

```bash
# 1. Verificar se os arquivos existem
ls -la templates/portfolio_risks.html
ls -la templates/portfolio_optimization.html
ls -la templates/portfolio_executive.html
ls -la static/js/portfolio_risks.js
ls -la static/js/portfolio_optimization.js
ls -la portfolio_risk_manager.py
ls -la portfolio_optimizer.py
ls -la portfolio_export.py

# 2. Verificar se os módulos podem ser importados
python3 -c "import portfolio_risk_manager; print('portfolio_risk_manager OK')"
python3 -c "import portfolio_optimizer; print('portfolio_optimizer OK')"
python3 -c "import portfolio_export; print('portfolio_export OK')"

# 3. Verificar dependências
python3 -c "import pulp; print('PuLP OK')"
python3 -c "import openpyxl; print('openpyxl OK')"
python3 -c "import reportlab; print('reportlab OK')"

# 4. Verificar rotas no app
grep -n "@app.route('/portfolio" app.py

# 5. Verificar links de navegação
grep -A1 "portfolio/risks\|portfolio/optimize\|portfolio/executive" templates/index.html
```

## ✅ Status Esperado Após Deploy

Quando tudo estiver funcionando:

1. **Menu Principal** deve ter os links:
   - Portfolio
   - Dashboard
   - Risks ← NOVO (Phase 4)
   - Optimize ← NOVO (Phase 5)
   - Executive ← NOVO (Phase 6)
   - Documentação

2. **Portfolio Dashboard** deve ter:
   - Botões "Excel" e "PDF" no topo ← NOVO (Phase 6)

3. **Portfolio Manager** deve ter:
   - Botões de export (Excel/PDF) ← NOVO (Phase 6)

4. **Novas Páginas Funcionando**:
   - /portfolio/risks - Portfolio Risk Management
   - /portfolio/optimize - Portfolio Optimization
   - /portfolio/executive - Executive Dashboard

## 📞 Se Ainda Não Funcionar

Se após seguir todos os passos as páginas ainda não aparecerem:

1. **Verifique os logs do servidor** para erros
2. **Verifique se o branch correto está ativo**:
   ```bash
   git branch
   # Deve mostrar: * claude/add-fold-stride-backtesting-011CUqfJiLhi5Gv73CdaHrKU
   ```

3. **Verifique se o último commit está presente**:
   ```bash
   git log --oneline -1
   # Deve mostrar: 799dea3 feat: Implement Phase 6...
   ```

4. **Limpe o cache do navegador**:
   - Pressione Ctrl+Shift+R (ou Cmd+Shift+R no Mac)
   - Ou abra em aba anônima

5. **Verifique permissões dos arquivos**:
   ```bash
   chmod 644 templates/portfolio_*.html
   chmod 644 static/js/portfolio_*.js
   chmod 644 portfolio_*.py
   ```

---

**Última atualização**: 2025-11-07
**Versão**: 6.0
**Todas as 6 phases estão commitadas e pushed para o repositório remoto**
