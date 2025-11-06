# Guia de Uso: fold_stride no Backtesting

## 📋 Visão Geral

O parâmetro `fold_stride` foi adicionado ao backtesting walk-forward para permitir **previsões de horizonte longo com atualizações periódicas**.

### Problema Resolvido

Anteriormente, o backtesting walk-forward avançava 1 período por vez, o que:
- ❌ Gerava muitas simulações (lento)
- ❌ Não refletia cenários reais (ninguém faz previsão diária)
- ❌ Não permitia testar horizontes longos com atualizações espaçadas

### Solução: fold_stride

Com `fold_stride`, você pode:
- ✅ Prever 30 dias à frente
- ✅ Atualizar a previsão apenas semanalmente
- ✅ Reduzir drasticamente o número de simulações
- ✅ Simular cadências realistas de atualização

---

## 🎯 Conceitos

### Parâmetros Principais

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `test_size` | Horizonte de previsão (quantos períodos prever) | `30` = prever 30 dias |
| `fold_stride` | Cadência de atualização (a cada quantos períodos atualizar) | `7` = atualizar semanalmente |
| `min_train_size` | Tamanho mínimo do histórico de treino | `14` = mínimo 2 semanas |

### Como Funciona

```
Dados: [D1, D2, D3, ..., D60] (60 dias de throughput diário)

fold_stride = 1 (padrão):
  Teste 1: Treino [D1-D14], Teste [D15]
  Teste 2: Treino [D1-D15], Teste [D16]
  Teste 3: Treino [D1-D16], Teste [D17]
  ...
  Total: 46 testes

fold_stride = 7 (semanal):
  Teste 1: Treino [D1-D14], Teste [D15-D44]  (horizonte 30 dias)
  Teste 2: Treino [D1-D21], Teste [D22-D51]  (1 semana depois)
  Teste 3: Treino [D1-D28], Teste [D29-D58]  (mais 1 semana)
  Total: 3 testes
```

---

## 💡 Casos de Uso

### Caso 1: Atualizações Semanais (Mais Comum)

**Cenário**: Equipe ágil com sprints semanais, quer prever 1 mês à frente

```python
from backtesting import run_walk_forward_backtest

# Throughput diário dos últimos 90 dias
daily_throughput = [5, 6, 4, 7, 5, ...]  # 90 valores

summary = run_walk_forward_backtest(
    tp_samples=daily_throughput,
    backlog=150,
    min_train_size=14,     # Mínimo 2 semanas de histórico
    test_size=30,          # Horizonte de 30 dias
    fold_stride=7,         # Atualizar a cada 7 dias
    confidence_level='P85',
    n_simulations=10000
)

print(f"Total de testes: {summary.total_tests}")
print(f"Erro médio: {summary.mean_error_pct:.2f}%")
```

**Resultado esperado**: ~10 testes (em vez de 76 com stride=1)

---

### Caso 2: Atualizações Quinzenais

**Cenário**: Releases a cada 2 semanas, horizonte de 2 meses

```python
summary = run_walk_forward_backtest(
    tp_samples=daily_throughput,
    backlog=300,
    min_train_size=21,     # 3 semanas mínimo
    test_size=60,          # 2 meses de horizonte
    fold_stride=14,        # Atualizar a cada 2 semanas
    confidence_level='P85',
    n_simulations=10000
)
```

**Benefício**: Redução de ~15x no número de simulações

---

### Caso 3: Atualizações Mensais

**Cenário**: Planejamento trimestral, revisão mensal

```python
summary = run_walk_forward_backtest(
    tp_samples=daily_throughput,
    backlog=500,
    min_train_size=30,     # 1 mês mínimo
    test_size=90,          # Prever 3 meses
    fold_stride=30,        # Atualizar mensalmente
    confidence_level='P85',
    n_simulations=10000
)
```

---

## 🌐 Uso via API REST

### Endpoint: `/api/backtest`

#### Exemplo 1: Previsão Semanal (30 dias)

```bash
curl -X POST http://localhost:8080/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "tpSamples": [5, 6, 4, 7, 5, 6, 8, 5, 4, 7, 6, 5, ...],
    "backlog": 150,
    "method": "walk_forward",
    "minTrainSize": 14,
    "testSize": 30,
    "foldStride": 7,
    "confidenceLevel": "P85",
    "nSimulations": 10000
  }'
```

#### Exemplo 2: Previsão Quinzenal (60 dias)

```javascript
// JavaScript/TypeScript
const response = await fetch('/api/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tpSamples: dailyThroughput,
    backlog: 200,
    method: 'walk_forward',
    minTrainSize: 21,
    testSize: 60,
    foldStride: 14,  // ← Bi-weekly
    confidenceLevel: 'P85',
    nSimulations: 10000
  })
});

const result = await response.json();
console.log(`Tests run: ${result.summary.total_tests}`);
console.log(`Mean error: ${result.summary.mean_error_pct}%`);
```

---

## 📊 Comparação de Performance

### Cenário: 90 dias de dados diários

| Configuração | test_size | fold_stride | Testes Executados | Tempo (est.) | Redução |
|-------------|-----------|-------------|-------------------|--------------|---------|
| **Padrão** | 1 | 1 | 76 | ~4 min | - |
| **Semanal** | 30 | 7 | 10 | ~30 seg | **87% ⬇** |
| **Quinzenal** | 60 | 14 | 5 | ~15 seg | **93% ⬇** |
| **Mensal** | 90 | 30 | 2 | ~6 seg | **97% ⬇** |

---

## ⚠️ Validações e Erros

### Validação 1: fold_stride >= 1

```python
# ❌ ERRO
run_walk_forward_backtest(..., fold_stride=0)
# ValueError: fold_stride must be >= 1
```

### Validação 2: fold_stride <= tamanho dos dados

```python
# ❌ ERRO
run_walk_forward_backtest(tp_samples=[1,2,3,4,5], fold_stride=10)
# ValueError: fold_stride (10) cannot be larger than number of samples (5)
```

### Validação 3: Dados suficientes

```python
# ❌ ERRO
run_walk_forward_backtest(
    tp_samples=[1,2,3,4,5],
    min_train_size=10,  # Precisa de 10, tem apenas 5
    fold_stride=1
)
# ValueError: Need at least 11 samples for backtesting. Got 5.
```

---

## 🎨 Interface do Usuário

### Exemplo de Formulário

```html
<form id="backtestForm">
  <div class="form-group">
    <label>Horizonte de Previsão (dias)</label>
    <input type="number" name="testSize" value="30" min="1" max="365">
    <small>Quantos dias você quer prever?</small>
  </div>

  <div class="form-group">
    <label>Cadência de Atualização (dias)</label>
    <select name="foldStride">
      <option value="1">Diária (1 dia)</option>
      <option value="7" selected>Semanal (7 dias)</option>
      <option value="14">Quinzenal (14 dias)</option>
      <option value="30">Mensal (30 dias)</option>
    </select>
    <small>Com que frequência você quer atualizar a previsão?</small>
  </div>

  <div class="form-group">
    <label>Histórico Mínimo (dias)</label>
    <input type="number" name="minTrainSize" value="14" min="5" max="90">
    <small>Quantos dias de histórico mínimo para treinar?</small>
  </div>

  <button type="submit">Executar Backtesting</button>
</form>
```

---

## 📈 Interpretação dos Resultados

### Exemplo de Saída

```json
{
  "method": "walk_forward",
  "test_size": 30,
  "fold_stride": 7,
  "summary": {
    "total_tests": 10,
    "successful_tests": 10,
    "failed_tests": 0,
    "mean_error_pct": -5.2,
    "median_error_pct": -3.8,
    "std_error_pct": 12.4,
    "accuracy_metrics": {
      "mape": 15.3,
      "rmse": 2.1,
      "r_squared": 0.76,
      "bias_direction": "slightly_underestimated"
    }
  }
}
```

### Interpretação

| Métrica | Valor | Significado |
|---------|-------|-------------|
| `total_tests: 10` | 10 testes | Executou 10 previsões (1 a cada 7 dias) |
| `mean_error_pct: -5.2%` | -5.2% | Em média, subestimou em 5.2% |
| `mape: 15.3%` | 15.3% | Erro absoluto médio de 15.3% |
| `r_squared: 0.76` | 0.76 | Modelo explica 76% da variação (bom!) |

---

## 🧪 Testes

### Executar Suite de Testes

```bash
# Executar todos os testes de fold_stride
python test_fold_stride.py
```

### Testes Incluídos

1. ✅ Walk-forward padrão (fold_stride=1)
2. ✅ Atualizações semanais (fold_stride=7)
3. ✅ Atualizações quinzenais (fold_stride=14)
4. ✅ Validação de erros (fold_stride=0, fold_stride>data)
5. ✅ Comparação de performance (stride vs padrão)

---

## 💡 Recomendações

### Quando Usar fold_stride > 1?

✅ **Use fold_stride > 1 quando:**
- Você tem dados diários mas atualiza previsões semanalmente
- Quer reduzir tempo de execução do backtesting
- Precisa simular cadências realistas de atualização
- Tem horizontes longos (>14 dias)

❌ **Não use fold_stride > 1 quando:**
- Seus dados já são semanais/mensais (use stride=1)
- Quer máxima granularidade de validação
- Tem poucos dados (< 30 períodos)

### Combinações Recomendadas

| Tipo de Dados | Horizonte | fold_stride Recomendado |
|---------------|-----------|-------------------------|
| Diário | 30 dias | 7 (semanal) |
| Diário | 60 dias | 14 (quinzenal) |
| Diário | 90 dias | 30 (mensal) |
| Semanal | 4 semanas | 1 (padrão) |
| Semanal | 12 semanas | 2 (bi-semanal) |

---

## 🔗 Referências

- **Código**: `backtesting.py:84-210` - Função `run_walk_forward_backtest()`
- **Testes**: `test_fold_stride.py` - Suite completa de testes
- **API**: `app.py:2696-2810` - Endpoint `/api/backtest`
- **Paper**: Wheeler's "Understanding Variation" - Time series validation

---

## 🚀 Próximos Passos

Após implementar fold_stride, você pode:

1. **Process Behavior Charts** - Adicionar SPC (Statistical Process Control)
2. **Auto-tuning** - Sugerir automaticamente melhor fold_stride baseado nos dados
3. **Visualizações** - Gráficos mostrando impacto do fold_stride na acurácia
4. **Dashboard** - UI interativa para configurar fold_stride

---

**Versão**: 1.0
**Data**: 2025-11-06
**Autor**: Flow Forecaster Team
