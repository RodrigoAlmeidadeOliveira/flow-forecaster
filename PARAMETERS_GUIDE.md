# Parameters Guide - n_simulations Configuration

## Overview

O parâmetro `n_simulations` (ou `nSimulations` nas APIs REST) controla o **número de iterações** executadas nas simulações Monte Carlo. Este guia explica como o parâmetro funciona e como configurá-lo corretamente.

## ✅ Status: Funcionamento Correto

**O código JÁ está implementado corretamente**. Os valores de `n_simulations` são sempre respeitados quando fornecidos pelo usuário. Os valores fixos que você vê no código são apenas **defaults** (valores padrão) usados quando o usuário não especifica um valor.

## Como Funciona

### 1. API REST (`/api/mc-throughput`)

```python
# app.py:234
n_simulations = data.get('nSimulations', 10000)  # Default: 10000
mc_results = simulate_throughput_forecast(tp_samples, backlog, n_simulations)
```

**Comportamento:**
- Se o usuário enviar `"nSimulations": 50000` → usa 50000
- Se o usuário não enviar nada → usa default 10000

### 2. API REST (`/api/combined-forecast`)

```python
# app.py:284
n_simulations = data.get('nSimulations', 10000)  # Default: 10000
mc_results = simulate_throughput_forecast(tp_samples, backlog, n_simulations)
```

**Comportamento:**
- Se o usuário enviar `"nSimulations": 100000` → usa 100000
- Se o usuário não enviar nada → usa default 10000

### 3. API REST (`/api/simulate`)

```python
# app.py (complete mode)
# O valor vem direto do request
simulation_data = request.json
simulation_data['numberOfSimulations']  # Obrigatório no payload
```

**Comportamento:**
- O usuário DEVE especificar `"numberOfSimulations"` no JSON
- Valor padrão na interface web: 100000

### 4. Função Python `simulate_throughput_forecast()`

```python
def simulate_throughput_forecast(
    tp_samples: List[float],
    backlog: int,
    n_simulations: int = 10000  # Default
) -> Dict[str, Any]:
```

**Uso:**
```python
# Com valor customizado
result = simulate_throughput_forecast(
    tp_samples=[5, 6, 7, 4, 8],
    backlog=50,
    n_simulations=50000  # ← Especifica 50000
)

# Com valor default
result = simulate_throughput_forecast(
    tp_samples=[5, 6, 7, 4, 8],
    backlog=50
    # n_simulations usa default: 10000
)
```

### 5. Função Python `run_unified_simulation()`

```python
def run_unified_simulation(
    tp_samples: List[float],
    backlog: int,
    n_simulations: int = 10000,  # Default
    mode: str = 'complete',
    ...
) -> Dict[str, Any]:
```

**Uso:**
```python
# Modo simple com 25000 simulações
result = run_unified_simulation(
    tp_samples=[5, 6, 7, 4, 8],
    backlog=50,
    n_simulations=25000,  # ← Especifica 25000
    mode='simple'
)

# Modo complete com 100000 simulações
result = run_unified_simulation(
    tp_samples=[5, 6, 7, 4, 8],
    backlog=50,
    n_simulations=100000,  # ← Especifica 100000
    mode='complete',
    team_size=10,
    min_contributors=2,
    max_contributors=5
)
```

### 6. Classe Weibull `run_simulation()`

```python
def run_simulation(
    self,
    backlog: int,
    n_runs: int = 100000  # Default (mais alto para Weibull)
) -> Dict[str, Any]:
```

**Nota:** O default é **100000** (mais alto) porque Weibull é estatisticamente mais preciso com mais amostras.

## Exemplos de Uso nas APIs

### Exemplo 1: API `/api/mc-throughput` com 50K simulações

```bash
curl -X POST http://localhost:8080/api/mc-throughput \
  -H "Content-Type: application/json" \
  -d '{
    "tpSamples": [5, 6, 7, 4, 8, 6, 5, 7],
    "backlog": 50,
    "nSimulations": 50000
  }'
```

### Exemplo 2: API `/api/combined-forecast` com 100K simulações

```bash
curl -X POST http://localhost:8080/api/combined-forecast \
  -H "Content-Type: application/json" \
  -d '{
    "tpSamples": [5, 6, 7, 4, 8, 6, 5, 7, 6, 8],
    "backlog": 50,
    "forecastSteps": 4,
    "nSimulations": 100000
  }'
```

### Exemplo 3: API `/api/simulate` (Complete Mode) com 150K simulações

```bash
curl -X POST http://localhost:8080/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "projectName": "My Project",
    "numberOfSimulations": 150000,
    "tpSamples": [5, 6, 7, 4, 8, 6, 5, 7],
    "numberOfTasks": 50,
    "totalContributors": 10,
    "minContributors": 2,
    "maxContributors": 5,
    "sCurveSize": 20,
    "confidenceLevel": 85
  }'
```

## Valores Recomendados

| Modo | Uso | n_simulations Recomendado | Tempo Estimado |
|------|-----|---------------------------|----------------|
| **Quick Test** | Desenvolvimento/Debug | 1,000 - 5,000 | < 1 segundo |
| **Standard** | Uso geral, forecasts rápidos | 10,000 | 1-2 segundos |
| **High Confidence** | Apresentações, decisões importantes | 50,000 - 100,000 | 5-10 segundos |
| **Maximum Precision** | Análise estatística rigorosa | 100,000 - 500,000 | 10-60 segundos |
| **Weibull Mode** | Análise estatística avançada | 100,000+ | 10-30 segundos |

## Trade-offs

### Mais Simulações (↑)
✅ **Vantagens:**
- Maior precisão estatística
- Distribuições mais suaves
- Percentis mais confiáveis
- Melhor para decisões críticas

❌ **Desvantagens:**
- Tempo de execução maior
- Maior uso de memória
- Pode ser desnecessário para forecasts simples

### Menos Simulações (↓)
✅ **Vantagens:**
- Execução rápida
- Menor uso de recursos
- Suficiente para forecasts exploratórios

❌ **Desvantagens:**
- Distribuições podem ser irregulares
- Percentis menos precisos
- Não recomendado para commitments

## Validação

Execute o teste de validação para confirmar que os parâmetros estão funcionando:

```bash
python test_parameters.py
```

Resultado esperado:
```
✓ ALL PARAMETER TESTS COMPLETED
The n_simulations parameter is correctly respected in all functions.
```

## Interface Web

### Página Principal (Monte Carlo)
- Campo: "Number of simulations"
- Default: **100,000**
- Range: 10,000 - 10,000,000
- Localização: `templates/index.html:210`

### Página Avançada (ML + MC)
- Campo: "Monte Carlo Simulations"
- Default: **10,000**
- Range: 1,000 - 100,000
- Localização: `templates/index.html:436`

## Conclusão

**O sistema está funcionando corretamente!**

- ✅ Todos os valores de `n_simulations` fornecidos pelo usuário são respeitados
- ✅ Defaults são usados apenas quando o usuário não especifica
- ✅ Todos os testes de validação passam
- ✅ APIs REST funcionam como esperado

Os valores "fixos" que você viu no código são **apenas defaults**, não valores hardcoded que ignoram a entrada do usuário.

---

**Data:** 2025-10-10
**Status:** ✅ Validado e Funcionando
**Testes:** `test_parameters.py` - Todos os testes PASSED
