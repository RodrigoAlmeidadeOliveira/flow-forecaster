# 📘 Manual do Usuário - Flow Forecaster

> Guia completo para uso do Flow Forecaster: previsões probabilísticas de projetos com Machine Learning e Monte Carlo

**Versão**: 2.0
**Última atualização**: Outubro 2025
**Acesso**: https://flow-forecaster.fly.dev/

---

## 📋 Índice

1. [Introdução](#introdução)
2. [Conceitos Fundamentais](#conceitos-fundamentais)
3. [Primeiros Passos](#primeiros-passos)
4. [Funcionalidades Principais](#funcionalidades-principais)
5. [Análise de Custos](#análise-de-custos)
6. [Análise de Deadline](#análise-de-deadline)
7. [Perguntas Frequentes](#perguntas-frequentes)
8. [Dicas e Boas Práticas](#dicas-e-boas-práticas)
9. [Solução de Problemas](#solução-de-problemas)
10. [Glossário](#glossário)

---

## 🎯 Introdução

### O que é o Flow Forecaster?

O Flow Forecaster é uma ferramenta probabilística de previsão de projetos que combina:

- **Simulações Monte Carlo**: 10.000+ iterações para análise probabilística robusta
- **Machine Learning**: Modelos preditivos avançados (Random Forest, XGBoost, Gradient Boosting)
- **Análise de Custos**: Estimativas baseadas em esforço e distribuição PERT-Beta
- **Análise de Deadline**: Previsões sobre prazos e entregas

### Por que usar previsões probabilísticas?

Em vez de trabalhar com estimativas únicas ("o projeto termina em 10 semanas"), trabalhamos com **distribuições de probabilidade**:

- **P50 (Mediana)**: 50% de chance de terminar neste prazo ou antes
- **P85 (Recomendado)**: 85% de chance - equilibra confiança e realismo
- **P95 (Conservador)**: 95% de chance - para contextos de alto risco

### Quando usar cada método?

| Método | Use quando... | Dados necessários |
|--------|---------------|-------------------|
| **Monte Carlo** | • Dados voláteis<br>• Precisa modelar riscos<br>• Quer distribuições probabilísticas | Mínimo 3-5 amostras de throughput |
| **Machine Learning** | • Existem tendências claras<br>• Dados são estáveis<br>• Precisa de previsões pontuais | Mínimo 8 semanas de histórico |
| **Combined** | • Quer validação cruzada<br>• Precisa de análise robusta<br>• Relatórios para stakeholders | 8+ semanas de histórico |

---

## 📚 Conceitos Fundamentais

### Throughput (Vazão)

**Definição**: Número de itens completados por período de tempo (geralmente por semana).

**Exemplo**: Se sua equipe completou 5, 6, 7, 4, 8 itens nas últimas 5 semanas, seu throughput histórico é: `[5, 6, 7, 4, 8]`

**Como coletar**:
1. Defina o período de coleta (ex: últimas 12 semanas)
2. Conte quantos itens foram finalizados em cada semana
3. Use dados de ferramentas como Jira, Azure DevOps, Trello, etc.

**Dica**: Quanto mais dados históricos, mais precisas as previsões.

### Backlog

**Definição**: Número total de itens pendentes que precisam ser completados.

**Exemplo**: Se você tem 50 user stories ainda não finalizadas, seu backlog é `50`.

**Importante**:
- Conte apenas itens no mesmo nível de granularidade usado no throughput
- Se throughput é em "stories", backlog também deve ser em "stories"
- Não misture diferentes tipos de itens (ex: stories com bugs)

### Lead Time (Tempo de Ciclo)

**Definição**: Tempo que cada item leva desde o início até a conclusão.

**Exemplo**: Se 3 itens levaram 2, 3 e 4 dias para serem completados, seu lead time histórico é: `[2, 3, 4]`

**Quando usar**: Útil para análises mais avançadas e modelagem de WIP (Work in Progress).

### Split Rate (Taxa de Divisão)

**Definição**: Quantas vezes, em média, um item é dividido em sub-itens durante o desenvolvimento.

**Formato**: Use multiplicadores, não porcentagens:
- `1.1` = item dividido em 10% a mais (1 item vira 1.1)
- `1.5` = item dividido em 50% a mais (1 item vira 1.5)
- `2.0` = item dobrado (1 item vira 2)

**Exemplo**: Se você estima 20 items mas historicamente eles viram 25, seu split rate é `1.25` (25% de aumento).

### Distribuição PERT-Beta

**Definição**: Técnica de estimativa de três pontos usada para modelar incertezas.

**Componentes**:
- **Otimista (a)**: Melhor cenário possível
- **Mais Provável (m)**: Cenário mais realista
- **Pessimista (b)**: Pior cenário razoável

**Fórmula**:
```
Média PERT = (a + 4m + b) / 6
Desvio Padrão = (b - a) / 6
```

**Exemplo**: Para estimar o esforço de um projeto:
- Otimista: 30 pessoa-semanas
- Mais Provável: 50 pessoa-semanas
- Pessimista: 80 pessoa-semanas

### Percentis (P50, P85, P95)

**Definição**: Pontos de corte em uma distribuição probabilística.

- **P50 (Mediana)**: 50% dos cenários simulados terminam antes deste ponto
- **P85**: 85% dos cenários terminam antes deste ponto (recomendado para planejamento)
- **P95**: 95% dos cenários terminam antes deste ponto (planejamento conservador)

**Interpretação**:
- Se P85 = 10 semanas, há 85% de chance de terminar em 10 semanas ou menos
- Se P95 = 12 semanas, há apenas 5% de chance de levar mais que 12 semanas

---

## 🚀 Primeiros Passos

### 1. Acessando o Sistema

Acesse: **https://flow-forecaster.fly.dev/**

### 2. Preparando seus Dados

Antes de usar a ferramenta, colete:

**Dados Obrigatórios**:
- ✅ Throughput histórico (mínimo 3-5 amostras, ideal 8+)
- ✅ Backlog atual (número de itens pendentes)
- ✅ Data de início do projeto
- ✅ Data de deadline (se aplicável)

**Dados Opcionais (Melhoram a Precisão)**:
- 📊 Lead times históricos
- 📊 Split rates observados
- 📊 Tamanho da equipe
- 📊 Contribuidores mínimos/máximos
- 📊 Riscos identificados

### 3. Estrutura da Interface

A interface possui **4 abas principais**:

1. **Simulação Monte Carlo**: Previsões probabilísticas tradicionais
2. **Machine Learning**: Previsões baseadas em tendências e padrões
3. **Análise de Custos**: Estimativas de custo baseadas em esforço e demanda
4. **Análise de Deadline**: Análise combinada de prazos e entregas

---

## 🎲 Funcionalidades Principais

### 1️⃣ Simulação Monte Carlo

**O que faz**: Executa 10.000+ simulações probabilísticas para prever quando o backlog será completado.

**Como usar**:

1. **Acesse a aba "Simulação Monte Carlo"**

2. **Preencha os Dados do Projeto**:
   ```
   Nome do Projeto: Meu Projeto
   Número de Tarefas (Backlog): 50
   Número de Simulações: 10000
   ```

3. **Insira o Throughput Histórico**:
   ```
   Throughput Semanal: 5, 6, 7, 4, 8, 6, 5, 7
   ```
   **Formato**: Números separados por vírgula

4. **Configure Parâmetros Avançados** (opcional):
   - **Tamanho da Equipe**: Número de pessoas (ex: 5)
   - **Min/Max Contributors**: Variação na disponibilidade (ex: 3 a 5)
   - **Curva-S**: Tamanho da rampa de produtividade (0 = sem rampa, 10 = rampa lenta)

5. **Adicione Lead Times** (opcional):
   ```
   Lead Times (dias): 2, 3, 4, 2, 5, 3
   ```

6. **Adicione Split Rates** (opcional):
   ```
   Split Rates: 1.1, 1.2, 1.15
   ```
   **Lembre-se**: Use multiplicadores, não porcentagens!

7. **Defina Riscos** (opcional):
   - Clique em "Adicionar Risco"
   - Preencha: Nome, Probabilidade (0-100%), Impacto em semanas

8. **Execute a Simulação**:
   - Clique em **"Executar Simulação"**
   - Aguarde o processamento (geralmente 2-5 segundos)

**Interpretando os Resultados**:

```
📊 Resultados Probabilísticos:

P50 (Mediana):      8.5 semanas   ← 50% de chance
P85 (Recomendado):  10.2 semanas  ← 85% de chance (USE ESTE!)
P95 (Conservador):  12.1 semanas  ← 95% de chance
```

**Gráficos Gerados**:
- **Histograma de Distribuição**: Mostra a distribuição de probabilidade dos cenários
- **Burn-down Trajectories**: Trajetórias de conclusão do backlog
- **Estatísticas de Entrada**: Análise dos dados históricos

**Dica**: Use **P85** para planejamento padrão. Reserve P95 para projetos críticos.

---

### 2️⃣ Machine Learning

**O que faz**: Usa modelos preditivos (Random Forest, XGBoost, Gradient Boosting) para prever o throughput futuro baseado em tendências históricas.

**Requisitos**: Mínimo **8 semanas** de throughput histórico.

**Como usar**:

1. **Acesse a aba "Machine Learning"**

2. **Insira o Throughput Histórico**:
   ```
   Throughput Semanal: 5, 6, 7, 4, 8, 6, 5, 7, 6, 8, 7, 9
   ```
   **Mínimo**: 8 amostras

3. **Configure os Parâmetros**:
   - **Forecast Steps**: Quantas semanas à frente prever (padrão: 4)
   - **Modelo**: Escolha entre:
     - `ensemble` (recomendado): Combina todos os modelos
     - `random_forest`: Robusto, boa baseline
     - `xgboost`: Máxima precisão
     - `hist_gradient_boosting`: Melhor para intervalos de confiança

4. **Defina Backlog e Data de Início** (opcional):
   ```
   Backlog: 50
   Data de Início: 01/10/2025
   ```

5. **Execute a Previsão**:
   - Clique em **"Executar Previsão ML"**
   - Aguarde o processamento (5-10 segundos)

**Interpretando os Resultados**:

```
🤖 Machine Learning Forecast

Risco Avaliado: LOW ✅
Confiança: ALTA

Previsão Média (próximas 4 semanas): 7.2, 7.5, 7.8, 8.0 items/semana

Intervalos de Confiança:
P10 (Pessimista): 5.5, 5.8, 6.0, 6.2
P90 (Otimista):   9.0, 9.3, 9.6, 10.0

Semanas para completar backlog (50 items): ~6.5 semanas
```

**Risk Assessment**:
- **LOW** ✅: Dados estáveis, previsão confiável
- **MEDIUM** ⚠️: Alguma volatilidade, use com cautela
- **HIGH** ❌: Dados muito voláteis, prefira Monte Carlo

**Gráficos Gerados**:
- **ML Forecast com Intervalos**: Previsões futuras com bandas de confiança
- **Análise Histórica**: Distribuição, autocorrelação, tendências
- **Walk-Forward Validation**: Validação da precisão do modelo

**Dica**: Se o Risk Assessment for HIGH, prefira usar Monte Carlo em vez de ML.

---

### 3️⃣ Análise Combinada (ML + Monte Carlo)

**O que faz**: Executa ambas as análises (ML e MC) simultaneamente e compara os resultados.

**Quando usar**:
- Quer validar uma previsão com outra
- Precisa de análise robusta para stakeholders
- Deseja entender divergências entre métodos

**Como usar**:

1. **Acesse a aba "Análise Combinada"** (ou "Advanced Forecast")

2. **Preencha todos os dados necessários**:
   - Throughput histórico (8+ amostras)
   - Backlog
   - Parâmetros avançados

3. **Execute a Análise Combinada**:
   - Clique em **"Executar Análise Combinada"**
   - Aguarde o processamento (10-15 segundos)

**Interpretando os Resultados**:

```
📊 Comparação ML vs Monte Carlo

Monte Carlo P85:     10.2 semanas
Machine Learning P85: 9.8 semanas

Diferença: 0.4 semanas (4%)

Consenso: ✅ Ambos os métodos concordam
Recomendação: Alta confiabilidade na previsão

Explicação:
✓ Ambos indicam viabilidade de completar em ~10 semanas
✓ Pequena divergência sugere previsão robusta
✓ Use a estimativa mais conservadora (10.2 semanas) para planejamento
```

**Gráfico de Comparação**:
- Mostra ambas as previsões lado a lado
- Destaca divergências e consensos
- Facilita comunicação com stakeholders

**Interpretando Divergências**:

| Diferença | Interpretação | Ação Recomendada |
|-----------|---------------|------------------|
| < 10% | Excelente consenso | Use qualquer estimativa |
| 10-20% | Divergência moderada | Use a mais conservadora |
| 20-50% | Divergência significativa | Revise os dados |
| > 50% | Divergência crítica | Colete mais dados históricos |

---

## 💰 Análise de Custos

A funcionalidade de análise de custos permite estimar o custo total do projeto baseado em esforço ou demanda.

### 💼 Custo por Pessoa-Semana

**O que faz**: Calcula custos baseados no esforço projetado (pessoa-semanas) multiplicado pelo custo semanal por pessoa.

**Fórmula**:
```
Custo Total = Esforço (pessoa-semanas) × Custo por Pessoa-Semana
```

**Como usar**:

1. **Acesse a aba "Análise de Custos"**

2. **Localize a seção "💰 Custo por Pessoa-Semana"**

3. **Defina o Custo por Pessoa-Semana**:
   ```
   Custo por Pessoa-Semana (R$): 5000
   ```
   **O que incluir**: Salário + encargos + overhead + benefícios

4. **Opção A: Usar Simulação Monte Carlo**:
   - Execute uma simulação Monte Carlo primeiro
   - A análise de custos usará automaticamente os resultados
   - Clique em **"Calcular Custos por Esforço"**

5. **Opção B: Usar Estimativa PERT-Beta**:
   - Preencha os campos de estimativa de esforço:
     ```
     Esforço Otimista (a):      30.0 pessoa-semanas
     Esforço Mais Provável (m): 50.0 pessoa-semanas
     Esforço Pessimista (b):    80.0 pessoa-semanas
     ```
   - Configure o número de simulações (padrão: 10.000)
   - Clique em **"Calcular Custos por Esforço"**

6. **Opção C: Esforço Manual**:
   - Insira um esforço estimado diretamente:
     ```
     Esforço Estimado (pessoa-semanas): 45.0
     ```
   - Clique em **"Calcular Custos por Esforço"**

**Interpretando os Resultados**:

```
💰 Custos Projetados por Esforço

┌─────────────────────────────────────┐
│ P50 (Mediana)                       │
│ Custo: R$ 225,000.00                │
│ Esforço: 45.0 pessoa-semanas        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ P85 (Recomendado) ✅                │
│ Custo: R$ 275,000.00                │
│ Esforço: 55.0 pessoa-semanas        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ P95 (Conservador)                   │
│ Custo: R$ 325,000.00                │
│ Esforço: 65.0 pessoa-semanas        │
└─────────────────────────────────────┘

📋 Taxas de Referência:
Por Pessoa-Semana:  R$ 5,000.00
Por Pessoa-Mês:     R$ 21,650.00 (4.33 semanas/mês)
Por Pessoa-Ano:     R$ 260,000.00 (52 semanas/ano)
```

**Gráfico Gerado**:
- **Histograma de Distribuição do Esforço (PERT-Beta)**: Mostra a distribuição probabilística do esforço projetado

**Dica**: Use **P85** para orçamento padrão. Reserve P95 para projetos com alto risco ou contingências.

---

### 📊 Custo Médio da Demanda

**O que faz**: Calcula custos baseados no custo médio por item do backlog usando distribuição PERT-Beta.

**Fórmula**:
```
Custo Total = Custo Médio por Item × Backlog Total
```

**Como usar**:

1. **Acesse a aba "Análise de Custos"**

2. **Localize a seção "📊 Custo Médio da Demanda"**

3. **Defina as Estimativas PERT-Beta**:
   ```
   Custo Otimista por Item (a):      R$ 500
   Custo Mais Provável por Item (m): R$ 1000
   Custo Pessimista por Item (b):    R$ 2000
   ```

4. **Defina o Backlog**:
   ```
   Número de Itens (Backlog): 50
   ```

5. **Configure Parâmetros Adicionais** (opcional):
   - **Custo Médio Histórico**: Se você tem dados reais de custos passados
   - **Tamanho da Equipe**: Número de pessoas
   - **Throughput Histórico**: Amostras de throughput (para contexto)

6. **Configure o Número de Simulações**:
   ```
   Número de Simulações: 10000
   ```

7. **Execute a Análise**:
   - Clique em **"Executar Análise de Custos"**
   - Aguarde o processamento (2-5 segundos)

**Interpretando os Resultados**:

```
📊 Análise de Custos por Demanda (PERT-Beta)

Distribuição de Custos:
P50 (Mediana):      R$ 52,500.00  (50% de chance)
P85 (Recomendado):  R$ 62,000.00  (85% de chance) ✅
P95 (Conservador):  R$ 71,000.00  (95% de chance)

Custo Médio por Item: R$ 1,050.00
Desvio Padrão: R$ 250.00

Backlog Total: 50 items

Parâmetros PERT-Beta:
- Alpha (α): 2.5
- Beta (β): 2.5
- Média PERT: R$ 1,000.00
- Desvio PERT: R$ 250.00

📋 Métricas de Risco:
- Probabilidade de exceder R$ 70,000: 8%
- Probabilidade de ficar abaixo de R$ 50,000: 42%
- Range de Confiança (80%): R$ 48,000 - R$ 65,000
```

**Gráficos Gerados**:
- **Histograma de Custos**: Distribuição de probabilidade dos custos totais
- **Curva Cumulativa**: Probabilidade acumulada de custos
- **Box Plot**: Visualização de quartis e outliers

**Métricas de Risco**:
- **Coefficient of Variation (CV)**: Mede a variabilidade relativa
  - CV < 15%: Baixo risco
  - CV 15-30%: Risco moderado
  - CV > 30%: Alto risco

- **Risk Score**: Pontuação combinada baseada em variabilidade e desvio

**Dica**: Se o CV for muito alto (>30%), considere refinar suas estimativas ou coletar mais dados históricos.

---

### 💡 Comparando Custo por Esforço vs. Custo por Demanda

| Aspecto | Custo por Pessoa-Semana | Custo Médio da Demanda |
|---------|--------------------------|------------------------|
| **Base de Cálculo** | Esforço (pessoa-semanas) | Custo por item × Backlog |
| **Quando usar** | Projetos com equipe dedicada | Projetos com custos variáveis por item |
| **Precisão** | Depende de estimativa de esforço | Depende de histórico de custos |
| **Melhor para** | Projetos internos, equipes fixas | Projetos terceirizados, desenvolvimento ágil |

**Exemplo Prático**:

**Cenário**: Desenvolvimento de 50 features

**Opção 1 - Custo por Pessoa-Semana**:
- Esforço estimado (P85): 55 pessoa-semanas
- Custo por pessoa-semana: R$ 5.000
- **Custo Total**: R$ 275.000

**Opção 2 - Custo Médio da Demanda**:
- Backlog: 50 features
- Custo médio por feature (P85): R$ 5.200
- **Custo Total**: R$ 260.000

**Qual usar?**
- Se você tem uma **equipe fixa dedicada**, use Custo por Pessoa-Semana
- Se você paga **por entrega/item**, use Custo Médio da Demanda
- Para **máxima robustez**, execute ambas e compare

---

## 📅 Análise de Deadline

**O que faz**: Análise completa de viabilidade de prazo, combinando Monte Carlo e Machine Learning para responder:
- ✅ É possível cumprir o deadline?
- 📊 Quanto do escopo será completado até o deadline?
- 📅 Quando o backlog completo será finalizado?

**Como usar**:

1. **Acesse a aba "Análise de Deadline"** ou navegue para `/deadline-analysis`

2. **Preencha os Dados Históricos**:
   ```
   Throughput Semanal: 5, 6, 7, 4, 8, 6, 5, 7, 6, 8
   ```

3. **Preencha os Dados do Projeto**:
   ```
   Backlog Total: 50 items
   Data de Início: 01/10/2025
   Deadline: 01/12/2025
   ```

4. **Configure Parâmetros Avançados** (opcional):
   - Tamanho da Equipe: 5 pessoas
   - Contribuidores Mínimos: 3
   - Contribuidores Máximos: 5
   - Curva-S: 0 (sem rampa)
   - Lead Times: [opcional]
   - Split Rates: [opcional]
   - Custo por Pessoa-Semana: R$ 5.000

5. **Execute a Análise**:
   - Clique em **"Análise de Deadline"**
   - Aguarde o processamento (5-10 segundos)

**Interpretando os Resultados**:

```
📅 Análise de Deadline - Visão Geral

Deadline: 01/12/2025
Data de Início: 01/10/2025
Semanas até Deadline: 8.7 semanas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎲 MONTE CARLO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Semanas Projetadas:
- P50 (Mediana):      8.2 semanas ✅
- P85 (Recomendado):  9.8 semanas ⚠️
- P95 (Conservador):  11.5 semanas ❌

Pode cumprir o deadline? ⚠️ PARCIALMENTE

Conclusão do Backlog (P85):
- Data Estimada: 10/12/2025
- Atraso Projetado: 1.1 semanas

Escopo até o Deadline (P85):
- Items Completados: 42 de 50
- Percentual de Conclusão: 84%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MACHINE LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Semanas Projetadas:
- P50 (Mediana):      8.0 semanas ✅
- P85 (Recomendado):  9.5 semanas ⚠️
- P95 (Conservador):  11.2 semanas ❌

Pode cumprir o deadline? ⚠️ PARCIALMENTE

Risk Assessment: LOW ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤝 CONSENSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Ambos os métodos concordam

Recomendação:
Ambos os métodos indicam que há risco moderado de não cumprir
100% do escopo no deadline. Considere:

1. Reduzir escopo para 42 items (viável com 85% de confiança)
2. Estender deadline em ~1 semana
3. Aumentar a equipe temporariamente

Diferença entre métodos: 0.3 semanas (3%)
```

**Visualizações Disponíveis**:
1. **Gráfico de Viabilidade**: Compara semanas disponíveis vs. projetadas
2. **Distribuição de Conclusão**: Probabilidade de terminar em cada semana
3. **Burn-down Projetado**: Trajetória esperada de conclusão do backlog
4. **Comparação ML vs MC**: Lado a lado das previsões

**Cenários de Resposta**:

### ✅ Cenário 1: Deadline Viável
```
Pode cumprir deadline? ✅ SIM

Monte Carlo P85: 7.5 semanas
Deadline: 8.7 semanas
Margem de Segurança: 1.2 semanas (14%)

Recomendação:
✓ Deadline viável com 85% de confiança
✓ Há margem para imprevistos
✓ Prossiga com o planejamento atual
```

### ⚠️ Cenário 2: Deadline Parcialmente Viável
```
Pode cumprir deadline? ⚠️ PARCIALMENTE

Monte Carlo P85: 9.8 semanas
Deadline: 8.7 semanas
Déficit: 1.1 semanas (11%)

Escopo viável no deadline (P85): 84%

Recomendação:
⚠️ Risco moderado de atraso
⚠️ Considere reduzir escopo ou estender prazo
⚠️ Alternativa: Priorize 84% do backlog mais crítico
```

### ❌ Cenário 3: Deadline Inviável
```
Pode cumprir deadline? ❌ NÃO

Monte Carlo P85: 12.5 semanas
Deadline: 8.7 semanas
Déficit: 3.8 semanas (44%)

Escopo viável no deadline (P85): 64%

Recomendação:
❌ Alta probabilidade de não cumprir o deadline
❌ Ações necessárias:
   1. Renegociar prazo (sugestão: +4 semanas)
   2. Reduzir escopo significativamente (para ~32 items)
   3. Aumentar equipe (considerar +2 pessoas)
```

**Análise de Custos Integrada**:

Se você configurou o custo por pessoa-semana, verá:

```
💰 Análise de Custos do Projeto

Monte Carlo (P85):
- Esforço: 49.0 pessoa-semanas
- Custo Total: R$ 245,000.00

Machine Learning (P85):
- Esforço: 47.5 pessoa-semanas
- Custo Total: R$ 237,500.00

Taxas de Referência:
- Por Pessoa-Semana: R$ 5,000.00
- Por Pessoa-Mês: R$ 21,650.00
- Por Pessoa-Ano: R$ 260,000.00
```

**Respostas a Perguntas-Chave**:

**Pergunta 1: "Quando o projeto termina?"**
```
📅 Data de Conclusão Projetada

P50 (50% confiança):  25/11/2025
P85 (85% confiança):  10/12/2025  ← Recomendado
P95 (95% confiança):  20/12/2025
```

**Pergunta 2: "Quantos items consigo entregar até o deadline?"**
```
📦 Entregas até o Deadline (01/12/2025)

P50 (50% confiança):  45 items (90%)
P85 (85% confiança):  42 items (84%)  ← Recomendado
P95 (95% confiança):  38 items (76%)
```

**Pergunta 3: "Preciso aumentar a equipe?"**
```
👥 Análise de Equipe

Equipe Atual: 5 pessoas
Semanas Disponíveis: 8.7
Semanas Necessárias (P85): 9.8

Cenário 1 - Manter equipe:
- Resultado: Atraso de 1.1 semanas

Cenário 2 - Aumentar equipe para 6 pessoas:
- Semanas Projetadas: ~8.2 semanas
- Resultado: ✅ Cumpre deadline com margem
- Custo adicional: R$ 41,000.00
```

---

## ❓ Perguntas Frequentes

### P1: Quantos dados históricos eu preciso?

**Resposta**:
- **Mínimo absoluto**: 3-5 amostras de throughput
- **Recomendado para Monte Carlo**: 8-12 amostras
- **Necessário para Machine Learning**: 8+ amostras (ideal 12+)

**Por quê?**
- Com poucos dados, as previsões têm baixa confiabilidade
- Com 12+ semanas, você captura ciclos e sazonalidades
- Quanto mais dados, mais precisas as previsões

---

### P2: Como coletar throughput se minha equipe não trabalha em sprints fixos?

**Resposta**:
1. Defina um período fixo (ex: semanas corridas, não sprints)
2. Conte itens **finalizados** (done) em cada período
3. Use a mesma definição de "done" consistentemente
4. Não importa quando começaram, apenas quando terminaram

**Exemplo**:
```
Semana 1 (01-07 Out): 5 items finalizados
Semana 2 (08-14 Out): 7 items finalizados
Semana 3 (15-21 Out): 4 items finalizados
...
```

---

### P3: Meus dados são muito voláteis. O que fazer?

**Resposta**:
1. **Prefira Monte Carlo**: Lida melhor com volatilidade
2. **Evite ML**: Pode produzir previsões instáveis
3. **Colete mais dados**: 16+ semanas ajudam a estabilizar
4. **Analise causas**: Investigar por que há volatilidade
   - WIP muito alto?
   - Items de tamanhos muito diferentes?
   - Dependências externas?

**Indicadores de volatilidade**:
- Coefficient of Variation (CV) > 30%
- Risk Assessment = HIGH no ML
- Grande diferença entre P50 e P95 (>100%)

---

### P4: Quando usar percentis diferentes (P50, P85, P95)?

**Resposta**:

| Percentil | Quando usar | Contexto |
|-----------|-------------|----------|
| **P50** | Previsões otimistas | Planejamento interno, baixo risco |
| **P85** | Planejamento padrão ✅ | Commitments com stakeholders |
| **P95** | Planejamento conservador | Projetos críticos, contratos fixos |

**Regra prática**:
- Use **P85** como padrão
- Use **P95** se o custo de atraso for muito alto
- Use **P50** apenas para discussões internas

---

### P5: Como interpretar "Risk Assessment: HIGH"?

**Resposta**:

**HIGH** significa que os dados históricos são muito voláteis/instáveis para previsões ML confiáveis.

**Possíveis causas**:
- Throughput varia muito (ex: 2, 10, 3, 15, 1 items/semana)
- Poucos dados históricos (<10 semanas)
- Mudanças recentes no processo/equipe
- Items de tamanhos muito diferentes

**Ações recomendadas**:
1. ✅ Use **Monte Carlo** em vez de ML
2. ✅ Colete mais dados (16+ semanas)
3. ✅ Padronize tamanho dos items
4. ✅ Estabilize WIP (Work in Progress)
5. ⚠️ Comunique incerteza aos stakeholders

---

### P6: Posso usar o Flow Forecaster para estimativas ágeis de longo prazo?

**Resposta**: Sim, mas com cuidados:

**✅ Funciona bem para**:
- Roadmaps de 3-6 meses
- Releases com múltiplas funcionalidades
- OKRs trimestrais

**⚠️ Limitações**:
- Previsões >6 meses têm baixa confiabilidade
- Assume que processo permanece estável
- Não captura mudanças de equipe/tecnologia

**Dica**:
- Para previsões >3 meses, revise a cada mês
- Atualize com novos dados históricos
- Considere usar ranges amplos (P50-P95)

---

### P7: Como explicar previsões probabilísticas para stakeholders não-técnicos?

**Resposta**: Use analogias do dia-a-dia:

**Analogia da Previsão do Tempo**:
```
"Assim como a previsão do tempo diz 'há 80% de chance de
chuva', nosso P85 diz 'há 85% de chance de terminar em
10 semanas ou menos'. Não é uma promessa, é uma
probabilidade baseada em dados históricos."
```

**Analogia de Viagem**:
```
"Imagine que você vai dirigir de São Paulo a Rio.
O GPS diz '5 horas'. Mas pode ser:
- P50: 5 horas (se não tiver trânsito)
- P85: 6 horas (considerando trânsito normal)
- P95: 7 horas (se der tudo errado)

Nosso P85 é como planejar '6 horas' - realista e seguro."
```

**Visualização Simples**:
```
Chances de entregar em cada prazo:

8 semanas:  ███████░░░░░░░░  50% (P50)
10 semanas: ███████████████░  85% (P85) ← Recomendado
12 semanas: █████████████████ 95% (P95)
```

---

### P8: O que fazer se Monte Carlo e ML divergirem muito?

**Resposta**:

**Divergência < 10%**: Normal, use qualquer estimativa.

**Divergência 10-20%**:
- Use a mais conservadora (maior)
- Investigue qual método é mais apropriado para seus dados
- Comunique incerteza ao stakeholder

**Divergência > 20%**:
```
⚠️ Divergência Significativa Detectada

Monte Carlo: 10 semanas
ML: 15 semanas
Diferença: 50%

Possíveis causas:
1. Dados insuficientes (colete mais)
2. Mudança recente no processo
3. Tendência forte (crescimento/queda)
4. Alta volatilidade

Recomendação:
❌ NÃO use nenhuma estimativa ainda
✅ Colete mais 4-6 semanas de dados
✅ Investigue mudanças recentes
✅ Revise definições (done, item size)
```

---

## 💡 Dicas e Boas Práticas

### 📊 Coleta de Dados

**✅ Faça**:
- Mantenha consistência na definição de "done"
- Use períodos fixos (ex: semanas corridas)
- Registre dados semanalmente
- Documente mudanças significativas (férias, novos membros, etc.)
- Use items de tamanho similar

**❌ Evite**:
- Misturar tipos de items (stories com bugs)
- Pular semanas sem dados
- Alterar definições no meio do caminho
- Incluir items parcialmente completos
- Comparar throughputs de equipes diferentes

---

### 🎯 Planejamento

**Use P85 como padrão**:
- 85% de confiança é o equilíbrio ideal entre otimismo e conservadorismo
- Stakeholders geralmente aceitam "15% de risco" como razoável
- Reserve P95 apenas para contextos críticos

**Comunique incertezas**:
- Não diga: "O projeto termina em 10 semanas"
- Diga: "Há 85% de chance de terminar em 10 semanas ou menos"
- Sempre apresente ranges (P50-P95)

**Revise frequentemente**:
- Atualize previsões a cada 2-4 semanas
- Incorpore novos dados históricos
- Recalcule se mudanças significativas ocorrerem

---

### 🔍 Validação de Previsões

**Backtesting**:
1. Execute uma previsão com dados até N semanas atrás
2. Compare com o que realmente aconteceu
3. Ajuste parâmetros se necessário

**Calibração**:
- Se P85 consistentemente superestima, considere usar P75-P80
- Se P85 consistentemente subestima, considere usar P90-P95
- Documente desvios e aprenda com eles

---

### 📈 Machine Learning

**Quando confiar no ML**:
- ✅ Risk Assessment = LOW ou MEDIUM
- ✅ Dados estáveis e suficientes (12+ semanas)
- ✅ Validação walk-forward mostra boa precisão
- ✅ Não houve mudanças recentes no processo

**Quando desconfiar do ML**:
- ❌ Risk Assessment = HIGH
- ❌ Poucos dados (<10 semanas)
- ❌ Grande volatilidade (CV > 40%)
- ❌ Mudanças recentes (nova equipe, nova tecnologia)

---

### 💰 Análise de Custos

**Defina custo realista por pessoa-semana**:
```
Salário bruto mensal: R$ 10,000
+ Encargos (80%):     R$ 8,000
+ Overhead (30%):     R$ 3,000
+ Benefícios:         R$ 1,000
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total mensal:         R$ 22,000
÷ 4.33 semanas:       R$ 5,081/semana
```

**Use estimativas PERT-Beta realistas**:
- **Otimista**: Melhor cenário razoável (não ideal impossível)
- **Mais Provável**: Baseado em experiência similar
- **Pessimista**: Pior cenário razoável (não apocalipse)

**Valide retroativamente**:
- Compare custos estimados vs. reais em projetos passados
- Ajuste parâmetros baseado em desvios históricos
- Documente premissas e contexto

---

## 🔧 Solução de Problemas

### Problema 1: "Resultados parecem irrealistas"

**Sintomas**:
- Previsões muito otimistas ou muito pessimistas
- Grande diferença entre métodos (>50%)
- Percentis muito próximos ou muito distantes

**Soluções**:
1. **Verifique os dados de entrada**:
   - Throughput está no formato correto? (números separados por vírgula)
   - Backlog está correto?
   - Datas no formato DD/MM/YYYY?

2. **Valide qualidade dos dados**:
   - Há outliers extremos? (ex: 1, 5, 6, 7, 50, 6)
   - Dados são consistentes na granularidade?
   - Definição de "done" é clara?

3. **Revise parâmetros avançados**:
   - Curva-S muito alta pode distorcer resultados
   - Split rates devem usar multiplicadores, não porcentagens
   - Contribuidores min/max devem ser realistas

---

### Problema 2: "Machine Learning não está disponível"

**Sintomas**:
- Mensagem: "Need at least 8 historical throughput samples for ML forecasting"
- Resultados ML não aparecem

**Soluções**:
1. **Colete mais dados**: ML requer mínimo 8 amostras
2. **Use Monte Carlo**: Funciona com apenas 3-5 amostras
3. **Aguarde**: Colete dados por mais 2-4 semanas antes de usar ML

---

### Problema 3: "Risk Assessment sempre HIGH"

**Sintomas**:
- ML sempre retorna Risk Assessment = HIGH
- Previsões ML divergem muito de Monte Carlo

**Causas comuns**:
1. **Alta volatilidade nos dados**: Throughput varia muito semana a semana
2. **Poucos dados**: <10 semanas de histórico
3. **Items de tamanhos muito diferentes**: Alguns levam 1 dia, outros 2 semanas
4. **WIP descontrolado**: Muitos items em progresso simultaneamente

**Soluções**:
1. **Curto prazo**: Use Monte Carlo em vez de ML
2. **Médio prazo**:
   - Padronize tamanho dos items (use story points, splits)
   - Limite WIP (ex: máximo 2-3 items por pessoa)
   - Colete mais dados (16+ semanas)
3. **Longo prazo**:
   - Melhore processo (Kanban, Scrum mais disciplinado)
   - Treine equipe em quebra de items
   - Estabeleça Definition of Ready/Done claras

---

### Problema 4: "Simulação demora muito"

**Sintomas**:
- Análise leva >30 segundos
- Timeout errors
- Navegador trava

**Soluções**:
1. **Reduza número de simulações**:
   - Padrão: 10,000 (recomendado)
   - Se muito lento: use 5,000 (ainda confiável)
   - Mínimo: 1,000 (apenas para testes)

2. **Simplifique parâmetros**:
   - Remova riscos desnecessários
   - Desabilite curva-S se não aplicável
   - Use menos dados históricos (últimas 20 semanas)

3. **Verifique navegador**:
   - Use Chrome ou Firefox (mais rápidos para JavaScript)
   - Feche outras abas
   - Limpe cache

---

### Problema 5: "Gráficos não aparecem"

**Sintomas**:
- Resultados numéricos aparecem, mas gráficos não
- Erro de "Chart is not defined"

**Soluções**:
1. **Verifique conexão com internet**: Bibliotecas de gráficos são carregadas via CDN
2. **Desabilite bloqueadores de anúncios**: Podem bloquear CDNs
3. **Atualize página**: Ctrl+F5 (força recarga)
4. **Use navegador moderno**: Chrome, Firefox, Edge atualizados

---

## 📖 Glossário

### A

**Alfa (α) - PERT-Beta**
Parâmetro da distribuição Beta que controla a forma da curva. Calculado automaticamente a partir das estimativas otimista, mais provável e pessimista.

**Autocorrelação**
Medida de quanto os valores de throughput de uma semana influenciam a semana seguinte. Alta autocorrelação indica tendências.

### B

**Backlog**
Conjunto de itens pendentes que precisam ser completados. Deve estar no mesmo nível de granularidade do throughput.

**Beta (β) - PERT-Beta**
Parâmetro da distribuição Beta complementar ao alfa. Juntos definem a forma da curva de probabilidade.

**Burn-down**
Gráfico que mostra a evolução da conclusão do backlog ao longo do tempo.

### C

**Coefficient of Variation (CV)**
Medida de variabilidade relativa. CV = (desvio padrão / média) × 100%. Indica instabilidade dos dados.

**Curva-S**
Padrão de produtividade onde a equipe começa lenta (rampa de aprendizado), acelera, e depois desacelera no final.

### D

**Deadline**
Data limite para conclusão do projeto ou release.

**Distribuição de Probabilidade**
Função matemática que descreve a probabilidade de diferentes resultados. Ex: distribuição normal, Beta, etc.

### E

**Ensemble Forecasting**
Técnica de ML que combina previsões de múltiplos modelos para maior precisão e robustez.

**Esforço (pessoa-semanas)**
Quantidade de trabalho medida em semanas × número de pessoas. Ex: 5 pessoas × 10 semanas = 50 pessoa-semanas.

### F

**Forecast**
Previsão baseada em dados históricos e modelos estatísticos/ML.

### G

**Gradient Boosting**
Algoritmo de ML que constrói modelos sequencialmente, cada um corrigindo erros do anterior.

### H

**Histograma**
Gráfico de barras que mostra a distribuição de frequência dos resultados simulados.

**Hist Gradient Boosting**
Variante do Gradient Boosting otimizada para grandes datasets e quantile regression.

### I

**Intervalo de Confiança**
Range de valores dentro do qual esperamos que o resultado real esteja com certa probabilidade. Ex: P10-P90.

### K

**K-Fold Cross-Validation**
Técnica de validação de modelos ML que divide dados em K partes, treina em K-1 e testa na parte restante, rotacionando.

### L

**Lead Time**
Tempo que um item leva desde o início do trabalho até a conclusão.

### M

**Machine Learning (ML)**
Técnicas computacionais que aprendem padrões dos dados para fazer previsões.

**Monte Carlo**
Método estatístico que usa amostragem aleatória repetida para simular milhares de cenários possíveis.

### O

**Otimista (a)**
Estimativa de melhor cenário razoável na técnica PERT-Beta.

**Overhead**
Custos indiretos (infraestrutura, gestão, ferramentas, etc.) incluídos no custo por pessoa-semana.

### P

**P50 (Percentil 50 / Mediana)**
Valor onde 50% dos cenários simulados terminam antes deste ponto. Representa o cenário "típico".

**P85 (Percentil 85)**
Valor onde 85% dos cenários simulados terminam antes deste ponto. Recomendado para planejamento padrão.

**P95 (Percentil 95)**
Valor onde 95% dos cenários simulados terminam antes deste ponto. Usado para planejamento conservador.

**PERT (Program Evaluation and Review Technique)**
Técnica de estimativa de três pontos (otimista, mais provável, pessimista) que usa distribuição Beta.

**Pessoa-Semana**
Unidade de esforço: uma pessoa trabalhando em tempo integral por uma semana.

**Pessimista (b)**
Estimativa de pior cenário razoável na técnica PERT-Beta.

### Q

**Quantile Regression**
Técnica de ML que prevê percentis específicos (P10, P90) em vez de apenas a média.

### R

**Random Forest**
Algoritmo de ML que combina múltiplas árvores de decisão para previsões robustas.

**Risk Assessment**
Avaliação automática da confiabilidade de previsões ML baseada na volatilidade dos dados (LOW/MEDIUM/HIGH).

### S

**Split Rate**
Taxa de divisão de items. Formato: multiplicador (ex: 1.2 = item aumenta 20%).

**Simulação**
Processo de gerar milhares de cenários possíveis para análise probabilística.

### T

**Throughput**
Vazão: número de items completados por período de tempo (ex: items/semana).

**Time Series**
Série temporal: dados coletados em intervalos regulares ao longo do tempo.

### W

**Walk-Forward Validation**
Técnica de validação que simula previsões futuras usando dados históricos, movendo-se passo a passo no tempo.

**WIP (Work in Progress)**
Trabalho em andamento: número de items sendo trabalhados simultaneamente mas ainda não finalizados.

### X

**XGBoost (eXtreme Gradient Boosting)**
Implementação otimizada de Gradient Boosting conhecida por alta precisão e velocidade.

---

## 📞 Suporte e Recursos

### 🌐 Links Úteis

- **Aplicação Web**: https://flow-forecaster.fly.dev/
- **Documentação Técnica**: Consulte `README_ADVANCED.md` no repositório
- **Guia de Parâmetros**: Consulte `PARAMETERS_GUIDE.md`
- **Guia de Deploy**: Consulte `FLY_DEPLOY.md`

### 📧 Contato

Para questões, sugestões ou problemas:
- Abra uma issue no repositório GitHub
- Consulte a documentação técnica complementar
- Revise este manual e as seções de FAQ

### 🎓 Aprenda Mais

**Conceitos Estatísticos**:
- [Simulações Monte Carlo (Wikipedia)](https://pt.wikipedia.org/wiki/M%C3%A9todo_de_Monte_Carlo)
- [Distribuição Beta (Wikipedia)](https://pt.wikipedia.org/wiki/Distribui%C3%A7%C3%A3o_beta)
- [Análise PERT (Wikipedia)](https://pt.wikipedia.org/wiki/PERT)

**Machine Learning**:
- [Random Forest (scikit-learn)](https://scikit-learn.org/stable/modules/ensemble.html#forest)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Gradient Boosting (scikit-learn)](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)

**Gestão de fluxo**:
- [Kanban Guide](https://all.kanban.plus/en/content/kanbanplus/)
- [Agile Forecasting (Troy Magennis)](https://github.com/FocusedObjective/FocusedObjective.Resources)
- [Aspercom ](https://www.aspercom.com.br)

---

## 📄 Notas da Versão

**Versão 2.0** (Outubro 2025)
- ✅ Análise de Custos por Pessoa-Semana com PERT-Beta
- ✅ Análise de Custos Médio da Demanda
- ✅ Histogramas de distribuição PERT-Beta
- ✅ Análise de Deadline integrada com custos
- ✅ Consenso entre Monte Carlo e Machine Learning
- ✅ Interface aprimorada com separação clara de funcionalidades

**Versão 1.5** (Setembro 2025)
- ✅ Machine Learning (Random Forest, XGBoost, Gradient Boosting)
- ✅ K-Fold Cross-Validation
- ✅ Walk-Forward Validation
- ✅ Risk Assessment automático

**Versão 1.0** (Agosto 2025)
- ✅ Simulações Monte Carlo básicas
- ✅ Análise de throughput e lead-time
- ✅ Modelagem de riscos
- ✅ Curva-S de produtividade

---

**Bom uso do Flow Forecaster! 🚀**

*Para dúvidas ou sugestões de melhoria deste manual, consulte a documentação técnica ou abra uma issue no repositório.*
