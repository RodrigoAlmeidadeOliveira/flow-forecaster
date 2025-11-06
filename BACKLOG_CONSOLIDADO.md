# 📋 BACKLOG CONSOLIDADO - Flow Forecaster
**Última Atualização:** 2025-11-06 (Revisado após análise de CoD)
**Status:** Lista única consolidada de todas as pendências

---

## ✅ RECÉM IMPLEMENTADO (Confirmar funcionamento)

### Sistema Completo de Custo de Atraso (CoD)
**Status:** ✅ **IMPLEMENTADO COMPLETO** (commits fa45951, 0b0869d, a81a3bb)

**O que foi implementado:**
- ✅ `cod_forecaster.py` com Random Forest + Gradient Boosting
- ✅ Features completas: budget, duration, team_size, stakeholders, business_value, complexity, risk_level, project_type
- ✅ Feature engineering: budget_per_week, stakeholder_density, value_per_week, risk_complexity_score
- ✅ K-Fold Cross-Validation (5 folds) + métricas (MAE, RMSE, R², MAPE)
- ✅ Cálculo dinâmico: `custo_total = custo_semanal × semanas_atraso`
- ✅ API completa: `/api/cod/predict`, `/api/cod/calculate_total`, `/api/cod/feature_importance`
- ✅ UI com aba "💰 Cost of Delay" no menu principal
- ✅ Visualização de resultados (weekly, daily, monthly CoD)
- ✅ Calculadora de custo total de atraso
- ✅ Gráfico de feature importance (horizontal bar chart)
- ✅ Ensemble predictions com intervalos de confiança (95% CI)
- ✅ Suite de testes completa (`test_cod_forecaster.py`)

**Arquivos:**
- `cod_forecaster.py` ✅
- `test_cod_forecaster.py` ✅
- `templates/index.html` (seção CoD) ✅
- `static/js/cost_of_delay.js` ✅
- `app.py` (endpoints CoD) ✅

**Nota:** Features #4 e #5 do FEATURES_ML_ROADMAP.md foram marcadas como implementadas.

---

## 🔥 CRÍTICO / URGENTE (Máximo Impacto)

### 1. Análise de Cenários (What-If Analysis)
**Prioridade:** ⭐⭐⭐⭐⭐ | **Esforço:** 1-2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Interface para criar 3 cenários: Otimista/Realista/Pessimista
- [ ] Comparação lado-a-lado em tabela e gráficos
- [ ] What-if interativo: "E se adicionar 2 pessoas ao time?"
- [ ] Sensitivity analysis: impacto de cada parâmetro no resultado
- [ ] Simulação de múltiplas estratégias simultaneamente
- [ ] Export de comparações de cenários

**Arquivos:**
- `src/scenario_analysis.py` (novo)
- `templates/scenario_comparison.html` (novo)
- `static/js/scenario.js` (novo)

---

### 2. Visualização de Feature Importance (ML Forecasting)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 3-5 dias | **Status:** 🟡 Parcialmente implementado

**Gap Identificado:** Feature #6 - Feature importance existe para CoD (✅), falta para ML Forecasting

**Já implementado:**
- ✅ Feature importance para CoD: `/api/cod/feature_importance` + gráfico na aba CoD
- ✅ Gráfico de barras horizontal na interface de CoD

**O que falta:**
- [ ] Adicionar endpoint `/api/ml/feature_importance` para modelos de throughput
- [ ] Gráfico de feature importance na aba de ML Forecasting
- [ ] Insights acionáveis automáticos (ex: "Lags de 3 semanas têm maior impacto")
- [ ] Feature importance por modelo (RF, XGBoost, Ridge, etc.)
- [ ] Comparação de importância entre modelos

**Arquivos:**
- `app.py` (adicionar endpoint)
- `templates/ml_forecasting.html` (adicionar seção)
- `ml_forecaster.py` (método get_feature_importance)

---

## 🟡 IMPORTANTE (Curto/Médio Prazo)

### 3. Visualizações Avançadas
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 1 semana | **Status:** 🟡 Parcial

**Gap Identificado:** Feature #12 - visualizações básicas existem, faltam avançadas

**Implementação:**
- [ ] **Scatter plot:** Duração vs Custo (correlações)
- [ ] **Box plot:** Distribuição por tipo de projeto/complexidade
- [ ] **Heatmap:** Correlação entre features do modelo
- [ ] **Violin plot:** Distribuições de throughput por período
- [ ] **Sunburst chart:** Hierarquia de riscos/dependências
- [ ] **Gantt probabilístico:** Timeline com intervalos de confiança

**Arquivos:**
- `templates/advanced_charts.html` (novo)
- `static/js/advanced_visualizations.js` (novo)

---

### 4. Upload de Dados Históricos (CSV/Excel)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 1 semana | **Status:** 🟡 DB existe, falta UI

**Gap Identificado:** Feature #13 - estrutura de DB pronta, falta interface

**Implementação:**
- [ ] UI para upload de CSV/Excel com projetos históricos
- [ ] Parser e validação automática de dados
- [ ] Mapeamento de colunas flexível (match automático + manual)
- [ ] Preview dos dados antes de importar
- [ ] Auto-retreino de modelos ML com novos dados
- [ ] Comparação: modelo genérico vs customizado
- [ ] Template CSV/Excel para download

**Arquivos:**
- `src/data_import.py` (novo)
- `templates/data_import.html` (novo)
- `static/js/file_upload.js` (novo)

---

### 5. Integração com Jira
**Prioridade:** ⭐⭐⭐⭐⭐ | **Esforço:** 2-3 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Autenticação com Jira (API Token + OAuth)
- [ ] Import automático de throughput (issues completadas por semana)
- [ ] Import de backlog atual (status, estimativas, prioridades)
- [ ] Sincronização periódica (webhook ou polling)
- [ ] Interface de configuração (URL, projeto, filtros JQL)
- [ ] Mapeamento de campos customizados
- [ ] Import de histórico (últimos 6-12 meses)

**Arquivos:**
- `integrations/jira_connector.py` (novo)
- `templates/integrations.html` (novo)
- `static/js/jira_config.js` (novo)

---

### 6. Export para PDF e Excel
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 1 semana | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Export de forecasts para PDF (biblioteca ReportLab ou WeasyPrint)
- [ ] Template profissional de relatório executivo
- [ ] Export para Excel com múltiplas abas e gráficos (openpyxl)
- [ ] Configuração de template (logo, cores, seções)
- [ ] Botão de export em cada análise
- [ ] Relatório automático agendado (diário/semanal)

**Arquivos:**
- `src/report_generator.py` (novo)
- `templates/report_config.html` (novo)
- `static/templates/report_template.html` (novo)

---

### 7. Dashboard de Portfolio (Multi-Projeto)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** 🟡 Análise existe, falta dashboard

**Implementação:**
- [ ] Lista consolidada de todos os projetos ativos
- [ ] Comparação de health score (MAPE, bias, trend)
- [ ] Análise de capacidade compartilhada entre projetos
- [ ] Matriz de priorização visual (valor vs risco)
- [ ] Alertas agregados por projeto
- [ ] Drill-down para análise individual
- [ ] Filtros por status, tipo, responsável

**Arquivos:**
- `templates/portfolio_dashboard.html` (novo)
- `static/js/portfolio.js` (novo)

---

### 8. Otimização Matemática de Portfólio
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Gap Identificado:** Feature #18 - análise existe, falta solver

**Implementação:**
- [ ] Integrar solver de Programação Linear (PuLP ou OR-Tools)
- [ ] Maximizar NPV total com restrições de orçamento/recursos
- [ ] Programação Inteira Mista para decisões binárias (fazer/não fazer)
- [ ] UI para definir restrições (orçamento, FTEs, diversificação)
- [ ] Análise de sensibilidade: impacto de relaxar restrições
- [ ] Visualização de trade-offs (fronteira de Pareto)

**Arquivos:**
- `src/portfolio_optimizer.py` (novo)
- `templates/optimization.html` (novo)

---

### 9. Modelo de Sucesso do Projeto (Classificação)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 1-2 semanas | **Status:** ❌ Não implementado

**Gap Identificado:** Feature #19 - ausente

**Implementação:**
- [ ] Random Forest Classifier para sucesso/falha
- [ ] Features: métricas de qualidade, satisfação cliente, scope changes
- [ ] Probabilidade de sucesso em tempo real na UI
- [ ] Fatores críticos de sucesso identificados automaticamente
- [ ] Alertas quando probabilidade < 70%
- [ ] Recomendações baseadas em projetos bem-sucedidos

**Arquivos:**
- `src/project_success_predictor.py` (novo)
- `templates/success_prediction.html` (novo)

---

## 🔬 AVANÇADO (Médio/Longo Prazo)

### 10. Análise de Tendências Automática
**Prioridade:** ⭐⭐⭐ | **Esforço:** 3-4 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Detecção automática de tendências (throughput melhorando/piorando)
- [ ] Análise de sazonalidade (ex: produtividade cai em dezembro)
- [ ] Detecção de anomalias nos dados (outliers, mudanças abruptas)
- [ ] Projeção de melhoria contínua: "Se melhorar 10% por sprint..."
- [ ] Alertas de degradação de performance
- [ ] Model drift detection (quando o modelo precisa ser retreinado)

**Arquivos:**
- `src/trend_analysis.py` (novo)
- `templates/trends.html` (novo)

---

### 11. Clustering e Análise de Causas Raiz
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Gap Identificado:** Feature #16

**Implementação:**
- [ ] K-Means/DBSCAN para agrupar projetos similares
- [ ] Análise de padrões em projetos atrasados vs bem-sucedidos
- [ ] Identificação automática de causas raiz de atrasos
- [ ] Recomendações baseadas em clusters de sucesso
- [ ] Visualização de clusters (PCA, t-SNE)

**Arquivos:**
- `src/clustering_analysis.py` (novo)
- `templates/root_cause.html` (novo)

---

### 12. Persistência e Versionamento de Modelos ML
**Prioridade:** ⭐⭐⭐ | **Esforço:** 1 semana | **Status:** 🟡 Cache existe, falta persistência

**Gap Identificado:** Feature #20

**Implementação:**
- [ ] Salvar modelos treinados em disco (pickle/joblib)
- [ ] Versionamento de modelos (MLflow ou similar)
- [ ] Comparação de versões de modelos
- [ ] Rollback para versão anterior
- [ ] Documentação automática (features, performance, data de treino)
- [ ] Compartilhamento de modelos entre equipes/organizações

**Arquivos:**
- `src/model_versioning.py` (novo)
- `models/` (diretório para modelos salvos)

---

### 13. Forecast de Defeitos/Bugs
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Modelo para prever quantidade de bugs baseado em histórico
- [ ] Features: complexidade, tamanho, tecnologia, maturidade da equipe
- [ ] Impacto de bugs na duração total do projeto
- [ ] Análise de padrões de bugs (quando ocorrem mais)
- [ ] Recomendações de alocação de tempo para correções

**Arquivos:**
- `src/defect_forecaster.py` (novo)

---

### 14. Technical Debt Impact Analysis
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Estimativa de impacto de technical debt na velocidade
- [ ] Análise de ROI de pagar dívida técnica vs features novas
- [ ] Forecast com diferentes níveis de tech debt
- [ ] Integração com ferramentas de análise de código (SonarQube)

**Arquivos:**
- `src/tech_debt_analyzer.py` (novo)

---

### 15. Correlação entre Riscos
**Prioridade:** ⭐⭐ | **Esforço:** 1-2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Análise de correlação entre riscos (riscos que ocorrem juntos)
- [ ] Rede de riscos (grafo de dependências)
- [ ] Simulação de cascata de riscos
- [ ] Identificação de riscos "chave" (maior impacto no sistema)

**Arquivos:**
- `src/risk_correlation.py` (novo)

---

### 16. Rolling Wave Planning Support
**Prioridade:** ⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Planejamento detalhado para próximo período + estimativas para futuro
- [ ] Forecast com granularidade variável (detalhado próximo, agregado futuro)
- [ ] Atualização incremental do plano

**Arquivos:**
- `src/rolling_wave.py` (novo)

---

### 17. Probabilistic Roadmaps
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2-3 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Roadmap visual com datas probabilísticas (P10-P90)
- [ ] Visualização de incerteza ao longo do tempo
- [ ] Milestones com intervalos de confiança
- [ ] Atualização automática conforme dados reais chegam

**Arquivos:**
- `templates/probabilistic_roadmap.html` (novo)
- `static/js/roadmap.js` (novo)

---

### 18. Process Behavior Charts (XmR Charts)
**Prioridade:** ⭐⭐⭐ | **Esforço:** 1-2 semanas | **Status:** ❌ Não implementado

**Solicitado pelo usuário - Controle estatístico de processo**

**Implementação:**
- [ ] Gráfico de controle XmR (Individual + Moving Range)
- [ ] Detecção de sinais especiais (regras de Western Electric)
- [ ] Cálculo de limites naturais de processo (NPL)
- [ ] Identificação de causas especiais vs variação comum
- [ ] Análise de estabilidade e previsibilidade do processo
- [ ] Alertas quando processo sai de controle

**Arquivos:**
- `src/process_behavior_charts.py` (novo)
- `templates/pbc.html` (novo)
- `static/js/control_charts.js` (novo)

---

## 🏢 PLATAFORMA & INFRAESTRUTURA

### 19. Autenticação Google OAuth2
**Prioridade:** ⭐⭐⭐⭐⭐ | **Esforço:** 1 semana | **Status:** ❌ Não implementado

**Solicitado pelo usuário - Obrigatório para multi-tenant**

**Implementação:**
- [ ] Configurar Google OAuth2 (credentials, redirect URIs)
- [ ] Login/logout via Google
- [ ] Gerenciamento de sessões
- [ ] Perfis de usuário (admin, viewer, editor)
- [ ] Isolamento de dados por usuário/organização
- [ ] Email de boas-vindas e onboarding

**Arquivos:**
- `src/auth.py` (novo)
- `templates/login.html` (novo)
- `templates/profile.html` (novo)

---

### 20. Sistema de Créditos e Monetização
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 2-3 semanas | **Status:** ❌ Não implementado

**Solicitado pelo usuário - Modelo de negócio**

**Implementação:**
- [ ] **Sistema de créditos:**
  - [ ] 1 crédito = 1 simulação Monte Carlo
  - [ ] Pacotes: 10, 50, 100, 500 créditos
  - [ ] Créditos expiram em 12 meses
  - [ ] Dashboard de consumo de créditos

- [ ] **Pagamentos PIX:**
  - [ ] Integração com API PIX (Mercado Pago, PagSeguro ou similar)
  - [ ] Geração de QR Code
  - [ ] Confirmação automática via webhook
  - [ ] Recibo automático

- [ ] **Pagamentos PayPal:**
  - [ ] Integração PayPal REST API
  - [ ] Checkout internacional
  - [ ] Webhooks para confirmação

- [ ] **Billing:**
  - [ ] Histórico de transações
  - [ ] Notas fiscais (integração com sistema contábil)
  - [ ] Planos de assinatura (opcional: ilimitado por mês)

**Arquivos:**
- `src/credits.py` (novo)
- `src/payments/pix_integration.py` (novo)
- `src/payments/paypal_integration.py` (novo)
- `templates/pricing.html` (novo)
- `templates/billing.html` (novo)

---

### 21. Wizards e Onboarding Guiado
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Wizard step-by-step para primeira análise
- [ ] Templates por tipo de projeto (Scrum, Kanban, SAFe, Waterfall)
- [ ] Tutorial interativo (tour guiado)
- [ ] Samples de dados prontos para teste
- [ ] Video tutorials integrados
- [ ] FAQ contextual

**Arquivos:**
- `templates/onboarding.html` (novo)
- `static/js/wizard.js` (novo)
- `static/samples/` (dados de exemplo)

---

### 22. API REST Completa
**Prioridade:** ⭐⭐⭐ | **Esforço:** 2 semanas | **Status:** 🟡 Parcial

**Implementação:**
- [ ] Documentação OpenAPI/Swagger
- [ ] Endpoints para todas as funcionalidades
- [ ] Autenticação via API Key
- [ ] Rate limiting
- [ ] Webhooks para eventos (forecast concluído, alerta gerado)
- [ ] SDK Python e JavaScript

**Arquivos:**
- `api/` (novo diretório)
- `docs/api_documentation.html` (novo)

---

## 🎓 P.R.I.O.R.I.S. - DOUTORADO (Funcionalidades Separadas)

**Contexto:** Base para pesquisa de doutorado usando process mining, telemetria e ML

### 23. Integração com Azure DevOps (com Process Mining)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 3-4 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] **Conector Azure DevOps:**
  - [ ] Autenticação (PAT, OAuth)
  - [ ] Import de Work Items (backlog, tasks, bugs)
  - [ ] Import de histórico de mudanças de estado
  - [ ] Análise de velocity por sprint/release

- [ ] **Process Mining:**
  - [ ] Extração de event log (Work Item State Changes)
  - [ ] Descoberta de processo (BPMN) usando PM4Py
  - [ ] Análise de conformidade (desvios do processo ideal)
  - [ ] Bottleneck analysis
  - [ ] Variant analysis (diferentes caminhos do fluxo)

- [ ] **Telemetria e Features para ML:**
  - [ ] Tempo em cada estado
  - [ ] Número de transições
  - [ ] Rework rate (quantas vezes volta para To Do)
  - [ ] Lead time por tipo de Work Item
  - [ ] Handoffs entre pessoas/equipes
  - [ ] Ciclo time vs WIP

**Arquivos:**
- `prioris/integrations/azure_connector.py` (novo)
- `prioris/process_mining/event_log_extractor.py` (novo)
- `prioris/process_mining/process_discovery.py` (novo)
- `prioris/ml/process_features.py` (novo)

---

### 24. Integração com GitHub (com Process Mining)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 3-4 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] **Conector GitHub:**
  - [ ] Autenticação (GitHub Apps, OAuth)
  - [ ] Import de Issues, PRs, Projects
  - [ ] Import de commits, code reviews
  - [ ] Métricas de código (LOC, churn, complexity)

- [ ] **Process Mining:**
  - [ ] Event log de Issues (opened → in progress → review → closed)
  - [ ] Event log de PRs (created → review → approved → merged)
  - [ ] Análise de code review process
  - [ ] Social network analysis (quem colabora com quem)

- [ ] **Telemetria e Features para ML:**
  - [ ] PR cycle time
  - [ ] Número de revisões antes de merge
  - [ ] Time to first review
  - [ ] Code churn por developer
  - [ ] Defect density por módulo
  - [ ] Coupling entre módulos (análise de co-changes)

**Arquivos:**
- `prioris/integrations/github_connector.py` (novo)
- `prioris/process_mining/github_event_log.py` (novo)
- `prioris/ml/code_metrics_features.py` (novo)

---

### 25. Process Mining Dashboard (P.R.I.O.R.I.S.)
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 4 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Visualização de processo descoberto (BPMN, Petri Net, DFG)
- [ ] Heatmap de frequência e tempo por atividade
- [ ] Análise de conformidade (modelo real vs ideal)
- [ ] Dashboards de performance:
  - [ ] Throughput time
  - [ ] Waiting time
  - [ ] Processing time
  - [ ] Rework rate
- [ ] Filtros por período, equipe, tipo de trabalho
- [ ] Export de event logs para análise externa (XES format)

**Arquivos:**
- `prioris/templates/process_mining_dashboard.html` (novo)
- `prioris/static/js/process_viz.js` (novo)

---

### 26. Machine Learning com Features de Processo
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 4-6 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] **Feature Engineering de Processo:**
  - [ ] Métricas de fluxo (lead time, cycle time, WIP)
  - [ ] Métricas de qualidade (rework rate, defect density)
  - [ ] Métricas de colaboração (handoffs, bus factor)
  - [ ] Métricas de complexidade (cognitive complexity, cyclomatic)
  - [ ] Padrões temporais (sazonalidade, tendências)

- [ ] **Modelos Preditivos:**
  - [ ] Predição de lead time baseado em características do Work Item
  - [ ] Predição de risco de atraso
  - [ ] Predição de qualidade (probabilidade de defeitos)
  - [ ] Classificação de Work Items (epic, feature, task)
  - [ ] Recomendação de assignee ideal

- [ ] **Análise Causal:**
  - [ ] Identificação de fatores que impactam performance
  - [ ] What-if analysis baseado em mudanças de processo
  - [ ] Simulação de melhorias de processo

**Arquivos:**
- `prioris/ml/process_feature_engineering.py` (novo)
- `prioris/ml/predictive_models.py` (novo)
- `prioris/ml/causal_analysis.py` (novo)

---

### 27. Arqueologia de Processos (Process Archaeology)
**Prioridade:** ⭐⭐⭐ | **Esforço:** 3-4 semanas | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Reconstrução de processos históricos a partir de logs
- [ ] Análise de evolução do processo ao longo do tempo
- [ ] Detecção de mudanças estruturais no processo
- [ ] Análise de drift (quando e como o processo mudou)
- [ ] Comparação de processos entre equipes/períodos
- [ ] Identificação de best practices emergentes

**Arquivos:**
- `prioris/archaeology/process_reconstruction.py` (novo)
- `prioris/archaeology/drift_detection.py` (novo)

---

### 28. Menu Separado P.R.I.O.R.I.S.
**Prioridade:** ⭐⭐⭐⭐ | **Esforço:** 1 semana | **Status:** ❌ Não implementado

**Implementação:**
- [ ] Menu separado na navegação principal
- [ ] Landing page P.R.I.O.R.I.S. com explicação da pesquisa
- [ ] Acesso controlado (pode ser feature premium)
- [ ] Documentação da metodologia
- [ ] Links para artigos/publicações
- [ ] Casos de estudo

**Arquivos:**
- `prioris/templates/prioris_home.html` (novo)
- `prioris/static/css/prioris_theme.css` (novo)

---

## 📊 RESUMO EXECUTIVO

### Por Status:
- ✅ **Implementado Completo:** 13 features (incluindo CoD recém confirmado)
- 🟡 **Implementado Parcial:** 6 features (precisam ser completadas)
- ❌ **Não Implementado:** 28 features (backlog pendente)

### Por Prioridade:
- 🔥 **CRÍTICO/URGENTE:** 2 features (0-4 semanas)
- ⭐⭐⭐⭐⭐ **MUITO ALTA:** 9 features (1-3 meses)
- ⭐⭐⭐⭐ **ALTA:** 8 features (2-4 meses)
- ⭐⭐⭐ **MÉDIA:** 8 features (4-6 meses)
- ⭐⭐ **BAIXA:** 4 features (6+ meses)

### Por Categoria:
- **ML & Forecasting:** 7 features (CoD ✅)
- **Visualizações:** 3 features (CoD feature importance ✅)
- **Integrações:** 4 features
- **Plataforma:** 5 features
- **P.R.I.O.R.I.S. (Doutorado):** 6 features
- **Otimização:** 3 features
- **Qualidade & Validação:** 4 features

---

## 🎯 ROADMAP SUGERIDO

### **FASE 1 (0-2 meses) - Foundation**
Implementar features críticas para viabilizar o produto:
1. Google OAuth2 (#19)
2. Sistema de Créditos e Pagamentos (#20)
3. Análise de Cenários (#1)
4. Feature Importance UI para ML Forecasting (#2)
5. Visualizações Avançadas (#3)

**Resultado:** Produto monetizável com features core completas
**Nota:** CoD já implementado ✅

---

### **FASE 2 (2-4 meses) - Growth**
Expandir funcionalidades e integrações:
1. Integração Jira (#5)
2. Upload de Dados (#4)
3. Export PDF/Excel (#6)
4. Dashboard Portfolio (#7)
5. Modelo de Sucesso (#9)
6. Wizards e Onboarding (#21)

**Resultado:** Produto enterprise-ready com integrações principais

---

### **FASE 3 (4-6 meses) - Advanced**
Features avançadas de otimização e ML:
1. Otimização Matemática (#8)
2. Análise de Tendências (#10)
3. Process Behavior Charts (#18)
4. Forecast de Defeitos (#13)
5. Clustering e Causas Raiz (#11)
6. API REST Completa (#22)

**Resultado:** Plataforma completa e diferenciada

---

### **FASE 4 (6-12 meses) - P.R.I.O.R.I.S.**
Funcionalidades de pesquisa (doutorado):
1. Azure DevOps com Process Mining (#23)
2. GitHub com Process Mining (#24)
3. Process Mining Dashboard (#25)
4. ML com Features de Processo (#26)
5. Arqueologia de Processos (#27)
6. Menu Separado P.R.I.O.R.I.S. (#28)

**Resultado:** Base para publicações acadêmicas e diferencial científico

---

## 📝 OBSERVAÇÕES

### Melhorias Implementadas Recentemente:
- ✅ **Sistema Completo de Cost of Delay (CoD)** - commits fa45951, 0b0869d, a81a3bb
- ✅ Fold stride no backtesting - commit 857b60b
- ✅ Forecast vs Actual Tracking - implementado
- ✅ Persistência e Histórico - implementado

### Dependências Críticas:
- **OAuth2** deve ser implementado antes do sistema de créditos
- **Upload de dados** é pré-requisito para modelos customizados
- **Jira integration** aumenta drasticamente a adoção
- **P.R.I.O.R.I.S.** pode ser desenvolvido em paralelo ao roadmap principal

### Riscos:
- Scope muito grande - priorização é crítica
- Integrações externas (Jira, Azure, GitHub) têm complexidade alta
- Process Mining requer expertise específica
- Monetização precisa validar modelo de negócio (créditos vs assinatura)

---

**Documento gerado por:** Claude Code (Sonnet 4.5)
**Baseado em:** FEATURES_ML_ROADMAP.md + análises de 27/10, 05/11 e 06/11 + requisitos do usuário
**Última revisão:** 06/11/2025 - Confirmado implementação completa de CoD (✅)
