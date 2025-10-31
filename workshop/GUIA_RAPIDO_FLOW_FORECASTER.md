# 🚀 GUIA RÁPIDO: FLOW FORECASTER
## Workshop Monte Carlo - PMI-DF Summit 2025

**Acesso**: https://flow-forecaster.fly.dev/

---

## ⚡ INÍCIO RÁPIDO (5 minutos)

### 1️⃣ SIMULAÇÃO MONTE CARLO BÁSICA

**Onde**: Aba "Simulação Monte Carlo" (primeira aba)

**Passo-a-passo**:

1. **Preencha os dados básicos**:
   ```
   Nome do Projeto: [nome do seu cenário]
   Número de Tarefas (Backlog): [número do seu cenário]
   Número de Simulações: 10000 (deixar padrão)
   ```

2. **Insira o Throughput Histórico**:
   ```
   Exemplo: 6, 8, 5, 9, 7, 6, 10, 7, 8, 6

   ⚠️ FORMATO: números separados por VÍRGULA
   ```

3. **Configure a Equipe** (seção "Parâmetros da Equipe"):
   ```
   Tamanho da Equipe: [número de pessoas do cenário]
   Contributors (min): [mesmo valor ou menor]
   Contributors (max): [mesmo valor da equipe]
   Curva-S: 0 (deixar zero para simplificar)
   ```

4. **Clique em "Executar Simulação"**

5. **Interprete os Resultados** (rolagem para baixo):
   ```
   📊 Resultados Probabilísticos:

   P50 (Mediana):      X semanas    ← 50% de chance
   P85 (Recomendado):  Y semanas    ← 85% de chance ⭐ USE ESTE!
   P95 (Conservador):  Z semanas    ← 95% de chance
   ```

---

### 2️⃣ ADICIONAR RISCOS

**Onde**: Na mesma tela da Simulação Monte Carlo, rolar para "Gestão de Riscos"

**Passo-a-passo**:

1. **Clique em "➕ Adicionar Risco"**

2. **Preencha os dados do risco**:
   ```
   Nome/Descrição: [ex: "Atraso na homologação"]

   Probabilidade (%): [ex: 40]
   ⚠️ Use valor de 0 a 100 (não decimal)

   Impacto (Triangular):
   - Otimista (Low):      [menor impacto, ex: 5]
   - Mais Provável (Med): [impacto típico, ex: 8]
   - Pessimista (High):   [maior impacto, ex: 12]

   ⚠️ Use NÚMERO DE TAREFAS/ITENS, não semanas!
   ```

3. **Adicione mais riscos** se necessário (botão "➕ Adicionar Risco" novamente)

4. **Execute novamente** (botão "Executar Simulação")

5. **Compare** os resultados SEM riscos vs COM riscos:
   - O P85 aumentou quanto?
   - Qual risco teve mais impacto?

---

### 3️⃣ ANÁLISE DE DEADLINE

**Onde**: Aba "Análise de Deadline" (quarta aba)

**Passo-a-passo**:

1. **Preencha os dados**:
   ```
   Throughput Semanal: [mesmo de antes, com vírgulas]
   Backlog Total: [número de itens]

   Data de Início: DD/MM/YYYY
   Exemplo: 01/11/2025

   Deadline: DD/MM/YYYY
   Exemplo: 31/03/2026

   Tamanho da Equipe: [número de pessoas]
   ```

2. **Clique em "🎯 Análise de Deadline"**

3. **Interprete os Resultados**:
   ```
   Pode cumprir deadline? ✅ / ⚠️ / ❌

   Semanas até Deadline: [X]
   Semanas Projetadas (P85): [Y]

   Escopo até Deadline (P85): [Z]%

   ✅ SIM: Y <= X (viável!)
   ⚠️ PARCIAL: Y ligeiramente > X (ajustes necessários)
   ❌ NÃO: Y muito > X (não viável sem mudanças)
   ```

---

### 4️⃣ ANÁLISE DE CUSTOS

**Onde**: Aba "Análise de Custos" (terceira aba)

**Passo-a-passo**:

1. **Role até "💰 Custo por Pessoa-Semana"**

2. **Preencha**:
   ```
   Custo por Pessoa-Semana (R$): [ex: 5500]
   ```

3. **Execute a simulação Monte Carlo ANTES** (na aba 1)

4. **Volte para Análise de Custos** e clique em:
   ```
   "💰 Calcular Custos por Esforço"
   ```

5. **Veja os resultados**:
   ```
   P50 (Mediana):      R$ X
   P85 (Recomendado):  R$ Y  ← USE ESTE!
   P95 (Conservador):  R$ Z
   ```

---

## 🎯 CHECKLIST DO EXERCÍCIO

Durante os 25 minutos, completem:

- [ ] **Simulação básica** (sem riscos)
  - Anotar P50, P85, P95

- [ ] **Adicionar riscos** do cenário
  - Executar novamente
  - Comparar com resultado anterior

- [ ] **Análise de Deadline**
  - Verificar viabilidade
  - Anotar % de escopo viável

- [ ] **Análise de Custos**
  - Calcular custo total (P85)
  - Anotar para apresentação

- [ ] **Discussão em grupo** (5-8 min)
  - O que os números dizem?
  - Qual a recomendação?
  - GO / AJUSTAR / NO-GO?

---

## 🆘 PROBLEMAS COMUNS E SOLUÇÕES

### ❌ "Erro ao executar simulação"
**Causa**: Formato incorreto do throughput
**Solução**: Use números separados por VÍRGULA (não ponto-e-vírgula, não espaço)
```
✅ Correto: 5, 6, 7, 8, 9
❌ Errado: 5; 6; 7; 8; 9
❌ Errado: 5 6 7 8 9
```

### ❌ "Resultados parecem estranhos"
**Causa 1**: Throughput muito baixo vs backlog muito alto
**Solução**: Verifique se os números estão corretos (não inverteu?)

**Causa 2**: Riscos com impacto em SEMANAS (deveria ser em TAREFAS)
**Solução**: Riscos devem ter impacto em NÚMERO DE ITENS, não semanas!

### ❌ "Página demora a carregar"
**Causa**: Internet lenta ou muitos usuários simultâneos
**Solução**: Aguarde 10-15 segundos. Se travar, recarregue a página (F5)

### ❌ "Não consigo adicionar riscos"
**Causa**: Scroll não está na posição correta
**Solução**: Role a página para baixo até ver "Gestão de Riscos"

---

## 💡 DICAS PARA O EXERCÍCIO

### ✅ Divisão de Tarefas no Grupo:

1. **1 pessoa no computador** (operador)
   - Digita os dados
   - Executa as simulações
   - Navega pelas abas

2. **1 relator** (anotações)
   - Anota todos os resultados
   - Prepara apresentação de 1min30seg
   - Organiza conclusões

3. **3 analistas** (discussão)
   - Interpretam os números
   - Discutem recomendações
   - Validam com o operador

### ✅ Gestão do Tempo:

- **00:00 - 00:05** → Leitura do cenário e divisão de papéis
- **00:05 - 00:12** → Simulação básica + riscos
- **00:12 - 00:18** → Análise de deadline e custos
- **00:18 - 00:25** → Discussão e conclusões
- **00:25 - 00:33** → Preparação da apresentação

### ✅ Foco na Apresentação:

Preparem respostas para:
1. "Qual o P85?" (prazo e custo)
2. "Cumpre o deadline?"
3. "Qual sua recomendação?"
4. "Por quê?"

---

## 📊 INTERPRETANDO OS NÚMEROS

### P50 vs P85 vs P95:

```
P50 = 10 semanas → 50% de chance (otimista demais!)
P85 = 13 semanas → 85% de chance (RECOMENDADO para commitments)
P95 = 15 semanas → 95% de chance (conservador, para alto risco)
```

**Regra prática**: Use P85 para comprometimentos com stakeholders!

### Viabilidade do Deadline:

```
✅ VIÁVEL: P85 <= Deadline (há margem de segurança)
⚠️ PARCIAL: P85 ligeiramente > Deadline (risco moderado)
❌ INVIÁVEL: P85 muito > Deadline (alta chance de atraso)
```

### Impacto dos Riscos:

```
Se P85 aumentar:
- Menos de 10%: Risco baixo, gerenciável
- 10-30%: Risco médio, atenção necessária
- Mais de 30%: Risco alto, mitigação urgente!
```

---

## 🎯 OBJETIVO DA APRESENTAÇÃO

**Não se preocupem em explorar TODAS as funcionalidades!**

O objetivo é:
1. ✅ Executar 1-2 simulações
2. ✅ Interpretar os resultados (P85)
3. ✅ Tomar uma decisão baseada em dados
4. ✅ Apresentar recomendação em 1min30seg

**Lembrem-se**: Vocês são CONSULTORES apresentando ao SPONSOR do projeto!

---

## 🆘 PRECISA DE AJUDA?

**Durante o exercício**:
- Levante a mão
- O facilitador está circulando pelos grupos
- Pergunte aos colegas de grupo também!

**Dúvidas sobre conceitos**:
- P50/P85/P95: Percentis de probabilidade
- Monte Carlo: Simulação de milhares de cenários
- Throughput: Itens completados por semana
- Backlog: Total de itens pendentes

---

## ✅ SUCESSO = DADOS > OPINIÕES

Ao final, vocês devem poder dizer:

❌ "Eu acho que dá para terminar em 15 semanas"

✅ "Com base em 10.000 simulações usando dados históricos, há 85% de chance de terminar em 17 semanas ou menos"

**Esta é a diferença entre ACHISMO e DECISÃO BASEADA EM DADOS!**

---

**BOA SORTE NO EXERCÍCIO! 🚀**

*Em caso de problemas técnicos críticos, o facilitador tem cenários alternativos prontos.*
