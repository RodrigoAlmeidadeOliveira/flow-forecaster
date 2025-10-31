# 🆘 PLANO B - MANUAL DE CONTINGÊNCIAS
## Workshop Monte Carlo - PMI-DF Summit 2025

**IMPORTANTE**: Mantenha a calma e siga os planos abaixo. Todos são viáveis e funcionam!

---

## 🌐 CENÁRIO 1: INTERNET CAI OU FLOW FORECASTER NÃO ABRE

### 🚨 Sintomas:
- Wi-Fi do evento caiu
- Flow Forecaster demora >30 segundos para carregar
- Site retorna erro 500/503
- Performance extremamente lenta (>2 min por simulação)

### ✅ AÇÕES IMEDIATAS (Opção A - Internet 4G):

**Passo 1: Use seu celular como hotspot**
```
1. Ativar hotspot no seu celular
2. Conectar seu notebook ao hotspot
3. Abrir Flow Forecaster normalmente
4. Projetar tela do seu notebook

⏱️ Tempo: 2 minutos
```

**Passo 2: Compartilhar hotspot com 1-2 grupos**
```
Se houver necessidade, compartilhar senha do hotspot com:
- Grupo que estiver mais avançado
- Grupo com maior engajamento

Os outros grupos podem fazer exercício manual (ver Opção B)

⏱️ Tempo: 3 minutos
```

### ✅ AÇÕES IMEDIATAS (Opção B - Simulação Manual de Monte Carlo):

**ANUNCIAR AO GRUPO**:
```
"Pessoal, temos um imprevisto técnico. Vamos fazer algo ainda melhor:
uma simulação MANUAL de Monte Carlo! Vocês vão entender NA PRÁTICA
como funciona o algoritmo. Isso é mais valioso que usar a ferramenta!"
```

**MATERIAL NECESSÁRIO** (ter como backup):
- [ ] 6 dados de 6 faces (ou app de dados no celular)
- [ ] Post-its coloridos (já distribuídos)
- [ ] Flipchart ou quadro branco
- [ ] Calculadora (ou celular)

---

### 📊 EXERCÍCIO MANUAL - PASSO A PASSO

#### **Passo 1: Preparação (3 min)**

No quadro branco/flipchart, escrever:

```
SIMULAÇÃO MANUAL DE MONTE CARLO

Cenário Simplificado:
• Backlog: 30 itens
• Throughput histórico: 3, 5, 4, 6, 5, 4, 6, 5 items/semana
• Pergunta: Em quantas semanas terminamos?
```

#### **Passo 2: Explicar a Mecânica (2 min)**

```
"Vamos simular 10 cenários possíveis (normalmente seriam 10.000!):

1. Cada semana, vamos SORTEAR um throughput do histórico
2. Subtraímos do backlog
3. Repetimos até backlog = 0
4. Anotamos quantas semanas levou
5. Fazemos isso 10 vezes
6. Criamos distribuição visual com post-its"
```

#### **Passo 3: Executar Simulações em Grupo (15 min)**

**GRUPO 1 e 2**: Fazem simulações 1-5
**GRUPO 3 e 4**: Fazem simulações 6-10

**Template de execução** (cada grupo recebe uma folha):

```
═══════════════════════════════════════════════
SIMULAÇÃO #1

Backlog inicial: 30 itens

Semana 1: Sortear throughput = ___ → Backlog = ___
Semana 2: Sortear throughput = ___ → Backlog = ___
Semana 3: Sortear throughput = ___ → Backlog = ___
Semana 4: Sortear throughput = ___ → Backlog = ___
Semana 5: Sortear throughput = ___ → Backlog = ___
Semana 6: Sortear throughput = ___ → Backlog = ___

Total de semanas: ___

═══════════════════════════════════════════════
```

**Como sortear throughput SEM dados físicos**:
```
Opção 1: App de dados no celular
- Procurar "dice roller" na app store
- Usar dado de 8 faces
- Mapear: 1→3, 2→5, 3→4, 4→6, 5→5, 6→4, 7→6, 8→5

Opção 2: Sorteio manual
- Escrever throughputs em papéis (3,5,4,6,5,4,6,5)
- Colocar em um saco/chapéu
- Sortear, anotar, devolver ao saco
```

#### **Passo 4: Consolidar Resultados (5 min)**

No flipchart, criar histograma visual:

```
RESULTADOS DAS 10 SIMULAÇÕES

Semanas   | Frequência (use post-its)
─────────────────────────────────────
4 sem     | □
5 sem     | □ □ □
6 sem     | □ □ □ □
7 sem     | □ □
8 sem     |

P50 (mediana) ≈ 6 semanas
P85 (estimado) ≈ 7 semanas
```

#### **Passo 5: Discussão (5 min)**

**Perguntas para provocar**:
1. "Alguém teria estimado 6 semanas antes da simulação?"
2. "Por que tivemos resultados diferentes (4 a 8 semanas)?"
3. "Qual resultado vocês reportariam ao sponsor?"
4. "Isso é melhor que dizer 'vai dar 6 semanas' com certeza?"

---

### 🎯 MENSAGEM-CHAVE (Mesmo sem ferramenta):

**SLIDE/FLIP CHART**:
```
✅ O QUE APRENDEMOS:

1. Monte Carlo = SORTEAR múltiplos cenários
2. Gera DISTRIBUIÇÃO, não valor único
3. Quantifica INCERTEZA
4. Mesmo 10 simulações já mostram valor!
   (Imagine 10.000...)

💡 Flow Forecaster faz isso em 2 segundos!
   Mas o CONCEITO é o mesmo que fizemos agora!
```

---

### 📋 APRESENTAÇÕES DOS GRUPOS (Ajustado):

Como não fizeram no Flow Forecaster, ajustar formato:

```
APRESENTAÇÃO (1min30seg):

1. Mostrar papel com simulações (15 seg)
2. Resultado: "Entre 5-7 semanas, mediana 6" (30 seg)
3. Insight: "Antes estimaríamos 6 fixo. Agora sabemos
   que pode variar. P85 = 7 semanas seria nosso commitment." (45 seg)
```

---

## 📽️ CENÁRIO 2: PROJETOR FALHA

### 🚨 Sintomas:
- Projetor não liga
- Cabo HDMI com problema
- Imagem distorcida/ilegível
- Não há tempo para consertar

### ✅ AÇÕES IMEDIATAS:

#### **Opção A: Workshop sem Projeção (PREFERENCIAL)**

**Passo 1: Anunciar mudança (30 seg)**
```
"Pessoal, vamos fazer diferente. Em vez de eu mostrar na tela,
vocês vão aprender FAZENDO! Modo hands-on total!"
```

**Passo 2: Pular slides de teoria (ECONOMIZA 10 MIN!)**
```
Explicar conceitos verbalmente + flipchart:

[DESENHAR NO FLIPCHART]

MONTE CARLO = SIMULAR MÚLTIPLOS FUTUROS

Input:
┌─────────────────┐
│ Throughput:     │
│ 5,6,7,4,8,6,5,7 │ → SIMULAÇÃO → Resultado:
│ Backlog: 50     │   10.000×     P50: 8 sem
└─────────────────┘                P85: 10 sem
                                   P95: 12 sem

⏱️ Tempo: 5 minutos (em vez de 15 com slides)
```

**Passo 3: Demonstração circulante (10 min)**
```
Em vez de projetar, CIRCULAR pelos grupos:

1. Ir ao Grupo 1 com notebook
2. Mostrar Flow Forecaster (2 min)
3. Fazer 1 simulação rápida
4. Ir ao Grupo 2, repetir (2 min)
5. Grupos 3-6: observam sobre o ombro

Enquanto circula, grupos JÁ COMEÇAM a acessar
Flow Forecaster nos próprios notebooks!

⏱️ Tempo: 10 minutos
```

**Passo 4: Exercício estendido (40 min em vez de 25 min)**
```
Vantagem: Mais tempo para prática!

Dar 40 minutos para:
- Executar simulações
- Explorar ferramenta
- Discutir em grupo
- Preparar apresentação (últimos 8 min)
```

**Passo 5: Apresentações verbais (10 min)**
```
Grupos apresentam SEM slides projetados:

- Falar os números em voz alta
- Você anota no flipchart enquanto apresentam
- Criar tabela comparativa:

┌───────┬──────┬────────┬──────────────┐
│ Grupo │ P85  │ Custo  │ Recomendação │
├───────┼──────┼────────┼──────────────┤
│   1   │ 12s  │ 350k   │ GO           │
│   2   │ 19s  │ 910k   │ AJUSTAR      │
│  ...  │ ...  │  ...   │ ...          │
└───────┴──────┴────────┴──────────────┘
```

#### **Opção B: Usar Notebook + Grupos Pequenos**

```
1. Posicionar notebook no centro da sala
2. Grupos de 5 se revezam para ver demonstração
3. Depois cada grupo trabalha independente
4. Você circula com notebook mostrando exemplos
```

---

## 💻 CENÁRIO 3: MENOS DE 6 NOTEBOOKS

### 🚨 Situação:
- Apenas 3-4 notebooks disponíveis
- Não dá para fazer 6 grupos independentes

### ✅ AÇÕES IMEDIATAS:

#### **Opção A: Reduzir Grupos (3-4 grupos maiores)**

```
REORGANIZAÇÃO:

EM VEZ DE:    6 grupos de 5 = 30 pessoas
FAZER:        4 grupos de 7-8 = 30 pessoas
              (ou 3 grupos de 10)

CENÁRIOS:
- Grupo 1: App Mobile (complexo)
- Grupo 2: Compliance LGPD (prazo fixo)
- Grupo 3: Sistema Legado (alto custo)
- [Grupo 4: Infraestrutura Cloud]

⏱️ Ajuste de tempo:
- 30 min para exercício (em vez de 25)
- 2 min por apresentação (em vez de 1min30)
```

#### **Opção B: Demonstração Estendida (Modo "Aula")**

```
FORMATO ALTERNATIVO:

00:00-00:15  Abertura (igual)
00:15-00:45  DEMO LONGA (30 min em vez de 20)
             ↓
             Você executa TODOS os 6 cenários
             mostrando na tela (ou circulando)

00:45-01:05  Discussão em Grupos (20 min)
             ↓
             Grupos discutem VERBALMENTE:
             "Se fosse seu projeto, o que faria?"
             Trabalham com papel e caneta

01:05-01:20  Apresentações (15 min)
             ↓
             Grupos apresentam ANÁLISE,
             não resultados de simulação

01:20-01:30  Fechamento
```

**Vantagens**:
- Não depende de múltiplos notebooks
- Você mantém controle total
- Foco em INTERPRETAÇÃO vs. execução

**Desvantagens**:
- Menos hands-on
- Mais "palestra" do que "oficina"

#### **Opção C: Rotação de Notebooks (Modo "Estações")**

```
MECÂNICA:

Dividir em 3 "estações de trabalho":

┌─────────────────────────────────────┐
│ ESTAÇÃO 1: Notebook A               │
│ Grupos 1 e 2 (10 min cada)          │
├─────────────────────────────────────┤
│ ESTAÇÃO 2: Notebook B               │
│ Grupos 3 e 4 (10 min cada)          │
├─────────────────────────────────────┤
│ ESTAÇÃO 3: Notebook C               │
│ Grupos 5 e 6 (10 min cada)          │
└─────────────────────────────────────┘

CRONOGRAMA:
00:35-00:45  Rodada 1 (Grupos ímpares)
00:45-00:55  Rodada 2 (Grupos pares)
00:55-01:03  Preparação apresentação
01:03-01:13  Apresentações
01:13-01:18  Fechamento

⏱️ Tempo total: 43 min (cabe no workshop!)
```

---

## 🐌 CENÁRIO 4: FLOW FORECASTER COM PERFORMANCE RUIM

### 🚨 Sintomas:
- Site abre, mas muito lento
- Simulações levam 2-3 minutos (normal = 5 segundos)
- Travamentos frequentes
- Timeout errors

### ✅ DIAGNÓSTICO RÁPIDO:

```
TESTAR NO SEU NOTEBOOK (antes do workshop):

1. Abrir: https://flow-forecaster.fly.dev/
2. Executar simulação teste:
   - Throughput: 5,6,7,8,5,6,7,8
   - Backlog: 50
   - Simulações: 10000
3. Cronometrar tempo de resposta

✅ Normal: 3-8 segundos
⚠️ Lento: 15-30 segundos
❌ Crítico: >30 segundos ou timeout
```

### ✅ AÇÕES IMEDIATAS:

#### **Opção A: Reduzir Número de Simulações**

```
EM VEZ DE:    10.000 simulações (padrão)
USAR:         1.000 simulações

IMPACTO NA PRECISÃO:
- P50: ~0.1 semana de diferença (aceitável!)
- P85: ~0.2 semanas de diferença
- P95: ~0.3 semanas de diferença

GANHO:
- 10× mais rápido
- Ainda estatisticamente válido

INSTRUÇÃO PARA GRUPOS:
"Mudança de parâmetro: usem 1000 simulações
em vez de 10000 por questão de performance.
Os resultados serão praticamente os mesmos!"
```

#### **Opção B: Fazer 1 Simulação por Grupo (Sequential)**

```
MECÂNICA:

Em vez de 6 grupos simultâneos:
→ Você executa 1 simulação POR VEZ, projetada

Grupos apresentam cenário
     ↓
Você executa simulação ao vivo
     ↓
Grupo interpreta resultado
     ↓
Próximo grupo

⏱️ Tempo:
- 6 simulações × 5 min = 30 min
- Apresentações/discussão: 20 min
- Fechamento: 5 min
Total: 55 min (cabe nos 60 min disponíveis!)

VANTAGEM:
- Apenas 1 requisição por vez ao servidor
- Menos chance de overload
- Todos acompanham juntos
```

#### **Opção C: Modo Offline (Usar Excel)**

```
PREPARAÇÃO (fazer ANTES do workshop):

Criar planilha Excel com fórmulas Monte Carlo:

=RAND() para sortear throughput
=SOMA() para acumular
=CONT.SE() para calcular probabilidades

DISTRIBUIR:
- 6 planilhas (1 por grupo)
- Cada uma com cenário pré-configurado
- Grupos apenas ajustam parâmetros

⚠️ Requer preparação antecipada!
   Não é viável improvisar no dia.
```

---

## 🔥 CENÁRIO 5: MÚLTIPLOS PROBLEMAS SIMULTÂNEOS

### 🚨 Situação:
- Internet caiu + Projetor falhou + Poucos notebooks
- "Murphy's Law" total

### ✅ PLANO B DEFINITIVO: "WORKSHOP ANALÓGICO"

#### **Formato: Case Study + Debate**

```
CRONOGRAMA AJUSTADO:

00:00-00:10  Abertura Simplificada
             ↓ Flipchart apenas, sem slides

00:10-00:15  Explicar Monte Carlo no Quadro
             ↓ Desenhos + exemplo manual (1 simulação)

00:15-00:45  Exercício Analógico (30 min)
             ↓
             Distribuir IMPRESSOS com resultados
             prontos de simulações (você leva backup!)

00:45-01:10  Discussões em Grupo (25 min)
             ↓
             Grupos analisam resultados PRÉ-CALCULADOS
             e decidem recomendações

01:10-01:25  Apresentações (15 min)

01:25-01:30  Fechamento
```

#### **Material IMPRESSO de Backup (preparar antes)**

```
PARA CADA GRUPO, IMPRIMIR:

┌────────────────────────────────────────┐
│ GRUPO 1: INFRAESTRUTURA CLOUD         │
│                                        │
│ Dados do Projeto:                      │
│ • Backlog: 80 tarefas                  │
│ • Throughput: 6,8,5,9,7,6,10,7,8,6     │
│ • Deadline: 15 semanas                 │
│ • Equipe: 5 pessoas                    │
│ • Custo/semana: R$ 5.500               │
│                                        │
│ RESULTADOS DA SIMULAÇÃO MONTE CARLO:   │
│                                        │
│ P50 (mediana):     11.2 semanas        │
│ P85 (recomendado): 13.5 semanas        │
│ P95 (conservador): 15.8 semanas        │
│                                        │
│ CUSTO P85: R$ 371.250                  │
│                                        │
│ RISCOS (se ocorrerem):                 │
│ • Downtime: +1.5 semanas               │
│ • Testes falham: +2.3 semanas          │
│ TOTAL COM RISCOS: 17.3 semanas (P85)   │
│                                        │
│ PERGUNTAS PARA SEU GRUPO:              │
│ 1. Deadline de 15 sem é viável?        │
│ 2. Vale a pena o investimento?         │
│ 3. Qual sua recomendação?              │
│    □ GO  □ AJUSTAR  □ NO-GO           │
└────────────────────────────────────────┘
```

**Vantagem**:
- Funciona 100% offline
- Grupos focam em INTERPRETAÇÃO
- Discussão de negócio > operação de ferramenta

**Desvantagem**:
- Perde aspecto hands-on
- Mas ainda atinge 80% dos objetivos de aprendizado!

---

## 📋 CHECKLIST DE PREPARAÇÃO (Evitar Emergências)

### 1 SEMANA ANTES:

- [ ] **Testar Flow Forecaster** com 10 requisições simultâneas
  ```bash
  Abrir 10 abas do navegador
  Executar simulação em todas ao mesmo tempo
  Verificar se há lentidão/erros
  ```

- [ ] **Testar Wi-Fi do local** (se possível visitar)
  - Velocidade mínima: 10 Mbps
  - Latência máxima: 50ms
  - Pacotes perdidos: <1%

- [ ] **Preparar backup offline**:
  - [ ] Slides em PDF (pen drive)
  - [ ] 6 cenários impressos com resultados prontos
  - [ ] 6 dados físicos (ou app de dados instalado)
  - [ ] Post-its e marcadores extras

- [ ] **Confirmar com participantes**:
  - Quantos trarão notebooks? (mínimo 6)
  - Sistemas operacionais (Mac/Windows/Linux)
  - Navegadores atualizados?

### NO DIA (H-60):

- [ ] **Teste triplo**:
  - [ ] Projetor + HDMI (ter adaptadores)
  - [ ] Wi-Fi (speed test)
  - [ ] Flow Forecaster (simulação teste completa)

- [ ] **Backup imediato disponível**:
  - [ ] Hotspot do celular ativado (com créditos)
  - [ ] Planilhas impressas (6 cópias)
  - [ ] Flipchart pronto com desenhos base

- [ ] **Plano B visível**:
  - Ter este documento impresso ao lado
  - Se algo falhar, consultar rapidamente

---

## 🎯 MINDSET PARA EMERGÊNCIAS

### ✅ FAÇA:

```
✓ Mantenha energia alta e positiva
✓ Apresente o problema como "oportunidade de aprender diferente"
✓ Seja transparente: "Temos um imprevisto, mas tenho um plano!"
✓ Envolva o grupo: "Quem aqui tem hotspot?" "Alguém trouxe notebook?"
✓ Improvise com confiança (você domina o assunto!)
```

### ❌ NÃO FAÇA:

```
✗ Entrar em pânico ou mostrar frustração
✗ Culpar organização do evento
✗ Cancelar ou encurtar drasticamente
✗ Ficar se desculpando repetidamente
✗ Perder tempo tentando "consertar" (passe para Plano B rápido!)
```

### 💡 FRASES ÚTEIS:

**Se internet cair**:
> "Pessoal, a internet caiu, mas isso é uma ÓTIMA oportunidade!
> Vamos fazer uma simulação manual e entender como o algoritmo
> funciona por dentro. Vai ser ainda mais educativo!"

**Se projetor falhar**:
> "Mudança de planos! Vamos fazer modo workshop intensivo.
> Menos eu falando, mais vocês praticando. Vai ser melhor ainda!"

**Se poucos notebooks**:
> "Ótimo! Vamos trabalhar em grupos maiores e colaborativos.
> Isso vai gerar discussões mais ricas!"

**Se Flow Forecaster estiver lento**:
> "O servidor está sobrecarregado. Vamos reduzir para 1000 simulações.
> Matematicamente, o resultado é praticamente idêntico a 10000!"

---

## 📞 CONTATOS DE EMERGÊNCIA

**Suporte Técnico do Evento**:
- Nome: [preencher]
- Telefone: [preencher]
- Localização: [sala/andar]

**Plano B do Plano B**:
- Seu celular (hotspot): [ativar antes]
- Técnico backup (se houver): [contato]
- Organizador PMI-DF: [contato]

---

## ✅ RESUMO: QUAL PLANO B USAR?

| Problema | Solução Rápida (2 min) | Solução Completa (5 min) |
|----------|------------------------|--------------------------|
| **Internet cai** | Seu hotspot 4G | Simulação manual |
| **Projetor falha** | Pular slides, ir direto p/ prática | Demo circulante |
| **< 6 notebooks** | Grupos maiores (4 em vez de 6) | Demo estendida |
| **Flow lento** | Reduzir p/ 1000 simulações | Executar sequencial |
| **Tudo deu errado** | Exercício analógico | Case study c/ impressos |

---

**LEMBRE-SE**: O objetivo é ensinar **CONCEITOS**, não apenas "usar a ferramenta".

Se os participantes saírem entendendo:
- ✅ O que é Monte Carlo
- ✅ Por que P85 > estimativa única
- ✅ Como quantificar riscos
- ✅ Dados > opiniões

**→ O workshop foi um SUCESSO!** 🎯

Mesmo que usem apenas papel e caneta! 📝

---

**VOCÊ ESTÁ PREPARADO PARA QUALQUER CENÁRIO! 💪**
