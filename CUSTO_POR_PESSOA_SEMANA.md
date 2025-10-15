# Implementação de Custos por Pessoa-Semana

## Resumo

A funcionalidade de **custos por pessoa-semana** foi completamente implementada no Flow Forecaster, permitindo que os usuários obtenham estimativas de custo baseadas em esforço para seus projetos.

## Fórmula de Cálculo

```
Custo Total = Esforço (pessoa-semanas) × Custo por Pessoa-Semana
```

Onde:
- **Esforço (pessoa-semanas)** = Semanas Projetadas × Contribuidores Médios
- **Custo por Pessoa-Semana** = Custo semanal por pessoa (salário + encargos + overhead)

## Arquivos Modificados

### 1. Backend (Python)

#### `cost_pert_beta.py` (Linhas 213-312)
- **Função `calculate_effort_based_cost()`**: Calcula custos para um único esforço
- **Função `calculate_effort_based_cost_with_percentiles()`**: Calcula custos para múltiplos percentis (P50, P85, P95)
- Retorna custos formatados e taxas de conversão (semana/mês/ano)

#### `app.py` (Linhas 606-704)
- **Endpoint `/api/deadline-analysis`**: Integrado com cálculos de custo
- Calcula custos para **Monte Carlo** (sempre disponível)
- Calcula custos para **Machine Learning** (quando disponível)
- Retorna estrutura completa com:
  - `cost_analysis.monte_carlo`: Custos P50, P85, P95 do Monte Carlo
  - `cost_analysis.machine_learning`: Custos P50, P85, P95 do ML
  - `cost_analysis.team_info`: Informações da equipe
  - `cost_analysis.formula`: Fórmula de cálculo
  - `cost_analysis.explanation`: Explicação contextual

### 2. Frontend (HTML/JavaScript)

#### `templates/deadline_analysis.html`

**Interface de Entrada (Linhas 228-244):**
- Campo para **Custo por Pessoa-Semana** (padrão: R$ 5.000)
- Tooltip explicativo sobre o cálculo
- Integrado com parâmetros avançados

**Função JavaScript `getFormData()` (Linhas 307-322):**
- Captura o valor de custo por pessoa-semana
- Envia para o backend via API

**Visualização de Resultados (Linhas 479-587):**
- **Seção de Análise de Custos** mostrando:
  - Fórmula e explicação
  - Parâmetros da equipe (tamanho, contribuidores médios, custo/semana)
  - **Monte Carlo - Custos Projetados:**
    - Custo P50 (Mediana)
    - Custo P85 (Recomendado) - destacado em verde
    - Custo P95 (Conservador)
    - Esforço em pessoa-semanas para cada percentil
  - **Machine Learning - Custos Projetados** (se disponível):
    - Mesma estrutura do Monte Carlo
  - **Referência de Taxas:**
    - Taxa por Pessoa-Semana
    - Taxa por Pessoa-Mês (4.33 semanas/mês)
    - Taxa por Pessoa-Ano (52 semanas/ano)

## Como Usar

### 1. Acesso à Interface
Navegue para: `/deadline-analysis`

### 2. Configuração de Parâmetros
1. Insira os **Dados Históricos** (throughput semanal)
2. Configure os **Dados do Projeto** (backlog, datas)
3. Expanda **Parâmetros Avançados**
4. Configure:
   - **Tamanho da Equipe**: Número de pessoas
   - **Min/Max Contributors**: Contribuidores mínimos/máximos
   - **Custo por Pessoa-Semana**: Valor em R$ (ex: 5000)

### 3. Executar Análise
Clique em **"Análise de Deadline"**

### 4. Visualizar Resultados
A seção **"Análise de Custos"** exibirá:
- Custos projetados para Monte Carlo e Machine Learning
- Diferentes níveis de confiança (P50, P85, P95)
- Esforço correspondente em pessoa-semanas
- Taxas de referência para diferentes períodos

## Exemplo de Cálculo

### Cenário:
- **Throughput histórico**: 4, 5, 6, 7, 5, 6, 7, 8 items/semana
- **Backlog**: 20 items
- **Data Início**: 01/10/2025
- **Deadline**: 01/11/2025 (4.3 semanas)
- **Tamanho da Equipe**: 2 pessoas
- **Custo por Pessoa-Semana**: R$ 5.000

### Resultados Esperados (Monte Carlo):
- **Semanas Projetadas P85**: ~3.5 semanas
- **Esforço P85**: 3.5 semanas × 2 pessoas = 7.0 pessoa-semanas
- **Custo P85**: 7.0 × R$ 5.000 = **R$ 35.000**

### Resultados Adicionais:
- **P50 (Mediana)**: ~3.0 semanas → R$ 30.000
- **P95 (Conservador)**: ~4.0 semanas → R$ 40.000

## Estrutura da API Response

```json
{
  "monte_carlo": { ... },
  "machine_learning": { ... },
  "cost_analysis": {
    "monte_carlo": {
      "cost_p50": {
        "total_cost": 30000.0,
        "formatted_total": "R$ 30,000.00",
        "effort_person_weeks": 6.0
      },
      "cost_p85": {
        "total_cost": 35000.0,
        "formatted_total": "R$ 35,000.00",
        "effort_person_weeks": 7.0
      },
      "cost_p95": {
        "total_cost": 40000.0,
        "formatted_total": "R$ 40,000.00",
        "effort_person_weeks": 8.0
      }
    },
    "machine_learning": { /* mesma estrutura */ },
    "team_info": {
      "team_size": 2,
      "avg_contributors": 2.0,
      "cost_per_week": 5000
    },
    "formula": "Custo = Esforço (pessoa-semanas) × Custo por Pessoa-Semana",
    "explanation": "Monte Carlo: Com esforço de 7.0 pessoa-semanas..."
  }
}
```

## Vantagens da Implementação

1. **Dupla Abordagem**: Custos calculados tanto por Monte Carlo quanto por Machine Learning
2. **Múltiplos Percentis**: P50, P85, P95 para diferentes níveis de confiança
3. **Transparência**: Mostra tanto o custo quanto o esforço em pessoa-semanas
4. **Flexibilidade**: Taxas convertidas automaticamente para mês e ano
5. **Visual Claro**: Destaque para o P85 (recomendado) em verde
6. **Sempre Disponível**: Monte Carlo funciona com poucos dados históricos

## Testes Realizados

✓ Módulo `cost_pert_beta.py` funciona corretamente
✓ Função `calculate_effort_based_cost()` retorna valores formatados
✓ Função `calculate_effort_based_cost_with_percentiles()` calcula múltiplos percentis
✓ Flask app carrega sem erros
✓ Rota `/api/deadline-analysis` existe e está funcional
✓ Interface HTML renderiza corretamente

## Próximos Passos (Opcional)

- [ ] Adicionar gráfico de custos por percentil
- [ ] Exportar análise de custos para PDF/Excel
- [ ] Comparação de cenários (What-If)
- [ ] Histórico de custos reais vs projetados
- [ ] Integração com moedas internacionais

---

**Data de Implementação**: 15 de outubro de 2025
**Status**: ✅ Completo e Testado
