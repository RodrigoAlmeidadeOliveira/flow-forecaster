# 🎯 Como Acessar o Backtesting com fold_stride

## Guia Rápido de Acesso

---

## 📍 Opção 1: Via Menu do Site (RECOMENDADO)

### Passo 1: Abrir o Site
```
http://localhost:8080
```

### Passo 2: Clicar no Menu "Backtesting"

Na **barra superior** (navbar), você verá um novo item:

```
┌─────────────────────────────────────────────────────────┐
│ Flow Forecasting   🧪 Backtesting   📚 Documentação   │
└─────────────────────────────────────────────────────────┘
                          ↑
                    CLIQUE AQUI
```

### Passo 3: Configurar e Executar

Você verá uma interface completa com:

1. **Dados de Throughput**
   - Cole seus dados diários separados por vírgula
   - Ou clique em "Carregar Exemplo" para testar

2. **Configurações**
   - **Backlog**: Número de itens a prever (ex: 150)
   - **Histórico Mínimo**: Dias de histórico para treinar (ex: 14)

3. **fold_stride - O NOVO RECURSO!**
   - **Horizonte de Previsão**:
     - 1 dia
     - 1 semana (7 dias)
     - 2 semanas (14 dias)
     - **1 mês (30 dias)** ← Recomendado
     - 2 meses (60 dias)
     - 3 meses (90 dias)

   - **Cadência de Atualização**:
     - Diária (a cada 1 dia)
     - **Semanal (a cada 7 dias)** ← Recomendado
     - Quinzenal (a cada 14 dias)
     - Mensal (a cada 30 dias)

4. **Executar Backtesting**
   - Clique no botão azul "▶ Executar Backtesting"
   - Aguarde alguns segundos
   - Veja os resultados!

---

## 📊 Exemplo Visual

```
┌────────────────────────────────────────────────────────────────┐
│ 🧪 Backtesting com fold_stride                                │
│                                                                 │
│ Valide suas previsões com horizontes longos                    │
│ e atualizações periódicas                                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ⚙️ Configuração do Backtesting                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 📊 Dados de Throughput                                         │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 5, 6, 4, 7, 5, 6, 8, 5, 4, 7, 6, 5, 7, 8, 6, 5, 4, 7... │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 🔍 Horizonte de Previsão:  [1 mês (30 dias) ▼]                │
│                                                                 │
│ 🔄 Cadência de Atualização: [Semanal (a cada 7 dias) ▼]       │
│                             ~85% mais rápido                    │
│                                                                 │
│ 💡 Como funciona:                                               │
│ • Faz uma previsão para os próximos 30 dias                   │
│ • Espera 7 dias                                                │
│ • Faz nova previsão (com mais 7 dias de histórico)            │
│ • Repete até acabarem os dados                                │
│                                                                 │
│            [📥 Carregar Exemplo]  [▶ Executar Backtesting]    │
└────────────────────────────────────────────────────────────────┘

RESULTADOS
┌────────────────────────────────────────────────────────────────┐
│ 📊 Resumo dos Resultados                                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Testes Executados    Erro Médio       MAPE         R² Score   │
│        10             -5.2%          15.3%          0.76        │
│                                                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ 📋 Resultados Detalhados                                        │
├────────────────────────────────────────────────────────────────┤
│ Teste  Treino      Previsto   Real      Erro     Erro %       │
│ 1      14 amostras 25.3 sem   26.1 sem  -0.8     -3.1%        │
│ 2      21 amostras 24.8 sem   25.2 sem  -0.4     -1.6%        │
│ 3      28 amostras 25.5 sem   24.9 sem  +0.6     +2.4%        │
│ ...                                                             │
└────────────────────────────────────────────────────────────────┘
```

---

## 📍 Opção 2: Via URL Direta

Você pode acessar diretamente:

```
http://localhost:8080/backtesting
```

---

## 📍 Opção 3: Via API (Para Desenvolvedores)

Se você prefere usar a API diretamente:

### JavaScript
```javascript
const response = await fetch('/api/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tpSamples: [5, 6, 4, 7, 5, 6, 8, 5, 4, 7, 6, 5, ...],
    backlog: 150,
    method: 'walk_forward',
    minTrainSize: 14,
    testSize: 30,        // ← Horizonte de 30 dias
    foldStride: 7,       // ← Atualização semanal
    confidenceLevel: 'P85',
    nSimulations: 10000
  })
});

const result = await response.json();
console.log(result.summary);
```

### Python
```python
import requests

response = requests.post('http://localhost:8080/api/backtest', json={
    'tpSamples': [5, 6, 4, 7, 5, 6, 8, 5, 4, 7, 6, 5, ...],
    'backlog': 150,
    'method': 'walk_forward',
    'minTrainSize': 14,
    'testSize': 30,        # ← Horizonte de 30 dias
    'foldStride': 7,       # ← Atualização semanal
    'confidenceLevel': 'P85',
    'nSimulations': 10000
})

result = response.json()
print(result['summary'])
```

### cURL
```bash
curl -X POST http://localhost:8080/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "tpSamples": [5, 6, 4, 7, 5, 6, 8, 5, 4, 7, 6, 5],
    "backlog": 150,
    "testSize": 30,
    "foldStride": 7,
    "confidenceLevel": "P85"
  }'
```

---

## 🎓 Exemplos Práticos

### Exemplo 1: Equipe Ágil (Sprint Semanal)

**Cenário**: Você quer prever 1 mês à frente, mas atualizar a previsão toda semana (quando termina uma sprint).

**Configuração**:
- **Horizonte**: 30 dias
- **Cadência**: 7 dias (semanal)
- **Backlog**: 150 itens

**Resultado**: ~10 testes em vez de 46 (**78% mais rápido!**)

---

### Exemplo 2: Release Quinzenal

**Cenário**: Releases a cada 2 semanas, horizonte de 2 meses.

**Configuração**:
- **Horizonte**: 60 dias
- **Cadência**: 14 dias (quinzenal)
- **Backlog**: 300 itens

**Resultado**: ~5 testes em vez de 76 (**93% mais rápido!**)

---

### Exemplo 3: Planejamento Trimestral

**Cenário**: Planejamento de 3 meses, revisão mensal.

**Configuração**:
- **Horizonte**: 90 dias
- **Cadência**: 30 dias (mensal)
- **Backlog**: 500 itens

**Resultado**: ~2-3 testes em vez de 76 (**96% mais rápido!**)

---

## 🔧 Teste Rápido (5 minutos)

### Passo a Passo:

1. **Abra o site**:
   ```
   http://localhost:8080
   ```

2. **Clique em "🧪 Backtesting"** no menu superior

3. **Clique em "📥 Carregar Exemplo"**
   - Isso carrega 60 dias de dados sintéticos
   - Configuração: Horizonte 30 dias, Cadência Semanal

4. **Clique em "▶ Executar Backtesting"**

5. **Aguarde ~10 segundos**

6. **Veja os resultados!**
   - Testes executados
   - Erro médio
   - MAPE (Mean Absolute Percentage Error)
   - R² Score
   - Tabela detalhada de cada teste
   - Relatório completo

---

## 📱 Acesso Mobile

A interface é **100% responsiva**. Você pode acessar do celular:

```
http://SEU-IP:8080/backtesting
```

---

## 🆘 Problemas Comuns

### Erro: "Need at least 20 throughput samples"

**Solução**: Insira mais dados. Para testes significativos, recomendamos:
- **Mínimo**: 20 valores
- **Ideal**: 60-90 valores (2-3 meses de dados diários)

### Erro: "Page not found"

**Solução**:
1. Certifique-se de que o servidor está rodando
2. Verifique se está na branch correta:
   ```bash
   git branch
   ```
3. Deve mostrar: `claude/add-fold-stride-backtesting-011CUqfJiLhi5Gv73CdaHrKU`

### Botão "Executar" não faz nada

**Solução**: Abra o console do navegador (F12) e veja se há erros.
Verifique se a API `/api/backtest` está acessível.

---

## 📚 Mais Informações

- **Documentação Técnica**: `FOLD_STRIDE_GUIDE.md`
- **Testes**: `test_fold_stride.py`
- **API**: `app.py:2696-2810`

---

## ✨ Recursos da Interface

✅ **Dropdown de Configurações**: Valores pré-definidos comuns
✅ **Badge de Eficiência**: Mostra % de redução de simulações em tempo real
✅ **Carregamento de Exemplo**: Teste instantâneo com dados sintéticos
✅ **Validação de Inputs**: Avisos claros se algo estiver errado
✅ **Loading State**: Indicador visual durante execução
✅ **Resultados Detalhados**: Tabela + relatório formatado
✅ **Métricas de Acurácia**: MAPE, R², Erro Médio
✅ **Design Moderno**: Bootstrap 5 com gradientes e animações
✅ **Responsivo**: Funciona em desktop, tablet e mobile

---

**Desenvolvido com ❤️ por Flow Forecaster Team**

**Versão**: 2.0 (com fold_stride)
**Data**: 2025-11-06
