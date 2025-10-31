# 🎯 ROTEIRO DE WORKSHOP - PMI-DF SUMMIT 2025
## Oficina Prática de Monte Carlo para Avaliação de Riscos e Otimização de Portfólio utilizando I.A.

**Facilitador**: Rodrigo Oliveira
**Duração**: 90 minutos
**Participantes**: 30 pessoas (6 grupos de 5)
**Ferramenta**: Flow Forecaster (https://flow-forecaster.fly.dev/)

---

## 📊 OBJETIVOS DO WORKSHOP

Ao final do workshop, os participantes serão capazes de:
1. ✅ Compreender os fundamentos de simulações Monte Carlo para gestão de projetos
2. ✅ Aplicar técnicas probabilísticas para análise de riscos e previsões
3. ✅ Utilizar o Flow Forecaster para forecasting de portfólio
4. ✅ Interpretar resultados probabilísticos (P50/P85/P95) para tomada de decisão
5. ✅ Combinar Monte Carlo com Machine Learning (IA) para validação de previsões

---

## 🕐 CRONOGRAMA DETALHADO (90 minutos)

### ⏰ **00:00 - 00:15 (15 min) - ABERTURA E CONTEXTO**

#### **Atividades:**
1. **Boas-vindas e apresentação** (3 min)
   - Apresentação do facilitador
   - Visão geral do workshop
   - Objetivo: transformar incerteza em decisões baseadas em dados

2. **Dinâmica de Quebra-gelo: "O Problema da Estimativa"** (7 min)
   - **Pergunta ao grupo**: "Quando este projeto vai terminar?"
   - Pedir para 3-4 voluntários darem suas estimativas
   - Mostrar a variação nas respostas (geralmente 50-200% de diferença!)
   - **Insight**: Estimativas pontuais são perigosas. Precisamos trabalhar com probabilidades!

3. **Conceitos fundamentais** (5 min)
   - **Slide 1**: O que é Monte Carlo?
     - Técnica criada em 1940 no Projeto Manhattan
     - Simula milhares de cenários possíveis
     - Gera distribuições de probabilidade em vez de valores únicos

   - **Slide 2**: Por que usar no gerenciamento de projetos?
     - Projetos têm incertezas inerentes
     - Stakeholders precisam de ranges, não certezas falsas
     - Permite análise de riscos quantitativa

   - **Slide 3**: Monte Carlo + IA (Machine Learning)
     - MC: Simula variabilidade histórica
     - ML: Identifica tendências e padrões
     - **Juntos**: Validação cruzada e maior confiabilidade

#### **Material de apoio:**
- Slide com citação: "In God we trust, all others must bring data" - W. Edwards Deming
- Exemplo visual: histograma de distribuição vs. estimativa única

---

### ⏰ **00:15 - 00:35 (20 min) - DEMONSTRAÇÃO PRÁTICA AO VIVO**

#### **Cenário Real: Projeto de Transformação Digital**

**Contexto projetado no telão:**
```
🏢 Empresa: FinTech em expansão
📦 Projeto: Migração de sistemas legados para cloud
📋 Backlog: 120 user stories
👥 Equipe: 8 desenvolvedores
📅 Deadline: 31/03/2026 (20 semanas disponíveis)
💰 Custo/pessoa-semana: R$ 6.000
```

**Dados Históricos (últimas 12 semanas):**
```
Throughput semanal: 8, 6, 10, 7, 9, 8, 5, 11, 7, 9, 8, 10 items/semana
```

#### **Passo-a-passo da demonstração:**

**1. Acesso ao Flow Forecaster** (2 min)
- Projetar: https://flow-forecaster.fly.dev/
- Explicar brevemente a interface
- Mostrar as 4 abas principais

**2. Simulação Monte Carlo Básica** (5 min)
- Navegar para aba "Simulação Monte Carlo"
- Preencher dados:
  ```
  Nome do Projeto: Migração Cloud FinTech
  Backlog: 120
  Throughput: 8, 6, 10, 7, 9, 8, 5, 11, 7, 9, 8, 10
  Número de Simulações: 10000
  Tamanho da Equipe: 8
  ```
- Clicar em "Executar Simulação"
- **PAUSAR e explicar os resultados**:
  - P50: ~14 semanas (50% de chance)
  - P85: ~17 semanas (85% de chance) ← **RECOMENDADO**
  - P95: ~19 semanas (95% de chance)

**Pergunta ao grupo**: "Com deadline em 20 semanas, vocês aceitariam este projeto?"

**3. Análise de Riscos** (5 min)
- Adicionar riscos reais:
  ```
  Risco 1: "Atraso na homologação de segurança"
    - Probabilidade: 40%
    - Impacto: 8-12-20 stories adicionais

  Risco 2: "Dependência externa (API do banco)"
    - Probabilidade: 30%
    - Impacto: 5-8-15 stories adicionais

  Risco 3: "Retrabalho por mudança de requisitos"
    - Probabilidade: 60%
    - Impacto: 3-5-10 stories adicionais
  ```
- Executar novamente
- **Mostrar o impacto**: P85 agora pode estar em 20+ semanas!

**4. Análise de Deadline Integrada** (5 min)
- Navegar para aba "Análise de Deadline"
- Preencher:
  ```
  Data Início: 01/11/2025
  Deadline: 31/03/2026
  Backlog: 120
  Throughput: (mesmo de antes)
  ```
- Executar e mostrar:
  - Pode cumprir deadline? ⚠️ **PARCIALMENTE**
  - Escopo viável até deadline: ~102 stories (85%)
  - Opções: reduzir escopo OU aumentar equipe OU estender prazo

**5. Machine Learning + Validação** (3 min)
- Mostrar comparação ML vs. Monte Carlo
- Explicar "Risk Assessment": LOW/MEDIUM/HIGH
- Mostrar consenso entre métodos

#### **Mensagem-chave:**
"Não estamos adivinhando. Estamos simulando 10.000 futuros possíveis baseados em dados reais!"

---

### ⏰ **00:35 - 01:15 (40 min) - EXERCÍCIO PRÁTICO EM GRUPOS**

#### **Organização dos grupos:**
- **6 grupos de 5 pessoas** (ilhas já organizadas)
- Cada grupo recebe um **Cenário de Portfólio diferente**
- Cada grupo terá 1 laptop acessando o Flow Forecaster

#### **📋 CENÁRIOS POR GRUPO:**

**GRUPO 1 - Projeto de Infraestrutura Cloud**
```
Contexto: Migração de datacenter para AWS
Backlog: 80 tarefas
Throughput histórico (10 semanas): 6, 8, 5, 9, 7, 6, 10, 7, 8, 6
Equipe: 5 pessoas
Deadline: 15 semanas
Custo/pessoa-semana: R$ 5.500

Riscos:
1. "Downtime não planejado": 25%, impacto 5-8-12 tarefas
2. "Falha em testes de performance": 40%, impacto 8-12-20 tarefas

Desafio: Avaliar viabilidade e custo total (P85)
```

**GRUPO 2 - Desenvolvimento de App Mobile**
```
Contexto: App de delivery para marketplace
Backlog: 150 features
Throughput histórico (12 semanas): 10, 12, 8, 14, 11, 9, 13, 10, 12, 11, 15, 10
Equipe: 10 desenvolvedores
Deadline: 18 semanas
Custo/pessoa-semana: R$ 4.800

Riscos:
1. "Mudança de design pela diretoria": 70%, impacto 10-15-25 features
2. "Integração com sistema de pagamento": 50%, impacto 8-12-18 features
3. "Bugs críticos em produção": 30%, impacto 5-8-12 features

Desafio: O deadline é viável? Quanto do escopo será entregue?
```

**GRUPO 3 - Transformação Digital (PMO)**
```
Contexto: Implantação de escritório de projetos
Backlog: 45 iniciativas
Throughput histórico (8 semanas): 4, 5, 3, 6, 5, 4, 7, 5
Equipe: 3 pessoas (PMO dedicado)
Deadline: 12 semanas
Custo/pessoa-semana: R$ 7.000

Riscos:
1. "Resistência cultural das áreas": 80%, impacto 5-10-15 iniciativas
2. "Falta de sponsor executivo": 40%, impacto 3-5-8 iniciativas

Desafio: Cenário de alta incerteza. Como comunicar ao board?
```

**GRUPO 4 - Projeto de Compliance LGPD**
```
Contexto: Adequação à Lei Geral de Proteção de Dados
Backlog: 95 ações corretivas
Throughput histórico (10 semanas): 7, 9, 6, 10, 8, 7, 11, 9, 8, 10
Equipe: 6 pessoas (jurídico + TI)
Deadline: 16 semanas (prazo regulatório!)
Custo/pessoa-semana: R$ 6.500

Riscos:
1. "Auditoria encontra novas não-conformidades": 60%, impacto 10-15-25 ações
2. "Terceiros não atendem no prazo": 50%, impacto 8-12-18 ações

Desafio: Prazo FIXO. Avaliar probabilidade de sucesso e plano B.
```

**GRUPO 5 - Lançamento de Produto (Go-to-Market)**
```
Contexto: Novo SaaS B2B para gestão de contratos
Backlog: 200 itens (marketing + vendas + tech)
Throughput histórico (12 semanas): 15, 18, 12, 20, 16, 14, 22, 17, 19, 16, 21, 18
Equipe: 15 pessoas (multidisciplinar)
Deadline: 25 semanas
Custo/pessoa-semana: R$ 5.200

Riscos:
1. "Pivotar estratégia após feedback de clientes": 50%, impacto 20-30-50 itens
2. "Atraso no desenvolvimento de integrações": 40%, impacto 15-25-40 itens
3. "Campanha de marketing precisa de ajustes": 60%, impacto 10-15-20 itens

Desafio: Projeto grande. Analisar capacidade real vs. ambição.
```

**GRUPO 6 - Modernização de Sistema Legado**
```
Contexto: Refactoring de monolito para microsserviços
Backlog: 65 módulos para modernizar
Throughput histórico (8 semanas): 5, 7, 4, 8, 6, 5, 9, 6
Equipe: 7 desenvolvedores sêniores
Deadline: 14 semanas
Custo/pessoa-semana: R$ 8.000 (equipe sênior!)

Riscos:
1. "Débito técnico maior que o esperado": 70%, impacto 8-15-25 módulos
2. "Testes de regressão encontram bugs críticos": 50%, impacto 5-10-15 módulos

Desafio: Alto custo. Avaliar trade-off entre escopo e budget.
```

#### **Instruções para os grupos (5 min):**

1. **Leiam o cenário juntos** (2 min)
2. **Designem papéis** (1 min):
   - 1 pessoa no computador (operador do Flow Forecaster)
   - 1 relator (anotará conclusões)
   - 3 analistas (discutem e tomam decisões)

3. **Executem as análises** (25 min):
   - [ ] Simulação Monte Carlo básica (P50/P85/P95)
   - [ ] Adicionar riscos identificados
   - [ ] Análise de deadline (viabilidade)
   - [ ] Análise de custos (P85)
   - [ ] Comparar com ML (se tiver 8+ amostras)

4. **Preparem apresentação de 3 minutos** (8 min):
   - Cenário recebido
   - Principais achados (números!)
   - Recomendação ao sponsor/stakeholder
   - Decisão: GO / AJUSTAR / NO-GO

#### **Facilitador circula pelos grupos:**
- Tirar dúvidas sobre uso da ferramenta
- Provocar discussões: "E se aumentarem a equipe?", "E se cortarem 20% do escopo?"
- Garantir que todos os grupos estão progredindo

---

### ⏰ **01:15 - 01:25 (10 min) - APRESENTAÇÕES RÁPIDAS DOS GRUPOS**

**Formato**: 1 minuto e 30 segundos por grupo + 30 seg de perguntas/comentários

**Cada grupo apresenta:**
1. Cenário recebido (15 seg)
2. **Números-chave** (45 seg):
   - P85 de prazo e custo
   - Viabilidade do deadline
   - Impacto dos riscos
3. **Recomendação** (30 seg): GO / AJUSTAR / NO-GO + justificativa

**Papel do facilitador:**
- Timeboxing rigoroso (1min30seg por grupo)
- Destacar insights interessantes
- Conectar com conceitos apresentados

---

### ⏰ **01:25 - 01:30 (5 min) - FECHAMENTO E TAKEAWAYS**

#### **Principais Aprendizados:**

**1. Estimativas Probabilísticas > Estimativas Únicas**
```
❌ "O projeto termina em 15 semanas"
✅ "Há 85% de chance de terminar em 17 semanas ou menos (P85)"
```

**2. Use P85 como padrão para comprometimentos**
- P50: Muito otimista (50% de chance de atrasar!)
- P85: Equilíbrio entre confiança e realismo
- P95: Reservar para contextos críticos

**3. Monte Carlo + IA = Validação Cruzada**
- Se MC e ML concordam → Alta confiança
- Se divergem muito (>20%) → Investigar causas

**4. Riscos devem ser quantificados**
- Não basta listar riscos
- Quantificar: probabilidade × impacto
- Flow Forecaster simula automaticamente!

**5. Dados > Opiniões**
- Throughput histórico é seu melhor preditor
- Quanto mais dados, melhores as previsões
- Mínimo: 5-8 semanas. Ideal: 12+

#### **Call to Action:**

**🎯 Próximos Passos:**
1. ✅ Acessem: https://flow-forecaster.fly.dev/
2. ✅ Coletem throughput histórico dos seus projetos (esta semana!)
3. ✅ Executem uma simulação com dados reais
4. ✅ Compartilhem resultados com stakeholders usando P50/P85/P95

**📚 Materiais Complementares:**
- Flow Forecaster: https://flow-forecaster.fly.dev/
- Manual do Usuário (completo): disponível no site
- Conceito: "Forecasting" baseado em Troy Magennis
- Livros recomendados:
  - "When Will It Be Done?" - Daniel Vacanti
  - "Actionable Agile Metrics" - Daniel Vacanti
  - "How to Measure Anything" - Douglas Hubbard

**Citação Final:**
> "Previsão não é sobre estar certo. É sobre quantificar incerteza para tomar melhores decisões."
> — Rodrigo Oliveira

---

## 📦 CHECKLIST PRÉ-WORKSHOP (30 min antes)

### ✅ Infraestrutura Técnica:
- [ ] Projetor conectado e testado (HDMI)
- [ ] Wi-Fi funcionando (testar velocidade)
- [ ] Flow Forecaster acessível (abrir em 3-4 dispositivos para testar carga)
- [ ] Flipchart/quadro branco com canetas
- [ ] Extensões elétricas posicionadas
- [ ] Som testado (se houver vídeo de abertura)

### ✅ Materiais para Participantes:
- [ ] 30 blocos de anotações + canetas
- [ ] 6 cartões com cenários impressos (1 por grupo)
- [ ] Post-its em 3 cores distribuídos nas ilhas
- [ ] 6 marcadores para flipcharts móveis (1 por grupo)

### ✅ Materiais do Facilitador:
- [ ] Slides de abertura (15 slides máximo)
- [ ] Cenário de demonstração pronto no browser
- [ ] Timer visível para timeboxing
- [ ] Lista de participantes (se houver)
- [ ] Certificados (se aplicável)

### ✅ Configuração da Sala:
- [ ] 6 ilhas de 5 cadeiras
- [ ] 1 laptop por ilha (ou garantir que pelo menos 6 participantes tragam)
- [ ] Tomadas acessíveis para cada ilha
- [ ] Flipchart móvel ou espaço para anotações por grupo
- [ ] Relógio/cronômetro visível

---

## 🎓 DICAS DE FACILITAÇÃO

### Para o Facilitador:

**Durante a Demonstração:**
- ⏱️ **Gerencie o tempo rigorosamente** - 90 min passam RÁPIDO
- 🗣️ **Fale menos, mostre mais** - Priorize hands-on vs. teoria
- ❓ **Faça perguntas provocativas**: "O que vocês fariam com esses números?"
- 🎯 **Use exemplos reais** - Projetos atrasados que todos conhecem

**Durante os Exercícios:**
- 🚶 **Circule pelos grupos** - Não fique parado no palco
- 👂 **Ouça as discussões** - Capture insights para o fechamento
- ⚡ **Intervenha se travar** - Mas deixe eles explorarem primeiro
- 🕐 **Avisos de tempo**: 20 min restando, 10 min, 5 min

**Durante as Apresentações:**
- ⏰ **Seja FIRME no tempo** - 1min30seg por grupo, sem exceções
- 👏 **Celebre insights** - "Ótima observação sobre os riscos!"
- 🔗 **Conecte com teoria** - "Vejam como o P85 deles foi conservador"
- 📸 **Fotos dos grupos** - Registre para redes sociais (se autorizado)

### Frases Úteis:

**Se alguém perguntar sobre Python/código:**
"Ótima pergunta! O Flow Forecaster abstrai toda a complexidade. Vocês estão usando Monte Carlo e Machine Learning sem precisar programar uma linha!"

**Se alguém questionar a precisão:**
"Lembrem-se: não estamos tentando acertar o futuro. Estamos quantificando incerteza. P85 significa que em 85% das simulações o resultado foi este ou melhor."

**Se um grupo travar:**
"Qual é a primeira pergunta que o sponsor faria? 'Quando termina?' Comecem por aí!"

**Se sobrar tempo (improvável):**
"Vamos simular um 'what-if': e se aumentássemos a equipe em 2 pessoas? Quanto muda o P85?"

---

## 📊 MÉTRICAS DE SUCESSO DO WORKSHOP

**Indicadores de que o workshop foi bem-sucedido:**

✅ **Engajamento:**
- Todos os 6 grupos completaram pelo menos 1 simulação
- Discussões ativas durante exercícios (ruído produtivo!)
- Perguntas sobre aplicação em projetos reais

✅ **Aprendizado:**
- Participantes conseguem explicar P50/P85/P95
- Grupos apresentam recomendações baseadas em dados (não "achismos")
- Pelo menos 3 participantes pedem acesso ao Flow Forecaster depois

✅ **Aplicabilidade:**
- Participantes veem valor imediato para seus projetos
- Feedback positivo sobre "isso resolve meu problema de estimativas!"
- Alguém pergunta: "Posso usar isso na segunda-feira?"

---

## 🚀 PÓS-WORKSHOP: FOLLOW-UP

**1. Email para participantes (enviar em 24h):**
```
Assunto: [PMI-DF Summit] Material do Workshop Monte Carlo + Flow Forecaster

Olá!

Foi um prazer ter vocês no workshop! Seguem os materiais e próximos passos:

🔗 Flow Forecaster: https://flow-forecaster.fly.dev/
📘 Manual Completo: [link para manual]
📊 Slides do Workshop: [link para slides]
🎯 Cenários dos Exercícios: [link para PDF com os 6 cenários]

✨ Desafio: Esta semana, executem UMA simulação com dados reais do seu projeto!

Compartilhem os resultados comigo: [seu email]

Abraços,
Rodrigo Oliveira
```

**2. Pesquisa de Feedback (Google Forms):**
- O workshop atendeu suas expectativas? (1-5)
- Você pretende usar Monte Carlo nos seus projetos? (Sim/Não/Talvez)
- Qual foi seu principal aprendizado?
- Sugestões de melhoria?

**3. LinkedIn Post (opcional):**
```
🎲 "Monte Carlo não é só para cassinos!"

Acabei de facilitar um workshop no #PMIDFSummit sobre simulações
probabilísticas para gestão de projetos.

30 profissionais de PMO experimentaram o Flow Forecaster e descobriram
como transformar incerteza em decisões baseadas em dados.

Principais aprendizados:
✅ P85 > estimativas únicas
✅ Monte Carlo + IA = validação cruzada
✅ Riscos devem ser quantificados, não só listados

Obrigado a todos que participaram! 🚀

#MonteCarloSimulation #ProjectManagement #DataDriven #AI
```

---

## 📌 APÊNDICE: RESPOSTAS ESPERADAS DOS CENÁRIOS

### GRUPO 1 (Infraestrutura Cloud):
- **P85 esperado**: ~12-13 semanas
- **Viabilidade**: ✅ SIM (deadline: 15 semanas)
- **Custo P85**: ~R$ 350.000 - R$ 400.000
- **Recomendação**: GO com margem confortável

### GRUPO 2 (App Mobile):
- **P85 esperado**: ~15-16 semanas (sem riscos), ~18-20 semanas (com riscos)
- **Viabilidade**: ⚠️ PARCIAL (deadline: 18 semanas)
- **Impacto riscos**: Alto! 70% de chance de mudança de design
- **Recomendação**: AJUSTAR - priorizar MVP ou aumentar equipe

### GRUPO 3 (PMO - Alta Incerteza):
- **P85 esperado**: ~10-11 semanas (sem riscos), ~14-16 semanas (com 80% de resistência cultural!)
- **Viabilidade**: ❌ NÃO (deadline: 12 semanas)
- **Mensagem-chave**: Resistência cultural é o maior risco!
- **Recomendação**: AJUSTAR - iniciar com change management primeiro

### GRUPO 4 (Compliance LGPD):
- **P85 esperado**: ~12-13 semanas (sem riscos), ~16-18 semanas (com riscos)
- **Viabilidade**: ⚠️ CRÍTICO (prazo regulatório fixo!)
- **Recomendação**: Aumentar equipe AGORA ou priorizar ações críticas

### GRUPO 5 (Produto SaaS):
- **P85 esperado**: ~15-17 semanas (sem riscos), ~22-25 semanas (com riscos)
- **Viabilidade**: ⚠️ PARCIAL (deadline: 25 semanas)
- **Insight**: 50% de chance de pivotar estratégia muda TUDO
- **Recomendação**: Usar metodologia Lean Startup, validar antes de construir

### GRUPO 6 (Sistema Legado):
- **P85 esperado**: ~10-11 semanas (sem riscos), ~15-17 semanas (com débito técnico)
- **Viabilidade**: ⚠️ PARCIAL (deadline: 14 semanas)
- **Custo alto**: R$ 8.000/pessoa-semana! Total: ~R$ 840.000 - R$ 950.000
- **Recomendação**: Trade-off entre escopo e budget. Priorizar módulos críticos.

---

## ✅ LISTA DE VERIFICAÇÃO FINAL

**1 semana antes:**
- [ ] Confirmar infraestrutura com organização do evento
- [ ] Testar Flow Forecaster com 10+ usuários simultâneos
- [ ] Imprimir 6 cartões com cenários (backup se internet cair)
- [ ] Preparar slides finais

**1 dia antes:**
- [ ] Revisar roteiro completo
- [ ] Preparar timer/cronômetro
- [ ] Confirmar acesso à sala 30 min antes
- [ ] Carregar todos os materiais digitais em backup (pen drive)

**Dia do workshop (30 min antes):**
- [ ] Chegar cedo e testar TUDO
- [ ] Organizar ilhas de 5 pessoas
- [ ] Distribuir materiais nas mesas
- [ ] Abrir Flow Forecaster em modo projeção
- [ ] Respirar fundo e se divertir! 🎉

---

**BOA SORTE NO WORKSHOP! 🚀**

*Este roteiro foi criado para maximizar aprendizado hands-on em 90 minutos. Ajuste conforme necessário para seu estilo de facilitação.*
