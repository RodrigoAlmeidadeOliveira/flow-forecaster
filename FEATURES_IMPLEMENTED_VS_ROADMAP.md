# Análise Comparativa: Features Implementadas vs Roadmap ML

**Data da Análise:** 2025-11-05
**Baseado em:** Notebooks do Workshop MCS/ML + Código do Flow-Forecaster

---

## 📊 Resumo Executivo

Esta análise compara as funcionalidades propostas no **FEATURES_ML_ROADMAP.md** com o que já foi implementado no **flow-forecaster** e nos notebooks do Workshop MCS/ML.

### Status Geral:
- ✅ **Implementado Completo:** 12 features (60%)
- 🟡 **Implementado Parcial:** 5 features (25%)
- ❌ **Não Implementado:** 3 features (15%)

---

## 🎯 Análise Detalhada por Prioridade

## ✅ PRIORIDADE ALTA - Predição de Prazos

### Feature #1: Regressão Linear para Duração de Projetos
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py`: Ridge Regression implementado (linhas 182-186)
- ✅ Pipeline com StandardScaler (linhas 182-186)
- ✅ Features incluem lags, rolling mean/std
- ✅ Intervalos de confiança via percentis (P10, P25, P50, P75, P90)
- ✅ Cross-validation com K-Fold (TimeSeriesSplit)

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Regressão Linear + Ridge completos
- ✅ Features: tamanho_equipe, experiencia_pm, orcamento, complexidade
- ✅ Intervalos de confiança calibrados
- ✅ Predição com dados históricos

#### O que falta:
- 🟡 **Calibração específica com dados do usuário** (framework existe, precisa exposição na UI)
- 🟡 **Features de projeto** (tipo, complexidade) não estão no modelo atual (usa apenas throughput histórico)

---

### Feature #2: Pipeline de Pré-processamento
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:182-198`: Pipeline sklearn completo
  ```python
  'Ridge': Pipeline([
      ('scaler', StandardScaler()),
      ('ridge', Ridge())
  ])
  ```
- ✅ StandardScaler para normalização
- ✅ Features automáticas: lags, rolling statistics
- ✅ Encoding não aplicável (modelo usa séries temporais, não categóricas)

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Pipeline com PolynomialFeatures
- ✅ One-hot encoding para variáveis categóricas

#### O que falta:
- ✅ **Nada crítico** - Pipeline completo e funcional

---

### Feature #3: Validação e Métricas de Qualidade
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:276-290`: Avaliação com Time Series Cross-Validation
- ✅ `ml_forecaster.py:355-503`: K-Fold CV completo (5 folds)
- ✅ Métricas: MAE, RMSE, R² Score (linhas 456-465)
- ✅ `ml_forecaster.py:666-858`: Walk-Forward Validation implementado
- ✅ Grid Search para otimização de hiperparâmetros (linhas 404-427)
- ✅ Análise de resíduos e detecção de outliers (linhas 876-893)

#### Nos Notebooks:
- ✅ `04_validacao_calibracao_modelos.ipynb`: Validação robusta completa
- ✅ Cross-validation temporal
- ✅ Análise de resíduos (Q-Q plots, histogramas)
- ✅ Testes estatísticos (Shapiro-Wilk, Durbin-Watson)

#### O que falta:
- ✅ **Nada crítico** - Sistema de validação robusto

---

## 🔥 PRIORIDADE ALTA - Custo de Atraso (CoD)

### Feature #4: Random Forest para Estimativa de CoD
**Status: ❌ NÃO IMPLEMENTADO**

#### No Flow-Forecaster:
- ✅ Random Forest existe para **throughput** (`ml_forecaster.py:156-161`)
- ❌ **Não existe modelo específico para CoD**
- ❌ Não calcula custo de atraso (R$/semana)
- ✅ Dependency Analyzer existe (`dependency_analyzer.py`) mas não integrado com CoD

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Random Forest para CoD completo
- ✅ Features: orcamento, stakeholders, tipo de projeto, duração
- ✅ Feature importance automática
- ✅ Otimização de hiperparâmetros via Grid Search

#### O que precisa ser implementado:
- ❌ **Modelo Random Forest dedicado para CoD**
- ❌ **Cálculo de custo de atraso semanal** (R$/semana)
- ❌ **Custo total de atraso** = custo_semanal × semanas_atraso
- ❌ **UI para configurar fatores de CoD** (impacto mercado, penalidades, etc.)

---

### Feature #5: Cálculo Dinâmico de CoD
**Status: ❌ NÃO IMPLEMENTADO**

#### No Flow-Forecaster:
- ❌ Nenhuma funcionalidade de CoD implementada
- ✅ Sistema de dependências (`dependency_analyzer.py`) que poderia alimentar CoD

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Cálculo completo de CoD
- ✅ Fórmula: `custo_total = custo_semanal × atraso_semanas`
- ✅ Fatores configuráveis por projeto

#### O que precisa ser implementado:
- ❌ **Integração duração predita → CoD total**
- ❌ **Input customizado de fatores de CoD** na UI
- ❌ **Visualização de impacto financeiro de atrasos**

---

### Feature #6: Visualização de Feature Importance
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ✅ Random Forest tem feature importance nativo
- ❌ **Não exposto na UI** (não há visualização)
- ❌ Não há insights acionáveis

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Gráficos de feature importance
- ✅ `16_planejamento_riscos.ipynb`: Feature importance para classificação de riscos
- ✅ Insights acionáveis (ex: "Reduzir mudanças de escopo diminui 30% do risco")

#### O que precisa ser implementado:
- ❌ **Gráfico de barras** mostrando feature importance na UI
- ❌ **Insights automáticos** baseados nas features mais importantes
- ❌ **Recomendações acionáveis** para PMOs

---

## ⚙️ PRIORIDADE MÉDIA - Otimização e Modelos Avançados

### Feature #7: Grid Search para Hiperparâmetros
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:292-333`: Grid Search implementado
- ✅ Parâmetros otimizados para: RandomForest, XGBoost, HistGradient, Ridge, Lasso, KNN, SVR
- ✅ Busca automática com cross-validation
- ✅ Salvamento automático dos melhores parâmetros (linhas 420-422)

#### O que falta:
- ✅ **Nada crítico** - Grid Search completo

---

### Feature #8: Gradient Boosting como Alternativa
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:162-181`: HistGradientBoostingRegressor implementado
- ✅ Três variantes: Median, P10, P90 (quantile regression)
- ✅ XGBoost disponível como opcional (linhas 200-208)
- ✅ Seleção automática do melhor modelo baseado em MAE

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Gradient Boosting implementado
- ✅ Comparação lado a lado com Random Forest

#### O que falta:
- ✅ **Nada crítico** - GB completo

---

### Feature #9: Modelos de Ensemble
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:570-597`: Ensemble completo
- ✅ Estratégia: Voting (média, mediana)
- ✅ Percentis agregados: P10, P25, P50, P75, P90
- ✅ Desvio padrão agregado
- ✅ Forecast com múltiplos modelos: `forecast(model_name='ensemble')`

#### O que falta:
- 🟡 **Stacking** (meta-modelo que aprende a combinar) não implementado

---

## 🔬 PRIORIDADE MÉDIA - Integração ML + Monte Carlo

### Feature #10: Simulação Unificada ML + Monte Carlo
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_deadline_forecaster.py`: Classe `MLDeadlineForecaster` completa
- ✅ Integração ML + Monte Carlo (linhas 155-251)
- ✅ Simulação com team dynamics (S-curve)
- ✅ Variação de parâmetros: split rate, lead time
- ✅ Distribuições de resultados (P10-P95)
- ✅ Análise de dependências integrada (linhas 63-66, 102-126)

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Classe `PreditorProjetos` com ML + MC
- ✅ Variação de parâmetros com distribuições (triangular, normal, poisson)

#### O que falta:
- ✅ **Nada crítico** - Integração completa

---

### Feature #11: Métricas de Risco Avançadas
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `ml_forecaster.py:860-894`: `assess_forecast_risk()` - Avaliação de risco
- ✅ Métricas: volatility CV, trend deviation, outliers
- ✅ Risk level: LOW/MEDIUM/HIGH
- ✅ Recomendação automática de Monte Carlo quando risco alto
- ✅ `ml_deadline_forecaster.py:229-250`: Percentile stats (P10-P95)
- ✅ Análise de sensibilidade via ensemble stats

#### Nos Notebooks:
- ✅ `04_validacao_calibracao_modelos.ipynb`: Métricas de risco extensas
- ✅ Probabilidade de cenários específicos

#### O que falta:
- ✅ **Nada crítico** - Métricas robustas

---

### Feature #12: Visualizações Integradas
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ✅ `app.py`: Visualizações básicas com Chart.js
- ✅ Histogramas de distribuição
- ✅ Gráficos de percentis
- ❌ **Scatter plots** de correlação não implementados
- ❌ **Box plots** por categoria não implementados
- ❌ **Heatmaps** de correlação não implementados

#### Nos Notebooks:
- ✅ Todos os notebooks têm visualizações ricas com Matplotlib/Seaborn
- ✅ Scatter plots, box plots, heatmaps, Q-Q plots

#### O que precisa ser implementado:
- ❌ **Scatter plot** de duração vs custo na UI
- ❌ **Box plot** por tipo de projeto/complexidade
- ❌ **Heatmap** de correlação entre features
- ❌ **Gráfico de feature importance**

---

## 📊 PRIORIDADE BAIXA - Dados Históricos e Aprendizado

### Feature #13: Sistema de Dados Históricos
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ✅ `models.py`: Sistema de banco de dados com SQLAlchemy
- ✅ Tabelas: Project, Forecast, Actual
- ✅ `accuracy_metrics.py`: Comparação forecast vs actual
- ✅ Versionamento via timestamps
- ❌ **Upload de CSV/Excel** não implementado na UI
- ❌ Auto-treinamento com novos dados não automático

#### Nos Notebooks:
- ✅ `04_validacao_calibracao_modelos.ipynb`: Sistema de dados históricos sintéticos
- ✅ Geração e calibração com dados do usuário

#### O que precisa ser implementado:
- ❌ **UI para upload** de CSV/Excel com projetos históricos
- ❌ **Auto-retreino** quando novos projetos são adicionados
- ❌ **Comparação**: modelo genérico vs customizado

---

### Feature #14: Comparação Predição vs Real
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `accuracy_metrics.py`: Métricas completas (MAPE, MAE, Bias)
- ✅ `portfolio_analyzer.py`: Dashboard de acurácia histórica
- ✅ `backtesting.py`: Sistema de backtesting
- ✅ Gráficos de Predito vs Real via Chart.js

#### Nos Notebooks:
- ✅ `04_validacao_calibracao_modelos.ipynb`: Análise completa de predição vs real
- ✅ Q-Q plots, scatter plots, análise de resíduos

#### O que falta:
- ✅ **Nada crítico** - Sistema completo

---

### Feature #15: Gerador de Dados Sintéticos
**Status: ✅ IMPLEMENTADO COMPLETO**

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: `gerar_dados_projetos(n=500)`
- ✅ `04_validacao_calibracao_modelos.ipynb`: `gerar_dados_historicos_temporais()`
- ✅ Parâmetros configuráveis: tipo org, maturidade, mix de projetos
- ✅ Dados seguem regras realistas

#### No Flow-Forecaster:
- ❌ Não implementado (não é crítico para produção)

#### O que precisa ser implementado:
- 🟡 **Opcional**: Adicionar na UI para demonstração/testes

---

## 🧪 PRIORIDADE BAIXA - Features Experimentais

### Feature #16: Análise de Causas de Atraso
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ❌ Clustering não implementado
- ✅ `portfolio_analyzer.py`: Análise de projetos críticos
- ✅ Alertas automáticos sobre projetos em risco

#### Nos Notebooks:
- ✅ `16_planejamento_riscos.ipynb`: Análise de padrões em riscos
- ✅ Identificação de cenários de alto impacto

#### O que precisa ser implementado:
- ❌ **Clustering** (K-Means, DBSCAN) para agrupar projetos similares
- ❌ **Análise de causas raiz** de atrasos
- ❌ **Recomendações baseadas** em projetos bem-sucedidos

---

### Feature #17: Alertas Preditivos
**Status: ✅ IMPLEMENTADO COMPLETO**

#### No Flow-Forecaster:
- ✅ `portfolio_analyzer.py:359-419`: Sistema de alertas completo
- ✅ Alertas por severity: critical, high, medium
- ✅ Categorias: health, capacity, forecast, risk
- ✅ Recomendações automáticas de ações

#### O que falta:
- 🟡 **Integração com email/Slack** não implementada
- 🟡 **Dashboard de projetos em risco** existe mas pode ser melhorado

---

### Feature #18: Otimização de Portfólio
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ✅ `portfolio_analyzer.py:299-356`: Matriz de priorização (valor vs risco)
- ✅ `portfolio_analyzer.py:216-296`: Análise de capacidade
- ❌ **Otimização matemática** (Programação Linear) não implementada

#### Nos Notebooks:
- ✅ `05_otimizacao_portfolio.ipynb`: Otimização completa com PuLP
- ✅ Programação Inteira Mista
- ✅ Maximização de NPV com restrições
- ✅ Análise de sensibilidade

#### O que precisa ser implementado:
- ❌ **Solver de otimização** (PuLP ou similar) no flow-forecaster
- ❌ **Maximizar valor vs risco** com restrições de orçamento
- ❌ **UI para definir restrições** (orçamento, recursos, diversificação)

---

### Feature #19: Modelo de Sucesso do Projeto
**Status: ❌ NÃO IMPLEMENTADO**

#### Nos Notebooks:
- ✅ `03_ferramentas_machine_learning.ipynb`: Classificação binária (sucesso/falha)
- ✅ Random Forest Classifier
- ✅ Probabilidade de sucesso

#### No Flow-Forecaster:
- ❌ Nenhum modelo de classificação implementado

#### O que precisa ser implementado:
- ❌ **Random Forest Classifier** para sucesso/falha
- ❌ **Features**: métricas de qualidade, satisfação do cliente
- ❌ **Probabilidade de sucesso** em tempo real na UI
- ❌ **Fatores críticos de sucesso** identificados automaticamente

---

### Feature #20: Export de Modelos Treinados
**Status: 🟡 IMPLEMENTADO PARCIAL**

#### No Flow-Forecaster:
- ✅ Modelos são salvos em memória (cache)
- ✅ `ml_deadline_forecaster.py:126-153`: Cache de modelos treinados
- ❌ **Não persiste em disco** (pickle/joblib)
- ❌ **Sem API REST** para predições em batch

#### O que precisa ser implementado:
- ❌ **Salvar modelos** em pickle/joblib para persistência
- ❌ **Compartilhar modelos** entre equipes
- ❌ **API REST** para predições (`/api/predict`)
- ❌ **Documentação automática** do modelo (features, performance, data de treino)

---

## 📈 Resumo por Status

### ✅ Implementado Completo (12 features):
1. ✅ Feature #1: Regressão Linear para Duração
2. ✅ Feature #2: Pipeline de Pré-processamento
3. ✅ Feature #3: Validação e Métricas
4. ✅ Feature #7: Grid Search
5. ✅ Feature #8: Gradient Boosting
6. ✅ Feature #9: Modelos de Ensemble
7. ✅ Feature #10: Simulação ML + MC
8. ✅ Feature #11: Métricas de Risco Avançadas
9. ✅ Feature #14: Comparação Predição vs Real
10. ✅ Feature #15: Gerador de Dados Sintéticos (notebooks)
11. ✅ Feature #17: Alertas Preditivos

### 🟡 Implementado Parcial (5 features):
1. 🟡 Feature #6: Visualização Feature Importance (existe mas não exposto)
2. 🟡 Feature #12: Visualizações Integradas (básicas, faltam scatter/box/heatmap)
3. 🟡 Feature #13: Sistema de Dados Históricos (DB existe, falta upload UI)
4. 🟡 Feature #16: Análise de Causas (alertas existem, falta clustering)
5. 🟡 Feature #18: Otimização de Portfólio (análise existe, falta solver)
6. 🟡 Feature #20: Export de Modelos (cache existe, falta persistência)

### ❌ Não Implementado (3 features):
1. ❌ Feature #4: Random Forest para CoD
2. ❌ Feature #5: Cálculo Dinâmico de CoD
3. ❌ Feature #19: Modelo de Sucesso do Projeto

---

## 🎯 Prioridades de Implementação

### 🔥 **Urgente (Máximo Valor):**

1. **Feature #4 + #5: Sistema Completo de CoD**
   - **Esforço:** 2-3 semanas
   - **Impacto:** ALTO - Funcionalidade crítica ausente
   - **Implementação:**
     - Criar `cod_forecaster.py` com Random Forest
     - Features: orcamento, stakeholders, tipo, duração predita
     - UI para configurar fatores de CoD
     - Visualização de impacto financeiro

2. **Feature #6: Visualização Feature Importance**
   - **Esforço:** 3-5 dias
   - **Impacto:** MÉDIO - Facilita interpretação do modelo
   - **Implementação:**
     - Adicionar endpoint `/api/feature_importance`
     - Gráfico de barras no dashboard
     - Insights acionáveis automáticos

3. **Feature #12: Visualizações Avançadas**
   - **Esforço:** 1 semana
   - **Impacto:** MÉDIO - Melhora análise exploratória
   - **Implementação:**
     - Scatter plot de correlações
     - Box plot por categoria
     - Heatmap de correlação

### 🟡 **Importante (Curto Prazo):**

4. **Feature #13: Upload de Dados Históricos**
   - **Esforço:** 1 semana
   - **Impacto:** MÉDIO - Personalização do modelo
   - **Implementação:**
     - UI para upload CSV/Excel
     - Parser e validação de dados
     - Auto-retreino com novos dados

5. **Feature #18: Otimização Matemática de Portfólio**
   - **Esforço:** 2 semanas
   - **Impacto:** ALTO - Diferencial competitivo
   - **Implementação:**
     - Integrar PuLP ou similar
     - Solver de Programação Linear
     - UI para definir restrições e objetivos

6. **Feature #19: Modelo de Sucesso do Projeto**
   - **Esforço:** 1-2 semanas
   - **Impacto:** MÉDIO - Predição adicional valiosa
   - **Implementação:**
     - Random Forest Classifier
     - Features de qualidade e satisfação
     - Probabilidade de sucesso na UI

### 🟢 **Desejável (Médio Prazo):**

7. **Feature #16: Clustering e Análise de Causas**
   - **Esforço:** 2 semanas
   - **Impacto:** BAIXO-MÉDIO - Insights avançados
   - **Implementação:**
     - K-Means/DBSCAN para agrupar projetos
     - Análise de causas raiz
     - Recomendações baseadas em clusters

8. **Feature #20: Persistência e API de Modelos**
   - **Esforço:** 1 semana
   - **Impacto:** BAIXO-MÉDIO - Escalabilidade
   - **Implementação:**
     - Salvar modelos em pickle/joblib
     - API REST para predições
     - Documentação automática

---

## 📊 Análise de Gap por Notebook

### Notebook: `03_ferramentas_machine_learning.ipynb`
**Implementado:** 70%
- ✅ Regressão Linear/Ridge
- ✅ Random Forest para throughput
- ✅ Ensemble de modelos
- ✅ Integração ML + Monte Carlo
- ❌ Random Forest para CoD (não implementado)
- ❌ Feature importance visualizado (não exposto)

### Notebook: `04_validacao_calibracao_modelos.ipynb`
**Implementado:** 90%
- ✅ Ajuste de distribuições aos dados
- ✅ Cross-validation temporal
- ✅ Calibração probabilística
- ✅ Model drift detection
- ✅ Análise de resíduos completa
- 🟡 Testes estatísticos avançados (Shapiro-Wilk) não expostos na UI

### Notebook: `05_otimizacao_portfolio.ipynb`
**Implementado:** 40%
- ✅ Análise de capacidade
- ✅ Matriz de priorização
- ❌ Programação Linear (PuLP) não implementada
- ❌ Maximização de NPV com restrições
- ❌ Análise de sensibilidade matemática

### Notebook: `16_planejamento_riscos.ipynb`
**Implementado:** 60%
- ✅ Simulação Monte Carlo de riscos
- ✅ Análise de impacto financeiro
- ❌ Random Forest para classificação de riscos de alto impacto
- ❌ Feature importance para riscos

### Notebook: `00_sintese_proximos_passos.ipynb`
**Implementado:** 50%
- ✅ Pipeline básico de ML + MC
- ✅ Integração com BI (parcial)
- ❌ Templates de Power BI não criados
- ❌ Automação de reports não implementada

---

## 🚀 Roadmap de Implementação Sugerido

### **Sprint 1 (2 semanas): Sistema de CoD**
- Dia 1-3: Criar `cod_forecaster.py` com Random Forest
- Dia 4-7: UI para configurar fatores de CoD
- Dia 8-10: Integração com duração predita
- Dia 11-14: Visualizações e testes

### **Sprint 2 (2 semanas): Visualizações e Upload**
- Dia 1-5: Feature importance + scatter/box/heatmap
- Dia 6-10: Upload de CSV/Excel históricos
- Dia 11-14: Auto-retreino com novos dados

### **Sprint 3 (2 semanas): Otimização e Classificação**
- Dia 1-7: Solver de otimização (PuLP) + UI
- Dia 8-14: Modelo de sucesso do projeto (Classifier)

### **Sprint 4 (1-2 semanas): Refinamentos**
- Clustering e análise de causas
- Persistência de modelos (pickle)
- API REST para predições
- Documentação e testes

**Total: 7-8 semanas** para implementar todas as features faltantes.

---

## 📝 Observações Finais

### Pontos Fortes do Flow-Forecaster:
1. ✅ **ML robusto**: Multiple models, ensemble, K-Fold CV
2. ✅ **Integração ML + MC**: Implementação única e poderosa
3. ✅ **Dependency analysis**: Sistema de dependências avançado
4. ✅ **Walk-forward validation**: Validação temporal correta
5. ✅ **Portfolio analyzer**: Análise de portfólio já implementada
6. ✅ **Backtesting**: Sistema de backtesting completo

### Principais Gaps:
1. ❌ **Custo de Atraso (CoD)**: Ausente - funcionalidade crítica
2. ❌ **Feature importance UI**: Não visível para o usuário
3. ❌ **Otimização matemática**: Solver não implementado
4. ❌ **Classificação de sucesso**: Modelo não existe
5. 🟡 **Upload de dados**: DB existe mas falta UI
6. 🟡 **Visualizações avançadas**: Básicas implementadas

### Recomendação:
**Focar nas features #4, #5, #6 e #18** que têm o maior impacto e são relativamente rápidas de implementar. Isso levaria o flow-forecaster de 75% de completude para **90%+** em ~5-6 semanas.

---

**Análise realizada por:** Claude Code (Sonnet 4.5)
**Notebooks analisados:** 5 notebooks do Workshop MCS/ML
**Arquivos Python analisados:** 20+ módulos do flow-forecaster
