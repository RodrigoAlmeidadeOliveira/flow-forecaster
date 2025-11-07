# 📋 Inventário Completo do Flow Forecaster
## Análise para Visão Integrada: Itens → Projetos → Portfólio

**Data**: 2025-11-06
**Objetivo**: Melhorar portfólio com visão integrada de forecasting em 3 níveis

---

## 🏗️ ARQUITETURA ATUAL

### 📂 Estrutura de Módulos Python

#### ✅ Backend Core (Bem Implementado)
```
✅ app.py                      - Flask app (117 KB, 3100+ linhas)
✅ models.py                   - SQLAlchemy models (User, Project, Forecast, Actual)
✅ database.py                 - Database utilities
✅ monte_carlo.py              - Simulações Monte Carlo (legado)
✅ monte_carlo_unified.py      - MC unificado (55 KB)
✅ ml_forecaster.py            - Machine Learning (35 KB, 9 modelos)
✅ ml_deadline_forecaster.py  - ML para deadlines (23 KB)
✅ backtesting.py              - Backtesting (fold_stride implemented)
✅ accuracy_metrics.py         - Métricas MAPE, RMSE, R², MAE
```

#### ⚠️ Módulos Parcialmente Implementados
```
🟡 portfolio_analyzer.py       - Análise de portfólio (15 KB)
   ✅ Tem: ProjectHealthScore, CapacityAnalysis, PrioritizationMatrix
   ❌ Falta: Integração com CoD, Simulações agregadas, Risk rollup

🟡 cod_forecaster.py           - Cost of Delay ML (12 KB)
   ✅ Tem: Random Forest para CoD individual
   ❌ Falta: Visão de portfólio, Otimização WSJF, Priorização dinâmica

🟡 dependency_analyzer.py      - Análise de dependências (22 KB)
   ✅ Tem: Dependency graph, Critical path
   ❌ Falta: Portfolio-level dependencies, Cross-project impact

🟡 trend_analysis.py           - Análise de tendências (32 KB)
   ✅ Tem: Detecção de tendências, Sazonalidade
   ❌ Falta: Portfolio trends, Cross-project patterns
```

#### ✅ Módulos de Suporte
```
✅ visualization.py            - Gráficos Matplotlib
✅ cost_pert_beta.py          - Análise de custos PERT
✅ demand_forecasting.py       - Forecast de demanda
```

---

### 🗄️ MODELOS DE DADOS (SQLAlchemy)

#### ✅ Tabelas Existentes

```sql
-- USER (auth + multi-tenancy)
users
├── id
├── email, password_hash, name
├── role (student, instructor, admin)
├── is_active
├── created_at, updated_at, last_login
└── access_expires_at

-- PROJECT (bem estruturado para portfólio!)
projects
├── id, user_id
├── name, description, team_size
├── status (active, on_hold, completed, cancelled)
├── priority (1-5)
├── business_value (0-100) ✅
├── risk_level (low, medium, high, critical) ✅
├── capacity_allocated (FTE) ✅
├── strategic_importance ✅
├── start_date, target_end_date
├── owner, stakeholder
├── tags (JSON)
└── created_at, updated_at

-- FORECAST (linked to project)
forecasts
├── id, user_id, project_id ✅
├── name, description
├── forecast_type (deadline, throughput, cost)
├── forecast_data (JSON blob)
├── input_data (JSON blob)
├── backlog, deadline_date, start_date
├── projected_weeks_p85
├── can_meet_deadline
├── scope_completion_pct
├── version, parent_forecast_id
└── created_at

-- ACTUAL (for validation)
actuals
├── id, forecast_id
├── actual_completion_date
├── actual_weeks_taken
├── actual_items_completed
├── actual_scope_delivered_pct
├── weeks_error, weeks_error_pct
└── recorded_at
```

#### ❌ Tabelas FALTANDO (para portfólio completo)

```sql
-- PORTFOLIO (agrupamento de projetos)
portfolios
├── id, user_id
├── name, description
├── status (planning, active, completed)
├── total_budget
├── total_capacity (FTE)
├── start_date, end_date
├── strategic_objectives (JSON)
└── created_at, updated_at

-- PORTFOLIO_PROJECT (relacionamento N:N)
portfolio_projects
├── portfolio_id
├── project_id
├── allocation_pct (% do projeto alocado a este portfolio)
├── priority_in_portfolio
└── added_at

-- SIMULATION_RUN (guardar simulações de portfólio)
simulation_runs
├── id, portfolio_id, user_id
├── simulation_type (monte_carlo, what_if, optimization)
├── configuration (JSON: n_simulations, confidence_level, etc.)
├── results (JSON: aggregated metrics)
├── individual_project_results (JSON)
├── created_at
└── runtime_seconds

-- COD_ESTIMATION (guardar estimativas de CoD)
cod_estimations
├── id, project_id
├── weekly_cod (R$/week)
├── total_expected_cod (R$)
├── estimation_method (ml, manual, expert)
├── factors (JSON: stakeholders, complexity, etc.)
├── created_at
└── updated_at

-- RISK_REGISTER (portfolio-level risks)
portfolio_risks
├── id, portfolio_id, project_id (nullable)
├── risk_description
├── probability (0-1)
├── impact_weeks
├── impact_cost
├── mitigation_plan
├── status (identified, mitigating, resolved)
└── created_at, updated_at
```

---

### 🌐 API ENDPOINTS (app.py)

#### ✅ Endpoints Existentes

```python
# AUTHENTICATION
POST   /register
POST   /login
GET    /logout

# FORECASTING (Item-level)
POST   /api/simulate                # Monte Carlo tradicional
POST   /api/ml-forecast             # ML forecasting
POST   /api/mc-throughput           # MC throughput
POST   /api/combined-forecast       # ML + MC combined
POST   /api/backtest                # Backtesting (fold_stride) ✨ NEW

# DEADLINE ANALYSIS (Item-level)
GET    /deadline-analysis
POST   /api/deadline-analysis
POST   /api/forecast-how-many
POST   /api/forecast-when

# FORECAST VS ACTUAL (Validation)
GET    /forecast-vs-actual
GET    /api/forecast-vs-actual/dashboard
POST   /api/actuals
GET    /api/actuals
DELETE /api/actuals/<id>

# PORTFOLIO (Parcial)
GET    /api/portfolio/dashboard      # Dashboard básico
GET    /api/portfolio/capacity       # Análise de capacidade
GET    /api/portfolio/prioritization # Matriz de priorização

# COST OF DELAY (Individual)
GET    /api/cod/forecaster           # Get CoD forecaster
POST   /api/cod/predict              # Predict CoD
POST   /api/cod/total                # Calculate total CoD
GET    /api/cod/feature-importance   # Feature importance
GET    /api/cod/model-info           # Model info
```

#### ❌ Endpoints FALTANDO (para portfólio integrado)

```python
# PORTFOLIO MANAGEMENT
POST   /api/portfolio                    # Create portfolio
GET    /api/portfolio/<id>               # Get portfolio details
PUT    /api/portfolio/<id>               # Update portfolio
DELETE /api/portfolio/<id>               # Delete portfolio
POST   /api/portfolio/<id>/projects      # Add projects to portfolio
DELETE /api/portfolio/<id>/projects/<pid># Remove project from portfolio

# PORTFOLIO SIMULATIONS
POST   /api/portfolio/<id>/simulate      # Run Monte Carlo for entire portfolio
POST   /api/portfolio/<id>/simulate-cod  # CoD analysis for portfolio
POST   /api/portfolio/<id>/optimize      # Optimize portfolio (WSJF, value/risk)
POST   /api/portfolio/<id>/what-if       # What-if analysis
GET    /api/portfolio/<id>/simulations   # List past simulations
GET    /api/simulation/<id>              # Get simulation details

# PORTFOLIO RISKS
GET    /api/portfolio/<id>/risks         # Get portfolio risks
POST   /api/portfolio/<id>/risks         # Add risk
PUT    /api/risk/<id>                    # Update risk
DELETE /api/risk/<id>                    # Delete risk
POST   /api/portfolio/<id>/risk-rollup   # Aggregate project risks

# PORTFOLIO DASHBOARD
GET    /api/portfolio/<id>/dashboard-data # Integrated dashboard data
GET    /api/portfolio/<id>/trends        # Portfolio trends over time
GET    /api/portfolio/<id>/health        # Portfolio health metrics
GET    /api/portfolio/<id>/cod-summary   # CoD summary
GET    /api/portfolio/<id>/timeline      # Portfolio timeline/roadmap

# CROSS-PROJECT ANALYSIS
POST   /api/portfolio/<id>/dependencies  # Analyze cross-project dependencies
GET    /api/portfolio/<id>/critical-path # Portfolio critical path
POST   /api/portfolio/<id>/resource-conflicts # Identify resource conflicts
```

---

### 🎨 INTERFACE (Templates + JavaScript)

#### ✅ Páginas Existentes

```
templates/
├── index.html                    # Main page com abas
│   ├── Monte Carlo ✅
│   ├── Machine Learning ✅
│   ├── Combined Analysis ✅
│   ├── Cost of Delay ✅
│   ├── Historical Analysis ✅
│   ├── Cost Analysis ✅
│   ├── Trend Analysis ✅
│   ├── Forecast vs Actual ✅
│   ├── Dependency Analysis ✅
│   ├── Executive Dashboard 🟡 (básico)
│   └── Portfolio Dashboard 🟡 (básico)
│
├── backtesting.html ✨ NEW       # Backtesting com fold_stride
├── forecast_vs_actual.html       # Forecast vs Actual standalone
├── deadline_analysis.html        # Deadline analysis
├── dependency_analysis.html      # Dependency analysis
├── documentacao.html             # Documentation
└── auth/*.html                   # Login/Register

static/js/
├── ui.js                         # Main UI logic
├── charts.js                     # Chart.js integration
├── advanced_forecast.js          # ML forecast UI
├── cost_analysis.js              # Cost analysis
├── cost_of_delay.js              # CoD UI (individual)
├── dashboard.js                  # Executive dashboard (básico)
├── portfolio.js                  # Portfolio dashboard (básico)
├── trend_insights.js             # Trend analysis
├── forecast-vs-actual.js         # Forecast vs actual
├── forecast-persistence.js       # Save/load forecasts
└── i18n.js                       # Internationalization
```

#### ❌ Páginas FALTANDO

```
templates/
├── portfolio_manager.html        # CRUD de portfólios
├── portfolio_simulation.html     # Simulações de portfólio
├── portfolio_optimization.html   # Otimização WSJF
├── portfolio_risks.html          # Gerenciamento de riscos
└── portfolio_timeline.html       # Timeline/roadmap visual

static/js/
├── portfolio_manager.js          # Portfolio CRUD
├── portfolio_simulation.js       # Portfolio simulations
├── portfolio_optimization.js     # WSJF optimization
├── portfolio_risks.js            # Risk management
└── portfolio_charts.js           # Portfolio-specific charts
```

---

## 🔍 ANÁLISE FUNCIONAL POR NÍVEL

### NÍVEL 1: ITENS (Work Items) ✅ BEM IMPLEMENTADO

**Status**: 95% completo

#### ✅ Funcionalidades Existentes
- Monte Carlo simulation (throughput, deadline)
- Machine Learning forecasting (9 modelos)
- Combined ML + MC
- Backtesting com fold_stride ✨
- Deadline analysis (can we meet? how many items?)
- Cost analysis (PERT/Beta)
- Trend detection
- Dependency analysis
- Forecast vs Actual tracking
- Accuracy metrics (MAPE, RMSE, R², MAE)

#### 🟡 Melhorias Sugeridas
- Process Behavior Charts (SPC)
- Auto-tuning de parâmetros
- Forecast explainability (SHAP values)

---

### NÍVEL 2: PROJETOS (Projects) 🟡 PARCIALMENTE IMPLEMENTADO

**Status**: 60% completo

#### ✅ O Que Existe
```python
# models.py - Project model (bem estruturado!)
Project:
  - name, description, team_size
  - status, priority, business_value
  - risk_level, capacity_allocated
  - strategic_importance
  - start_date, target_end_date
  - owner, stakeholder, tags

# Relacionamentos
Project → Forecasts (1:N)
Forecast → Actuals (1:N)
```

#### ✅ Funcionalidades Existentes
- CRUD de projetos (via API)
- Salvar forecasts por projeto
- Comparar forecast vs actual
- Project health score (portfolio_analyzer.py)

#### ❌ O Que FALTA
```
❌ Interface visual para gerenciar projetos (CRUD UI)
❌ Timeline do projeto (burn-up/burn-down)
❌ Project dashboard consolidado
❌ Histórico de forecasts do projeto (timeline chart)
❌ Análise de variação (forecast vs plan vs actual)
❌ Project cost tracking (budget vs spend)
❌ Resource allocation tracking
❌ Risk register por projeto
❌ Milestone tracking
❌ Project comparison (comparar múltiplos projetos)
```

---

### NÍVEL 3: PORTFÓLIO 🔴 POUCO IMPLEMENTADO

**Status**: 30% completo

#### ✅ O Que Existe
```python
# portfolio_analyzer.py (parcial)
✅ ProjectHealthScore:
   - overall_score, forecast_accuracy_score
   - delivery_performance_score
   - capacity_health_score, risk_score
   - mape, bias, health_status, alerts

✅ CapacityAnalysis:
   - total_capacity, allocated_capacity, available_capacity
   - utilization_rate
   - over_allocated_projects, under_allocated_projects

✅ PrioritizationMatrix:
   - high_value_low_risk (Quick wins)
   - high_value_high_risk (Strategic bets)
   - low_value_low_risk (Fill-ins)
   - low_value_high_risk (Money pits)

# Endpoints existentes
GET /api/portfolio/dashboard
GET /api/portfolio/capacity
GET /api/portfolio/prioritization
```

#### ❌ O Que FALTA (CRÍTICO!)

```
🔴 MODELO DE DADOS:
   ❌ Tabela Portfolio (para agrupar projetos)
   ❌ Tabela PortfolioProject (relacionamento N:N)
   ❌ Tabela SimulationRun (guardar simulações)
   ❌ Tabela CoDEstimation (estimativas de CoD)
   ❌ Tabela PortfolioRisks (riscos agregados)

🔴 SIMULAÇÕES DE PORTFÓLIO:
   ❌ Monte Carlo agregado (todos os projetos juntos)
   ❌ Análise de dependências entre projetos
   ❌ Simulação de cenários (what-if)
   ❌ Análise de impacto de atrasos em cascata
   ❌ Resource conflict detection
   ❌ Portfolio capacity planning

🔴 COST OF DELAY DE PORTFÓLIO:
   ❌ CoD agregado (somatório de todos os projetos)
   ❌ WSJF (Weighted Shortest Job First) optimization
   ❌ Priorização dinâmica baseada em CoD
   ❌ Análise de oportunidade perdida
   ❌ Trade-off analysis (custo vs delay)
   ❌ Portfolio CoD dashboard

🔴 ANÁLISE DE RISCOS:
   ❌ Portfolio risk rollup (agregação de riscos)
   ❌ Correlação entre riscos
   ❌ Impact analysis (se projeto X atrasar, qual impacto?)
   ❌ Risk mitigation planning
   ❌ Portfolio risk heatmap
   ❌ Probabilistic roadmap

🔴 DASHBOARD EXECUTIVO:
   ❌ Visão consolidada de todos os projetos
   ❌ KPIs de portfólio (valor total, risco total, health score)
   ❌ Timeline integrado (Gantt probabilístico)
   ❌ Burn-up/burn-down de portfólio
   ❌ Resource utilization heatmap
   ❌ Portfolio health trends
   ❌ Alertas e recomendações

🔴 OTIMIZAÇÃO:
   ❌ Otimização de alocação de recursos
   ❌ Maximizar valor vs minimizar risco
   ❌ Solver de programação linear (PuLP)
   ❌ Recomendações de repriorização
   ❌ Scenario comparison

🔴 INTERFACE:
   ❌ Portfolio manager (CRUD de portfólios)
   ❌ Portfolio simulation page
   ❌ Portfolio optimization page
   ❌ Portfolio risks page
   ❌ Portfolio timeline/roadmap
   ❌ Drag-and-drop prioritization
```

---

## 📊 MATRIZ DE FUNCIONALIDADES

### Visão Integrada: O Que Funciona Hoje

| Funcionalidade | Itens | Projetos | Portfólio |
|----------------|-------|----------|-----------|
| Monte Carlo | ✅ 100% | 🟡 50% | ❌ 0% |
| Machine Learning | ✅ 100% | 🟡 50% | ❌ 0% |
| Backtesting | ✅ 100% | ❌ 0% | ❌ 0% |
| Forecast vs Actual | ✅ 100% | 🟡 50% | ❌ 0% |
| Cost of Delay | ✅ 80% | 🟡 40% | ❌ 10% |
| Risk Analysis | ✅ 70% | 🟡 30% | ❌ 5% |
| Dependency Analysis | ✅ 90% | 🟡 40% | ❌ 10% |
| Capacity Planning | 🟡 50% | 🟡 60% | 🟡 40% |
| Dashboard | ✅ 95% | 🟡 30% | 🟡 20% |
| Timeline/Roadmap | ✅ 80% | 🟡 20% | ❌ 0% |
| Optimization | ❌ 0% | ❌ 0% | ❌ 0% |
| What-If Analysis | 🟡 60% | ❌ 0% | ❌ 0% |

**Legenda**: ✅ Implementado | 🟡 Parcial | ❌ Não implementado

---

## 🎯 GAPS CRÍTICOS IDENTIFICADOS

### GAP 1: MODELO DE DADOS 🔴 CRÍTICO
**Impacto**: Alto
**Esforço**: Médio (2-3 semanas)

**Problema**: Não existe tabela `Portfolio` para agrupar projetos.

**Solução**:
```sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    total_budget FLOAT,
    total_capacity FLOAT,
    status VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE portfolio_projects (
    portfolio_id INTEGER REFERENCES portfolios(id),
    project_id INTEGER REFERENCES projects(id),
    allocation_pct FLOAT DEFAULT 100.0,
    priority_in_portfolio INTEGER,
    PRIMARY KEY (portfolio_id, project_id)
);
```

---

### GAP 2: SIMULAÇÕES DE PORTFÓLIO 🔴 CRÍTICO
**Impacto**: Alto
**Esforço**: Alto (3-4 semanas)

**Problema**: Não é possível simular um portfólio inteiro de projetos.

**Solução Necessária**:
```python
# portfolio_simulator.py (NOVO)
class PortfolioSimulator:
    def simulate_portfolio(
        self,
        portfolio_id: int,
        n_simulations: int = 10000
    ) -> PortfolioSimulationResult:
        """
        Run Monte Carlo for all projects in portfolio.
        Returns aggregated metrics:
        - Total duration (considering dependencies)
        - Total cost
        - Risk-adjusted timeline
        - Resource conflicts
        - Portfolio completion probability
        """
        pass

    def simulate_cod_portfolio(
        self,
        portfolio_id: int
    ) -> PortfolioCoDResult:
        """
        Calculate total Cost of Delay for portfolio.
        Includes:
        - WSJF scores for each project
        - Recommended prioritization
        - Total opportunity cost
        - Delay impact analysis
        """
        pass
```

---

### GAP 3: DASHBOARD INTEGRADO 🔴 CRÍTICO
**Impacto**: Alto
**Esforço**: Médio (2 semanas)

**Problema**: Dashboard executivo é muito básico, não mostra visão integrada.

**Solução**:
```javascript
// portfolio_integrated_dashboard.js (NOVO)
// Deve mostrar:
- KPIs consolidados (valor total, risco, health score)
- Timeline Gantt com probabilidades
- Resource utilization heatmap
- CoD portfolio summary
- Critical path analysis
- Alertas e recomendações
```

---

### GAP 4: COST OF DELAY DE PORTFÓLIO 🔴 CRÍTICO
**Impacto**: Muito Alto
**Esforço**: Médio (2 semanas)

**Problema**: CoD existe apenas para projetos individuais.

**Solução**:
```python
# cod_portfolio_analyzer.py (NOVO)
class CoDPortfolioAnalyzer:
    def calculate_wsjf_scores(self, portfolio_id: int):
        """WSJF = (Business Value + Time Criticality) / Duration"""
        pass

    def optimize_portfolio_sequence(self, portfolio_id: int):
        """Optimize project sequence to minimize total CoD"""
        pass

    def calculate_total_cod(self, portfolio_id: int):
        """Sum CoD of all projects, considering dependencies"""
        pass

    def delay_impact_analysis(self, project_id: int, delay_weeks: int):
        """Analyze cascading impact of delaying one project"""
        pass
```

---

### GAP 5: OTIMIZAÇÃO DE PORTFÓLIO ❌ NÃO EXISTE
**Impacto**: Alto
**Esforço**: Alto (3-4 semanas)

**Problema**: Não existe otimização matemática de portfólio.

**Solução**:
```python
# portfolio_optimizer.py (NOVO)
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

class PortfolioOptimizer:
    def optimize_value_vs_risk(
        self,
        portfolio_id: int,
        budget_constraint: float,
        capacity_constraint: float
    ):
        """
        Linear Programming to maximize:
        - Total business value
        Subject to:
        - Budget constraint
        - Capacity constraint
        - Strategic balance (diversification)
        """
        pass

    def optimize_cod_sequence(self, portfolio_id: int):
        """Optimize sequence to minimize total CoD"""
        pass
```

---

## 🗺️ ROADMAP DE IMPLEMENTAÇÃO

### FASE 1: Base de Portfólio (2-3 semanas) 🔴 URGENTE
```
✅ Semana 1: Modelo de Dados
   - Criar tabelas: Portfolio, PortfolioProject, SimulationRun
   - Migração de banco de dados
   - CRUD de Portfolio (API)
   - Testes

✅ Semana 2: Interface de Portfólio
   - portfolio_manager.html (CRUD UI)
   - portfolio_manager.js
   - Adicionar projetos ao portfólio (drag-and-drop)
   - Visualização de projetos do portfólio

✅ Semana 3: Simulações Básicas
   - PortfolioSimulator class
   - Endpoint /api/portfolio/<id>/simulate
   - Agregação de métricas
   - Visualização de resultados
```

### FASE 2: Cost of Delay de Portfólio (2 semanas) 🔥
```
✅ Semana 1: CoD Backend
   - cod_portfolio_analyzer.py
   - WSJF calculation
   - Endpoint /api/portfolio/<id>/cod-summary
   - Otimização de sequência

✅ Semana 2: CoD UI
   - Portfolio CoD dashboard
   - WSJF matrix visualization
   - Recomendações de priorização
   - What-if: "E se adiarmos projeto X?"
```

### FASE 3: Dashboard Integrado (2 semanas) 📊
```
✅ Semana 1: Backend Dashboard
   - Endpoint /api/portfolio/<id>/dashboard-data
   - Agregação de métricas
   - Trends over time
   - Health scores consolidados

✅ Semana 2: UI Dashboard
   - portfolio_dashboard_v2.html
   - KPIs consolidados
   - Timeline Gantt probabilístico
   - Resource heatmap
   - Alertas inteligentes
```

### FASE 4: Riscos de Portfólio (2 semanas) ⚠️
```
✅ Semana 1: Risk Backend
   - Tabela portfolio_risks
   - Risk rollup algorithm
   - Correlation analysis
   - Impact analysis

✅ Semana 2: Risk UI
   - portfolio_risks.html
   - Risk heatmap
   - Mitigation planning
   - Risk register
```

### FASE 5: Otimização (2-3 semanas) 🎯
```
✅ Semana 1-2: Optimization Backend
   - portfolio_optimizer.py
   - PuLP integration
   - Value vs Risk optimization
   - CoD sequence optimization

✅ Semana 3: Optimization UI
   - portfolio_optimization.html
   - Interactive constraints
   - Scenario comparison
   - Recommendations
```

### FASE 6: Integração Final (1-2 semanas) 🔗
```
✅ Integrar todas as visões
✅ Menu de navegação unificado
✅ Breadcrumbs: Portfolio → Project → Item
✅ Drill-down from portfolio to items
✅ Roll-up from items to portfolio
✅ Export completo (PDF, Excel)
✅ Testes de integração
✅ Documentação
```

---

## 🎨 PROPOSTA DE UI INTEGRADA

### Menu de Navegação Sugerido

```
┌─────────────────────────────────────────────────────────────┐
│ Flow Forecaster                                             │
├─────────────────────────────────────────────────────────────┤
│ 🏠 Home   |   📊 Portfólio   |   📁 Projetos   |   📋 Itens │
└─────────────────────────────────────────────────────────────┘

📊 PORTFÓLIO
├── 📈 Dashboard Executivo (overview de tudo)
├── 💼 Gerenciar Portfólios (CRUD)
├── 🎲 Simulações de Portfólio
│   ├── Monte Carlo Agregado
│   ├── Análise de Cenários (What-If)
│   └── Resource Conflict Detection
├── 💰 Cost of Delay
│   ├── WSJF Matrix
│   ├── Otimização de Sequência
│   └── Trade-off Analysis
├── ⚠️ Riscos
│   ├── Risk Register
│   ├── Risk Rollup
│   └── Impact Analysis
├── 🎯 Otimização
│   ├── Maximizar Valor
│   ├── Minimizar Risco
│   └── Recomendações
└── 📅 Timeline/Roadmap
    ├── Gantt Probabilístico
    └── Critical Path

📁 PROJETOS
├── 📋 Lista de Projetos
├── ➕ Criar Projeto
├── 🔍 Detalhes do Projeto
│   ├── Overview
│   ├── Forecasts (histórico)
│   ├── Timeline
│   ├── Riscos
│   └── Team & Resources
└── 📊 Comparar Projetos

📋 ITENS (já existe!)
├── 🎲 Monte Carlo
├── 🤖 Machine Learning
├── ⚖️ Combined Analysis
├── 🧪 Backtesting
├── 💰 Cost Analysis
├── 📈 Trend Analysis
└── ✅ Forecast vs Actual
```

---

## 📦 ARQUIVOS NOVOS A CRIAR

### Backend (Python)
```
✨ portfolio_simulator.py         # Simulações de portfólio
✨ cod_portfolio_analyzer.py      # CoD de portfólio
✨ portfolio_optimizer.py         # Otimização (PuLP)
✨ portfolio_risk_analyzer.py     # Análise de riscos agregados
✨ timeline_generator.py          # Gantt probabilístico
✨ resource_analyzer.py           # Resource conflicts
```

### Frontend (Templates)
```
✨ templates/portfolio_manager.html       # CRUD portfólios
✨ templates/portfolio_simulation.html    # Simulações
✨ templates/portfolio_cod.html           # CoD de portfólio
✨ templates/portfolio_risks.html         # Gestão de riscos
✨ templates/portfolio_optimization.html  # Otimização
✨ templates/portfolio_timeline.html      # Timeline/roadmap
✨ templates/project_detail.html          # Detalhes do projeto
✨ templates/project_comparison.html      # Comparação de projetos
```

### Frontend (JavaScript)
```
✨ static/js/portfolio_manager.js
✨ static/js/portfolio_simulation.js
✨ static/js/portfolio_cod.js
✨ static/js/portfolio_risks.js
✨ static/js/portfolio_optimizer.js
✨ static/js/portfolio_charts.js          # Gráficos específicos
✨ static/js/timeline_gantt.js            # Gantt chart
✨ static/js/resource_heatmap.js          # Heatmap de recursos
```

---

## 🔢 ESTIMATIVAS

### Esforço Total
```
FASE 1: Base de Portfólio         = 2-3 semanas
FASE 2: CoD de Portfólio          = 2 semanas
FASE 3: Dashboard Integrado       = 2 semanas
FASE 4: Riscos de Portfólio       = 2 semanas
FASE 5: Otimização               = 2-3 semanas
FASE 6: Integração Final         = 1-2 semanas
─────────────────────────────────────────────
TOTAL: 11-14 semanas (~3 meses)
```

### Complexidade por Fase
```
FASE 1: 🟡 Média  (DB + CRUD)
FASE 2: 🟡 Média  (CoD + WSJF)
FASE 3: 🟢 Baixa  (Dashboard)
FASE 4: 🟡 Média  (Risk analysis)
FASE 5: 🔴 Alta   (Optimization)
FASE 6: 🟢 Baixa  (Integration)
```

---

## 📊 PRIORIZAÇÃO (Valor vs Esforço)

| Fase | Valor | Esforço | Prioridade | Ordem |
|------|-------|---------|------------|-------|
| FASE 1: Base | ⭐⭐⭐⭐⭐ | 🟡 Médio | **CRÍTICO** | #1 |
| FASE 2: CoD | ⭐⭐⭐⭐⭐ | 🟡 Médio | **ALTO** | #2 |
| FASE 3: Dashboard | ⭐⭐⭐⭐ | 🟢 Baixo | **ALTO** | #3 |
| FASE 4: Riscos | ⭐⭐⭐⭐ | 🟡 Médio | **MÉDIO** | #4 |
| FASE 5: Otimização | ⭐⭐⭐⭐⭐ | 🔴 Alto | **MÉDIO** | #5 |
| FASE 6: Integração | ⭐⭐⭐ | 🟢 Baixo | **BAIXO** | #6 |

---

## ✅ PRÓXIMOS PASSOS IMEDIATOS

### Sprint 1 (Semana 1): Modelo de Dados
1. ✅ Criar migrations para tabelas Portfolio
2. ✅ Adicionar models no models.py
3. ✅ API endpoints CRUD (/api/portfolio)
4. ✅ Testes unitários

### Sprint 2 (Semana 2): UI de Portfólio
1. ✅ portfolio_manager.html
2. ✅ portfolio_manager.js
3. ✅ Drag-and-drop de projetos
4. ✅ Visualização básica

### Sprint 3 (Semana 3): Simulações Básicas
1. ✅ portfolio_simulator.py
2. ✅ Endpoint /api/portfolio/<id>/simulate
3. ✅ Agregação de métricas
4. ✅ UI de resultados

---

**FIM DO INVENTÁRIO**

**Versão**: 1.0
**Data**: 2025-11-06
**Autor**: Claude Code
