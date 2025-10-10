# Guia de Análise de Deadline e Forecast

## 📋 Visão Geral

Este projeto agora inclui funcionalidades completas de análise de deadline e forecast usando **dois métodos complementares**:

1. **Monte Carlo** - Simulação baseada em distribuição de Weibull
2. **Machine Learning** - Previsão baseada em modelos Random Forest, XGBoost e HistGradient Boosting

Ambos os métodos suportam **parâmetros completos de projeto**:
- ✅ Tamanho de equipe (team_size)
- ✅ Contribuidores mínimo/máximo (min_contributors, max_contributors)
- ✅ Curva S de produtividade (s_curve_size)
- ✅ Lead times (lt_samples)
- ✅ Split rates (split_rate_samples)
- ✅ Riscos (apenas Monte Carlo)

---

## 🎯 Três Perguntas Fundamentais

### 1. **"Posso cumprir o deadline?"**
Análise se um deadline pode ser cumprido dado o throughput histórico e backlog.

### 2. **"Quantos items posso entregar no período?"**
Previsão de quantos items serão completados em um período de tempo.

### 3. **"Quando vou terminar o backlog?"**
Previsão de quando um backlog específico será concluído.

---

## 🔧 Funções Disponíveis

### Monte Carlo

```python
from monte_carlo_unified import (
    analyze_deadline,
    forecast_how_many,
    forecast_when
)
```

#### `analyze_deadline()`
```python
result = analyze_deadline(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    backlog=20,
    deadline_date="16/10/2025",
    start_date="01/10/2025",
    n_simulations=10000
)

# Retorna:
# - weeks_to_deadline: Semanas até o deadline
# - projected_weeks_p85: Semanas necessárias (85% confiança)
# - projected_work_p85: Trabalho que pode ser entregue
# - can_meet_deadline: Boolean - pode cumprir?
# - scope_completion_pct: % do escopo que será completado
# - deadline_completion_pct: % do prazo que será usado
```

#### `forecast_how_many()`
```python
result = forecast_how_many(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    start_date="01/10/2025",
    end_date="16/10/2025",
    n_simulations=10000
)

# Retorna:
# - days, weeks: Período
# - items_p95, items_p85, items_p50: Items em diferentes confiânças
# - items_mean: Média de items
```

#### `forecast_when()`
```python
result = forecast_when(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    backlog=20,
    start_date="01/10/2025",
    n_simulations=10000
)

# Retorna:
# - date_p95, date_p85, date_p50: Datas de conclusão
# - weeks_p95, weeks_p85, weeks_p50: Semanas necessárias
```

---

### Machine Learning

```python
from ml_deadline_forecaster import (
    ml_analyze_deadline,
    ml_forecast_how_many,
    ml_forecast_when
)
```

#### `ml_analyze_deadline()`
```python
result = ml_analyze_deadline(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    backlog=20,
    deadline_date="16/10/2025",
    start_date="01/10/2025",
    team_size=10,               # ← Novo!
    min_contributors=2,          # ← Novo!
    max_contributors=5,          # ← Novo!
    s_curve_size=20,            # ← Novo!
    lt_samples=[1, 2, 3, 2],    # ← Novo!
    split_rate_samples=[1.0, 1.1, 1.2],  # ← Novo!
    n_simulations=1000
)

# Retorna os mesmos campos do Monte Carlo +
# - projected_effort_p85: Esforço em person-weeks
# - ml_models: Lista de modelos ML e suas métricas
# - forecast_method: "Machine Learning + Team Dynamics"
```

#### `ml_forecast_how_many()`
```python
result = ml_forecast_how_many(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    start_date="01/10/2025",
    end_date="16/10/2025",
    team_size=10,
    min_contributors=2,
    max_contributors=5,
    s_curve_size=20,
    n_simulations=1000
)
```

#### `ml_forecast_when()`
```python
result = ml_forecast_when(
    tp_samples=[4, 5, 6, 7, 5, 6, 7, 8],
    backlog=20,
    start_date="01/10/2025",
    team_size=10,
    min_contributors=2,
    max_contributors=5,
    s_curve_size=20,
    lt_samples=[1, 2, 3, 2],
    split_rate_samples=[1.0, 1.1],
    n_simulations=1000
)
```

---

## 📊 Parâmetros de Equipe e Projeto

### Team Size (Tamanho da Equipe)
```python
team_size=10  # Total de pessoas no time
```

### Contributors (Contribuidores Ativos)
```python
min_contributors=2  # Mínimo de pessoas trabalhando ativamente
max_contributors=5  # Máximo de pessoas trabalhando ativamente
```

### S-Curve (Curva de Produtividade)
```python
s_curve_size=20  # Percentual de ramp-up/down (0-50%)
```

**Como funciona:**
- Primeiros 20% do projeto: Ramp-up (2 → 5 pessoas)
- Meio 60% do projeto: Full capacity (5 pessoas)
- Últimos 20% do projeto: Ramp-down (5 → 2 pessoas)

### Lead Times
```python
lt_samples=[1, 2, 3, 2, 1, 2, 3, 2]  # Em dias
```
Tempo de espera/overhead por task.

### Split Rates
```python
split_rate_samples=[1.0, 1.1, 1.2, 1.0, 1.1]  # Multiplicadores de escopo
```
Modelagem de scope creep ou redução.

---

## 🎯 Exemplos Práticos

### Exemplo 1: Análise Simples (Sem Dinâmica de Equipe)

```python
from monte_carlo_unified import analyze_deadline

result = analyze_deadline(
    tp_samples=[5, 6, 7, 4, 8, 6, 5, 7],
    backlog=20,
    deadline_date="16/10/2025",
    start_date="01/10/2025",
    n_simulations=10000
)

print(f"Pode cumprir? {result['can_meet_deadline']}")
print(f"% escopo: {result['scope_completion_pct']}%")
```

### Exemplo 2: Projeto Completo com S-Curve

```python
from ml_deadline_forecaster import ml_analyze_deadline

result = ml_analyze_deadline(
    tp_samples=[3, 5, 4, 6, 5, 7, 4, 5, 6, 5],
    backlog=50,
    deadline_date="20/12/2025",
    start_date="01/11/2025",
    team_size=10,
    min_contributors=2,
    max_contributors=5,
    s_curve_size=20,
    lt_samples=[1, 2, 3, 2, 1, 2],
    split_rate_samples=[1.0, 1.1, 1.2],
    n_simulations=1000
)

print(f"Deadline: {result['deadline_date']}")
print(f"Semanas necessárias (P85): {result['projected_weeks_p85']}")
print(f"Esforço (P85): {result['projected_effort_p85']} person-weeks")
print(f"Pode cumprir? {result['can_meet_deadline']}")
print(f"% escopo: {result['scope_completion_pct']}%")

# Modelos ML
for model in result['ml_models']:
    print(f"{model['model']}: MAE = {model['mae']}")
```

### Exemplo 3: Comparação ML vs Monte Carlo

```python
from monte_carlo_unified import analyze_deadline as mc_deadline
from ml_deadline_forecaster import ml_analyze_deadline

tp_samples = [4, 5, 6, 7, 5, 6, 7, 8]
backlog = 20
deadline = "01/11/2025"
start = "01/10/2025"

# Monte Carlo
mc_result = mc_deadline(
    tp_samples=tp_samples,
    backlog=backlog,
    deadline_date=deadline,
    start_date=start,
    n_simulations=10000
)

# Machine Learning
ml_result = ml_analyze_deadline(
    tp_samples=tp_samples,
    backlog=backlog,
    deadline_date=deadline,
    start_date=start,
    n_simulations=1000
)

print("Monte Carlo vs Machine Learning:")
print(f"  MC P85: {mc_result['projected_weeks_p85']} semanas")
print(f"  ML P85: {ml_result['projected_weeks_p85']} semanas")
print(f"  Diferença: {abs(mc_result['projected_weeks_p85'] - ml_result['projected_weeks_p85'])} semanas")
```

---

## 📈 Quando Usar Cada Método?

### Use **Monte Carlo** quando:
- ✅ Quer análise probabilística pura
- ✅ Dados históricos são estáveis
- ✅ Quer resultados rápidos (10K+ simulações)
- ✅ Precisa incluir riscos específicos
- ✅ Prefere distribuição de Weibull

### Use **Machine Learning** quando:
- ✅ Há tendências nos dados históricos
- ✅ Quer capturar padrões de sazonalidade
- ✅ Deseja múltiplas perspectivas (ensemble de modelos)
- ✅ Prefere previsões baseadas em aprendizado
- ✅ Tem 8+ semanas de dados históricos

### Use **Ambos** quando:
- ✅ Quer validar resultados (consenso)
- ✅ Precisa de análise robusta para stakeholders
- ✅ Quer cobrir diferentes cenários de incerteza

---

## 🧪 Como Testar

### Teste Monte Carlo
```bash
python test_deadline_forecasts.py
python example_deadline_analysis.py
```

### Teste Machine Learning
```bash
python test_ml_deadline.py
```

### Comparação
Ambos os scripts incluem comparações lado a lado.

---

## 📊 Formato de Saída

### Análise de Deadline (Exemplo)

```
RESULTADOS DA SIMULAÇÃO
────────────────────────────────────────────────────────────────────────────────
DEAD LINE                                    16/10/25
Semanas para Dead Line                       2.1
Semanas Projetadas (P85)                     4.0

Trabalho a ser entregue (projetado) (P85)    21

Tem chance de cumprir o Dead Line?           Não

% que será cumprido do escopo                100%

% do prazo que será cumprido                 54%
```

### Forecast "Quantos?" (Exemplo)

```
RESPOSTAS BASEADAS NO THROUGHPUT
────────────────────────────────────────────────────────────────────────────────
INÍCIO                           01/10/2025
FIM                              16/10/2025
DIAS                             15
SEMANAS                          3

95% DE CONFIANÇA                 21
85% DE CONFIANÇA                 20
50% DE CONFIANÇA                 18
```

### Forecast "Quando?" (Exemplo)

```
PREVISÃO DE CONCLUSÃO
────────────────────────────────────────────────────────────────────────────────
BACKLOG                          20
INÍCIO                           01/10/25

95% de confiança                 05/11/25
85% de confiança                 29/10/25
50% de confiança                 29/10/25
```

---

## 🔍 Interpretação de Resultados

### Percentis de Confiança

| Percentil | Significado | Uso Recomendado |
|-----------|-------------|-----------------|
| **P50** | 50% de chance de terminar antes | Cenário otimista |
| **P85** | 85% de confiança | **Recomendado para commitments** |
| **P95** | 95% de confiança | Cenário conservador |

### Scope Completion %

- **100%**: Todo o escopo será entregue
- **60%**: Apenas 60% do escopo será entregue no deadline
- Valores < 100% indicam risco de não cumprir todo o escopo

### Deadline Completion %

- **100%**: Usará 100% do tempo disponível
- **54%**: Precisa de quase o dobro do tempo disponível
- Valores < 100% indicam deadline muito apertado

---

## 🚀 Performance

### Monte Carlo
- **Simple mode**: ~81,000 simulações/segundo
- **Complete mode**: ~42,000 simulações/segundo
- **Recomendado**: 10,000 simulações para análises

### Machine Learning
- **Treinamento**: ~0.1-0.5 segundos (uma vez)
- **Simulação**: ~1,000 iterações suficientes
- **Modelos**: 4-5 modelos em ensemble

---

## 📚 Arquivos de Referência

### Monte Carlo
- `monte_carlo_unified.py` - Funções principais
- `test_deadline_forecasts.py` - Testes
- `example_deadline_analysis.py` - Exemplos práticos

### Machine Learning
- `ml_deadline_forecaster.py` - Funções ML
- `ml_forecaster.py` - Base dos modelos ML
- `test_ml_deadline.py` - Testes ML

### Documentação
- `DEADLINE_FORECAST_GUIDE.md` - Este guia
- `WEIBULL_UNIFICATION.md` - Detalhes da distribuição de Weibull
- `PERFORMANCE_OPTIMIZATION.md` - Otimizações de performance
- `PARAMETERS_GUIDE.md` - Guia de parâmetros

---

## ✅ Checklist de Implementação

- [x] Análise de deadline (Monte Carlo)
- [x] Forecast "Quantos?" (Monte Carlo)
- [x] Forecast "Quando?" (Monte Carlo)
- [x] Análise de deadline (ML)
- [x] Forecast "Quantos?" (ML)
- [x] Forecast "Quando?" (ML)
- [x] Suporte a team_size
- [x] Suporte a min/max contributors
- [x] Suporte a S-curve
- [x] Suporte a lead times
- [x] Suporte a split rates
- [x] Testes completos
- [x] Documentação completa
- [x] Exemplos práticos

---

**Versão:** 2.2.0 - Deadline & Forecast Analysis
**Data:** 2025-10-10
**Status:** ✅ Implementado e Testado
