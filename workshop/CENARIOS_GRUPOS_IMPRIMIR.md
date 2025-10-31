# 📋 CENÁRIOS PARA EXERCÍCIO EM GRUPOS
## Workshop Monte Carlo - PMI-DF Summit 2025

**INSTRUÇÕES**: Imprimir 1 página por grupo (6 páginas no total)
**Formato sugerido**: Papel A4, fonte 14pt para facilitar leitura

---

# 🏗️ GRUPO 1 - PROJETO DE INFRAESTRUTURA CLOUD

## 📌 CONTEXTO
**Projeto**: Migração de datacenter on-premises para AWS
**Empresa**: Varejista de médio porte (200 colaboradores)
**Urgência**: Contrato do datacenter atual vence em 4 meses

## 📊 DADOS DO PROJETO

**Backlog Total**: 80 tarefas de migração

**Throughput Histórico** (últimas 10 semanas):
```
6, 8, 5, 9, 7, 6, 10, 7, 8, 6 tarefas/semana
```

**Equipe**: 5 pessoas (2 DevOps + 3 Infra)

**Deadline**: 15 semanas

**Custo por Pessoa-Semana**: R$ 5.500

## ⚠️ RISCOS IDENTIFICADOS

1. **Downtime não planejado durante migração**
   - Probabilidade: 25%
   - Impacto: 5 a 12 tarefas adicionais (mais provável: 8)

2. **Falha em testes de performance**
   - Probabilidade: 40%
   - Impacto: 8 a 20 tarefas adicionais (mais provável: 12)

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ O projeto pode ser concluído em 15 semanas com 85% de confiança (P85)?
2. ✅ Qual é o custo total projetado (P85)?
3. ✅ Os riscos comprometem significativamente o prazo?
4. ✅ Recomendação: GO / AJUSTAR / NO-GO?

## 🔧 PASSOS NO FLOW FORECASTER

1. Acessar: https://flow-forecaster.fly.dev/
2. Aba "Simulação Monte Carlo"
3. Inserir: Backlog, Throughput, Equipe
4. Adicionar Riscos (botão "Adicionar Risco")
5. Executar e analisar P85
6. Aba "Análise de Custos" → Calcular com R$ 5.500/pessoa-semana

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# 📱 GRUPO 2 - DESENVOLVIMENTO DE APP MOBILE

## 📌 CONTEXTO
**Projeto**: App de delivery para marketplace regional
**Empresa**: Startup de logística em crescimento
**Urgência**: Janela de mercado (competidores estão lançando apps similares)

## 📊 DADOS DO PROJETO

**Backlog Total**: 150 features

**Throughput Histórico** (últimas 12 semanas):
```
10, 12, 8, 14, 11, 9, 13, 10, 12, 11, 15, 10 features/semana
```

**Equipe**: 10 desenvolvedores (6 mobile + 2 backend + 2 QA)

**Deadline**: 18 semanas

**Custo por Pessoa-Semana**: R$ 4.800

## ⚠️ RISCOS IDENTIFICADOS

1. **Mudança de design pela diretoria**
   - Probabilidade: 70% (diretoria é indecisa!)
   - Impacto: 10 a 25 features adicionais (mais provável: 15)

2. **Integração com sistema de pagamento**
   - Probabilidade: 50%
   - Impacto: 8 a 18 features adicionais (mais provável: 12)

3. **Bugs críticos em produção (retrabalho)**
   - Probabilidade: 30%
   - Impacto: 5 a 12 features adicionais (mais provável: 8)

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ O deadline de 18 semanas é realista?
2. ✅ Quanto do escopo (% de features) será entregue no prazo?
3. ✅ Qual risco tem maior impacto? (analisar um de cada vez)
4. ✅ Se não cumprir prazo, qual a recomendação?
   - Aumentar equipe?
   - Reduzir escopo (MVP)?
   - Estender deadline?

## 🔧 PASSOS NO FLOW FORECASTER

1. Simulação básica (sem riscos)
2. Adicionar os 3 riscos e ver o impacto
3. Aba "Análise de Deadline" → Ver % de escopo viável
4. Usar aba "Machine Learning" para validação (12 amostras = OK)

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# 🏢 GRUPO 3 - TRANSFORMAÇÃO DIGITAL (IMPLANTAÇÃO DE PMO)

## 📌 CONTEXTO
**Projeto**: Implantação de Escritório de Projetos (PMO)
**Empresa**: Indústria tradicional (50 anos, cultura de "sempre foi assim")
**Urgência**: Pressão do board por profissionalização da gestão

## 📊 DADOS DO PROJETO

**Backlog Total**: 45 iniciativas (processos, templates, treinamentos, ferramentas)

**Throughput Histórico** (últimas 8 semanas):
```
4, 5, 3, 6, 5, 4, 7, 5 iniciativas/semana
```

**Equipe**: 3 pessoas (1 PMO Lead + 2 Analistas)

**Deadline**: 12 semanas

**Custo por Pessoa-Semana**: R$ 7.000 (equipe sênior)

## ⚠️ RISCOS IDENTIFICADOS

1. **Resistência cultural das áreas**
   - Probabilidade: 80% (cultura muito enraizada!)
   - Impacto: 5 a 15 iniciativas adicionais (mais provável: 10)
   - Exemplo: Refazer templates, treinamentos extras, reuniões de convencimento

2. **Falta de sponsor executivo forte**
   - Probabilidade: 40%
   - Impacto: 3 a 8 iniciativas adicionais (mais provável: 5)
   - Exemplo: Decisões travadas, escalações não funcionam

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ Com 80% de chance de resistência cultural, o prazo é viável?
2. ✅ Qual o custo total (P85) considerando equipe sênior?
3. ✅ Como comunicar alta incerteza ao board?
4. ✅ Seria melhor fazer uma fase piloto primeiro?

**ATENÇÃO**: Este é um cenário de **ALTA INCERTEZA**. Como vocês recomendariam abordar?

## 🔧 PASSOS NO FLOW FORECASTER

1. Executar simulação com throughput atual
2. Adicionar riscos (especialmente o de 80%!)
3. Comparar P50 vs P85 vs P95 (a diferença será grande!)
4. Análise de Deadline para ver viabilidade
5. **Discussão**: Se P95 for muito maior que deadline, qual a estratégia?

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# ⚖️ GRUPO 4 - PROJETO DE COMPLIANCE LGPD

## 📌 CONTEXTO
**Projeto**: Adequação à Lei Geral de Proteção de Dados
**Empresa**: E-commerce com 200 mil clientes cadastrados
**Urgência**: **CRÍTICA** - Prazo regulatório fixo! Multas por não conformidade.

## 📊 DADOS DO PROJETO

**Backlog Total**: 95 ações corretivas (mapeamento, processos, tech, docs)

**Throughput Histórico** (últimas 10 semanas):
```
7, 9, 6, 10, 8, 7, 11, 9, 8, 10 ações/semana
```

**Equipe**: 6 pessoas (2 Jurídico + 3 TI + 1 DPO)

**Deadline**: 16 semanas (**IMUTÁVEL** - prazo da ANPD)

**Custo por Pessoa-Semana**: R$ 6.500

## ⚠️ RISCOS IDENTIFICADOS

1. **Auditoria interna encontra novas não-conformidades**
   - Probabilidade: 60%
   - Impacto: 10 a 25 ações adicionais (mais provável: 15)

2. **Terceiros (fornecedores) não atendem no prazo**
   - Probabilidade: 50%
   - Impacto: 8 a 18 ações adicionais (mais provável: 12)

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ Qual a probabilidade REAL de cumprir o prazo regulatório?
2. ✅ O prazo de 16 semanas é suficiente com 85% de confiança?
3. ✅ Se não for viável, qual o **Plano B**?
   - Aumentar equipe? (em quanto?)
   - Priorizar ações críticas? (quais?)
   - Pedir extensão? (possível com órgão regulador?)

**ATENÇÃO**: Este é um cenário de **PRAZO FIXO**. Não dá para negociar!

## 🔧 PASSOS NO FLOW FORECASTER

1. Simulação Monte Carlo com os riscos
2. Análise de Deadline → Ver probabilidade de sucesso
3. Se P85 > 16 semanas, simular cenários:
   - **What-if 1**: E se aumentarmos equipe para 8 pessoas?
   - **What-if 2**: E se priorizarmos 70 ações mais críticas?
4. Calcular custo e apresentar trade-offs ao board

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# 🚀 GRUPO 5 - LANÇAMENTO DE PRODUTO (GO-TO-MARKET)

## 📌 CONTEXTO
**Projeto**: Lançamento de SaaS B2B para gestão de contratos
**Empresa**: Scale-up de software (Series A recém-captado)
**Urgência**: Burn rate alto, precisa começar a faturar!

## 📊 DADOS DO PROJETO

**Backlog Total**: 200 itens (marketing + vendas + tech + suporte)

**Throughput Histórico** (últimas 12 semanas):
```
15, 18, 12, 20, 16, 14, 22, 17, 19, 16, 21, 18 itens/semana
```

**Equipe**: 15 pessoas (5 dev + 3 marketing + 3 vendas + 2 CS + 2 produto)

**Deadline**: 25 semanas

**Custo por Pessoa-Semana**: R$ 5.200

## ⚠️ RISCOS IDENTIFICADOS

1. **Pivotar estratégia após feedback inicial de clientes**
   - Probabilidade: 50% (startup = incerteza!)
   - Impacto: 20 a 50 itens adicionais (mais provável: 30)

2. **Atraso no desenvolvimento de integrações**
   - Probabilidade: 40%
   - Impacto: 15 a 40 itens adicionais (mais provável: 25)

3. **Campanha de marketing precisa de ajustes**
   - Probabilidade: 60%
   - Impacto: 10 a 20 itens adicionais (mais provável: 15)

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ Com 200 itens, a capacidade da equipe é suficiente?
2. ✅ Qual o impacto real dos riscos? (testar cenário pessimista)
3. ✅ Custo total (P85)? Os investidores vão aprovar?
4. ✅ **Estratégia**: Melhor lançar MVP rápido e iterar, ou esperar o produto completo?

**INSIGHT**: 50% de chance de pivô muda TUDO! Como lidar com isso?

## 🔧 PASSOS NO FLOW FORECASTER

1. Simulação básica (200 itens)
2. Adicionar os 3 riscos
3. Usar Machine Learning para ver tendência (12 amostras = suficiente)
4. Comparar MC vs ML → Se divergirem muito, por quê?
5. Análise de Custos → Ver se cabe no budget de Series A
6. **Discussão**: MVP (100 itens) em 12 semanas vs Produto Completo (200 itens) em 25 semanas?

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# 💻 GRUPO 6 - MODERNIZAÇÃO DE SISTEMA LEGADO

## 📌 CONTEXTO
**Projeto**: Refactoring de monolito para microsserviços
**Empresa**: Banco regional (sistema com 15 anos de idade!)
**Urgência**: Sistema atual custa R$ 120k/mês em manutenção

## 📊 DADOS DO PROJETO

**Backlog Total**: 65 módulos para modernizar

**Throughput Histórico** (últimas 8 semanas):
```
5, 7, 4, 8, 6, 5, 9, 6 módulos/semana
```

**Equipe**: 7 desenvolvedores sêniores (salário alto!)

**Deadline**: 14 semanas

**Custo por Pessoa-Semana**: R$ 8.000 (equipe MUITO cara!)

## ⚠️ RISCOS IDENTIFICADOS

1. **Débito técnico maior que o esperado**
   - Probabilidade: 70% (código de 15 anos = surpresas!)
   - Impacto: 8 a 25 módulos adicionais (mais provável: 15)

2. **Testes de regressão encontram bugs críticos**
   - Probabilidade: 50%
   - Impacto: 5 a 15 módulos adicionais (mais provável: 10)

## 🎯 DESAFIOS PARA ANÁLISE

1. ✅ Qual o custo total (P85)? **ATENÇÃO**: R$ 8.000/pessoa-semana!
2. ✅ O deadline de 14 semanas é viável?
3. ✅ **Trade-off**: Vale a pena pagar R$ 1M+ para modernizar, ou manter sistema legado?
4. ✅ Seria melhor modernizar apenas módulos críticos primeiro?

**ANÁLISE DE ROI**:
- Custo atual: R$ 120k/mês manutenção = R$ 1.44M/ano
- Custo do projeto: ~R$ 800k - R$ 1M (calcular!)
- Payback em quanto tempo?

## 🔧 PASSOS NO FLOW FORECASTER

1. Simulação com riscos (débito técnico de 70% é ALTO!)
2. Análise de Deadline
3. **Análise de Custos** (P50 vs P85 vs P95)
   - Custo Conservador (P95) pode passar de R$ 1M!
4. **Cenário Alternativo**: E se priorizarmos apenas 40 módulos mais críticos?
   - Simular novamente com backlog de 40
   - Comparar custo vs benefício

**DISCUSSÃO**: Vocês recomendariam este investimento ao CFO?

**Tempo**: 25 minutos para análise + 8 minutos para preparar apresentação

---

# 📝 TEMPLATE DE APRESENTAÇÃO PARA TODOS OS GRUPOS

## Estrutura da Apresentação (1 minuto e 30 segundos)

### 1️⃣ CENÁRIO (15 segundos)
- Nome do projeto
- Contexto de urgência
- Prazo e orçamento

### 2️⃣ NÚMEROS-CHAVE (45 segundos)
- **P50**: [X] semanas
- **P85**: [Y] semanas ← **DESTAQUE ESTE**
- **P95**: [Z] semanas
- **Custo P85**: R$ [valor]
- **Viabilidade do deadline**: ✅ / ⚠️ / ❌
- **% de escopo viável no prazo**: [X]%

### 3️⃣ RECOMENDAÇÃO (30 segundos)
**Decisão**: 🟢 GO / 🟡 AJUSTAR / 🔴 NO-GO

**Justificativa**: (escolher 1-2 pontos)
- [ ] Prazo viável com margem de [X]%
- [ ] Necessário aumentar equipe de [X] para [Y] pessoas
- [ ] Reduzir escopo para [X] itens (MVP)
- [ ] Estender deadline em [X] semanas
- [ ] Mitigar risco [nome do risco] com [ação específica]
- [ ] Custo vs benefício não justifica investimento

---

**🎯 DICA FINAL**: Apresentem DADOS, não opiniões! Use os números do Flow Forecaster.

**⏰ TEMPO LIMITE**: 1 minuto e 30 segundos. Seja objetivo!
