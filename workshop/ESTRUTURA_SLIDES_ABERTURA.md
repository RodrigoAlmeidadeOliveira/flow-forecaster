# 🎬 ESTRUTURA DOS SLIDES DE ABERTURA
## Workshop Monte Carlo - PMI-DF Summit 2025

**Duração total dos slides**: 15 minutos máximo
**Número de slides**: 12-15 slides
**Estilo**: Visual, pouco texto, muitos exemplos

---

## 📑 SEQUÊNCIA DE SLIDES

### SLIDE 1: CAPA
```
🎲 Oficina Prática de Monte Carlo
para Avaliação de Riscos e Otimização de Portfólio
utilizando I.A.

PMI-DF Summit 2025

Rodrigo Oliveira
Duração: 90 minutos
```

**Elementos visuais**:
- Logo PMI-DF Summit
- Imagem: Dados de cassino (Monte Carlo) + chips de computador (IA)
- Cores: Roxo e ciano do PMI-DF

---

### SLIDE 2: QUEM SOU EU
```
Rodrigo Oliveira

[Foto profissional]

• [Sua experiência com gestão de projetos]
• [Certificações relevantes]
• [Experiência com forecasting/métricas]

GitHub: [link se aplicável]
LinkedIn: [seu perfil]
```

**Propósito**: Estabelecer credibilidade rápido (1 minuto)

---

### SLIDE 3: O PROBLEMA DAS ESTIMATIVAS
```
❓ "QUANDO ESTE PROJETO VAI TERMINAR?"

Respostas típicas:
👤 Gerente de Projetos: "8 semanas"
👤 Desenvolvedor Sênior: "12 semanas"
👤 Sponsor: "Preciso em 6 semanas!"
👤 PMO: "Entre 10 e 15 semanas..."

🤔 QUEM ESTÁ CERTO?
```

**Elementos visuais**:
- Ilustração de pessoas com balões de fala diferentes
- Destaque para a discrepância (8 vs 12 vs 6 vs 10-15)

**Mensagem**: Estimativas pontuais são problemáticas!

---

### SLIDE 4: O PROBLEMA É REAL
```
📊 ESTATÍSTICAS DE PROJETOS

45% dos projetos ultrapassam orçamento
(Fonte: PMI Pulse of the Profession 2024)

38% dos projetos atrasam
(Fonte: PMI Pulse of the Profession 2024)

Custo médio do atraso:
R$ 200.000 por semana em projetos de médio porte
```

**Elementos visuais**:
- Gráfico de pizza ou barras
- Ícone de dinheiro queimando

**Mensagem**: Não é só você. É um problema sistêmico!

---

### SLIDE 5: POR QUE ESTIMAMOS TÃO MAL?
```
🧠 VIESES COGNITIVOS

Otimismo Exagerado 😊
"Desta vez será diferente!"

Planning Fallacy 📅
Ignoramos o histórico de atrasos

Pressão de Stakeholders 💼
"Me dê um número!"

Incerteza Inerente 🎲
Projetos têm variabilidade natural
```

**Elementos visuais**:
- Ícones para cada viés
- Imagem de cérebro com "bugs"

---

### SLIDE 6: A SOLUÇÃO - MONTE CARLO
```
🎲 SIMULAÇÕES MONTE CARLO

O que é?
Técnica matemática que simula milhares
de cenários possíveis

De onde vem?
Criada em 1946 por Stanislaw Ulam
(Projeto Manhattan)

Como funciona?
1. Coleta dados históricos
2. Simula 10.000+ cenários
3. Gera distribuição de probabilidades
```

**Elementos visuais**:
- Foto histórica do Projeto Manhattan (opcional)
- Diagrama simples: Dados → Simulação → Resultados

---

### SLIDE 7: MONTE CARLO EM AÇÃO
```
📊 EXEMPLO VISUAL

[Histograma de distribuição]

Eixo X: Semanas até conclusão
Eixo Y: Frequência de cenários

Marcadores:
P50 = 10 semanas (mediana)
P85 = 13 semanas (recomendado)
P95 = 15 semanas (conservador)

❌ Resposta antiga: "Termina em 10 semanas"
✅ Resposta nova: "85% de chance de terminar em 13 semanas ou menos"
```

**Elementos visuais**:
- Histograma real (pode ser do Flow Forecaster)
- Setas destacando P50, P85, P95

---

### SLIDE 8: PERCENTIS - COMO INTERPRETAR
```
🎯 P50 vs P85 vs P95

P50 (50%)  😊 Otimista
→ Use para discussões internas
→ 50% de chance de atrasar!

P85 (85%)  ⭐ RECOMENDADO
→ Use para comprometimentos
→ Equilíbrio entre confiança e realismo

P95 (95%)  🛡️ Conservador
→ Use para projetos críticos
→ Contratos com multa por atraso
```

**Elementos visuais**:
- 3 colunas com cores diferentes
- Ícones: cara feliz (P50), estrela (P85), escudo (P95)

**Mensagem-chave**: SEMPRE use P85 para commitments!

---

### SLIDE 9: MONTE CARLO + INTELIGÊNCIA ARTIFICIAL
```
🤝 A COMBINAÇÃO PERFEITA

🎲 Monte Carlo
✓ Simula variabilidade
✓ Quantifica incerteza
✓ Funciona com poucos dados (5-8 amostras)

🤖 Machine Learning
✓ Identifica tendências
✓ Detecta padrões
✓ Precisa de mais dados (8+ amostras)

💡 JUNTOS = VALIDAÇÃO CRUZADA
Se ambos concordam → Alta confiança
Se divergem → Investigar por quê
```

**Elementos visuais**:
- Ícone de dados + ícone de IA = ícone de aperto de mãos
- Diagrama de Venn (MC ∩ ML)

---

### SLIDE 10: FLOW FORECASTER
```
🚀 FERRAMENTA QUE USAREMOS HOJE

https://flow-forecaster.fly.dev/

✓ Simulações Monte Carlo (10.000 iterações)
✓ Machine Learning (4 algoritmos)
✓ Análise de riscos probabilística
✓ Análise de deadline e custos
✓ 100% Web (não precisa instalar nada!)

Usado por:
• Equipes de software development
• PMOs corporativos
• Consultorias de gestão
```

**Elementos visuais**:
- Screenshot da interface do Flow Forecaster
- QR Code para o site (https://flow-forecaster.fly.dev/)

---

### SLIDE 11: COMO FUNCIONA NA PRÁTICA
```
📋 WORKFLOW TÍPICO

1️⃣ COLETA
Throughput histórico (ex: 5, 6, 7, 4, 8 items/semana)

2️⃣ ENTRADA
Backlog atual (ex: 50 items pendentes)

3️⃣ SIMULAÇÃO
10.000 cenários possíveis

4️⃣ RESULTADO
P50 = 8 semanas
P85 = 10 semanas ← USE ESTE!
P95 = 12 semanas

5️⃣ DECISÃO
"Commitamos 10 semanas com 85% de confiança"
```

**Elementos visuais**:
- Fluxograma com 5 etapas
- Destaque no resultado P85

---

### SLIDE 12: EXERCÍCIO EM GRUPOS
```
🎯 O QUE VOCÊS FARÃO HOJE

6 Grupos de 5 Pessoas

Cada grupo recebe:
• 1 Cenário de projeto real
• Dados históricos
• Riscos identificados
• Deadline a validar

Desafio (25 minutos):
✓ Executar simulações no Flow Forecaster
✓ Analisar viabilidade
✓ Calcular custos
✓ Recomendar: GO / AJUSTAR / NO-GO

Apresentação: 1min30seg por grupo
```

**Elementos visuais**:
- Ícone de 6 grupos (circles com pessoas)
- Cronômetro/timer visual

---

### SLIDE 13: CENÁRIOS DOS GRUPOS
```
📦 6 CENÁRIOS DIFERENTES

Grupo 1: Infraestrutura Cloud
Grupo 2: App Mobile
Grupo 3: Implantação de PMO
Grupo 4: Compliance LGPD ⚠️ Prazo Fixo!
Grupo 5: Lançamento de Produto SaaS
Grupo 6: Modernização de Sistema Legado

Todos baseados em projetos REAIS!
```

**Elementos visuais**:
- Grid 3x2 com ícones de cada cenário
- Destaque especial para Grupo 4 (prazo regulatório)

---

### SLIDE 14: PAPÉIS NO GRUPO
```
👥 ORGANIZAÇÃO DO GRUPO

1 Operador 💻
→ Usa o Flow Forecaster

1 Relator 📝
→ Anota resultados e prepara apresentação

3 Analistas 🧠
→ Discutem e tomam decisões

💡 DICA: Todos participam da análise!
O operador não trabalha sozinho.
```

**Elementos visuais**:
- Ilustração de grupo trabalhando
- Ícones para cada papel

---

### SLIDE 15: CRONOGRAMA DO WORKSHOP
```
⏰ PRÓXIMOS 75 MINUTOS

00:00 - 00:20  Demonstração ao vivo
               (Facilitador mostra passo-a-passo)

00:20 - 00:45  Exercício em grupos
               (Vocês executam as análises)

00:45 - 00:55  Apresentações
               (1min30seg por grupo)

00:55 - 01:00  Fechamento e Q&A
               (Principais aprendizados)

🎯 AGORA: Vamos para a demonstração!
```

**Elementos visuais**:
- Timeline horizontal
- Cores diferentes para cada bloco

---

## 🎨 DIRETRIZES DE DESIGN

### Estilo Visual:
- **Fonte**: Sans-serif moderna (Montserrat, Inter, Roboto)
- **Tamanho mínimo**: 24pt (para leitura na última fila)
- **Cores**:
  - Primária: Roxo do PMI-DF
  - Secundária: Ciano/Azul
  - Destaque: Laranja/Amarelo para calls-to-action
  - Texto: Cinza escuro (#333) sobre fundo claro

### Regras de Ouro:
- ✅ **Máximo 6 linhas por slide**
- ✅ **1 ideia central por slide**
- ✅ **Mais imagens, menos texto**
- ✅ **Fonte grande** (mínimo 24pt)
- ❌ **Evitar parágrafos longos**
- ❌ **Evitar bullets dentro de bullets**

### Recursos Visuais:
- Ícones: Font Awesome ou Flaticon
- Imagens: Unsplash, Pexels (royalty-free)
- Gráficos: Capturados do Flow Forecaster
- Cores: Palette consistente (max 4 cores)

---

## 🎤 NOTAS DE APRESENTAÇÃO (SPEAKER NOTES)

### SLIDE 3 (O Problema das Estimativas):
**Dinâmica interativa**: Pedir para 3-4 voluntários do público estimarem um projeto fictício simples. Mostrar a variação nas respostas. "Vejam, até entre profissionais experientes há discrepância enorme!"

### SLIDE 6 (A Solução - Monte Carlo):
**Story**: "Monte Carlo foi criado durante a Segunda Guerra para simular reações nucleares. Se funcionou para salvar o mundo, funciona para nossos projetos!"

### SLIDE 8 (Percentis):
**Analogia**: "É como previsão do tempo. Quando dizem '80% de chance de chuva', você leva guarda-chuva, certo? P85 é nosso 'guarda-chuva' de planejamento!"

### SLIDE 10 (Flow Forecaster):
**Transição**: "Tudo isso parece complexo? Tranquilo! O Flow Forecaster faz as contas pesadas. Vocês só precisam inserir os dados e interpretar resultados."

### SLIDE 15 (Cronograma):
**Call to Action**: "Chega de teoria! Nos próximos 20 minutos vou mostrar AO VIVO como usar. Depois é com vocês! Preparados?"

---

## 📊 RECURSOS ADICIONAIS PARA OS SLIDES

### Fontes de Dados para Estatísticas:
- PMI Pulse of the Profession 2024
- Standish Group CHAOS Report
- State of Agile Report
- McKinsey Delivering Large-Scale IT Projects

### Citações Úteis (usar em slides):

> "In God we trust, all others must bring data."
> — W. Edwards Deming

> "Prediction is very difficult, especially about the future."
> — Niels Bohr

> "Plans are useless, but planning is indispensable."
> — Dwight D. Eisenhower

> "It is better to be roughly right than precisely wrong."
> — John Maynard Keynes

---

## 💾 FORMATO E BACKUP

### Recomendações:
- **Software**: PowerPoint, Google Slides, ou Keynote
- **Resolução**: 16:9 (widescreen)
- **Backup**:
  - Salvar em PDF (caso software falhe)
  - Salvar em pen drive + email + cloud
  - Testar no projetor 30 min antes

### Checklist Técnico:
- [ ] Slides funcionam sem animações complexas (caso projetor seja lento)
- [ ] Fontes estão embedadas (para abrir em outro computador)
- [ ] Vídeos (se houver) estão locais (não dependem de YouTube)
- [ ] Links funcionam (testar Flow Forecaster antes)
- [ ] QR Codes estão grandes o suficiente para scan

---

## 🎬 VÍDEO DE ABERTURA (OPCIONAL)

**Se houver tempo de preparar um vídeo curto (1-2 min)**:

**Conteúdo sugerido**:
1. Montage de manchetes sobre projetos atrasados (30 seg)
2. Time-lapse de simulação Monte Carlo rodando (30 seg)
3. Depoimentos rápidos: "Como Monte Carlo mudou minha forma de planejar" (30 seg)
4. Call-to-action: "Vamos aprender juntos!" (30 seg)

**Música**: Instrumental energizante (royalty-free)
**Fonte**: Epidemic Sound, Artlist, Bensound

---

## ✅ CHECKLIST FINAL DOS SLIDES

Antes do workshop, verificar:

- [ ] Todos os slides estão numerados
- [ ] Timer está configurado (15 min para apresentação)
- [ ] Links para Flow Forecaster funcionam
- [ ] Screenshots estão atualizados (interface pode mudar)
- [ ] Não há typos ou erros gramaticais
- [ ] Cores são legíveis mesmo com projetor fraco
- [ ] Slide de "Perguntas?" no final (opcional)
- [ ] Slide com contatos e recursos (último slide)

---

## 🎯 ÚLTIMO SLIDE: OBRIGADO + RECURSOS

```
🙏 OBRIGADO!

Recursos:
🔗 Flow Forecaster: https://flow-forecaster.fly.dev/
📧 Email: [seu email]
💼 LinkedIn: [seu perfil]
📚 Material do workshop: [link para download]

Perguntas?

#PMIDFSummit2025 #MonteCarlo #DataDriven
```

**Elementos visuais**:
- QR Code para o site
- Foto sua sorrindo
- Logos de parceiros/patrocinadores (se aplicável)

---

**BOA APRESENTAÇÃO! 🎤**

*Lembre-se: Slides são apoio visual. Sua energia e entusiasmo são o que engaja a audiência!*
