# Guia: Como Usar Cost of Delay (CoD) Analysis

## 📋 O que é CoD Analysis?

A funcionalidade **Cost of Delay (CoD) Analysis** otimiza automaticamente a ordem de execução dos projetos do seu portfólio usando o algoritmo **WSJF (Weighted Shortest Job First)**.

**Benefícios:**
- 🎯 Priorização objetiva baseada em dados
- 💰 Redução de 20-40% no Cost of Delay total
- 📊 Comparação de 4 estratégias diferentes
- ⚡ Identificação de projetos urgentes
- 🔢 Cálculo automático de economia

---

## ✅ Pré-requisitos

Antes de executar a análise CoD, você precisa:

### 1. **Portfolio Criado**
- Acesse: Menu → Portfolio
- Crie um novo portfolio com nome, orçamento e capacidade

### 2. **Projetos Adicionados ao Portfolio**
- Clique em "Adicionar Projeto"
- Selecione projetos da lista
- Configure as métricas (veja seção abaixo)

### 3. **Forecasts Executados** ⚠️ OBRIGATÓRIO
Cada projeto no portfolio DEVE ter um forecast salvo:
- Vá em: Projetos → Selecione o projeto
- Clique em "Executar Forecast"
- Aguarde simulação Monte Carlo
- Verifique se o forecast foi salvo com sucesso

### 4. **Métricas Configuradas** (Recomendado)
- **Cost of Delay (R$/semana)**: Quanto a empresa perde por semana de atraso
- **Business Value (0-100)**: Valor de negócio do projeto
- **Time Criticality (0-100)**: Urgência temporal
- **Risk Reduction (0-100)**: Quanto reduz riscos organizacionais

---

## 🔢 Como Configurar as Métricas

### Cost of Delay (CoD)
**O que é:** Perda financeira semanal por atraso no projeto.

**Como calcular:**
```
Receita esperada por ano / 52 semanas = CoD semanal
```

**Exemplos:**
- Projeto gera R$ 500.000/ano → CoD = R$ 9.615/semana
- Projeto reduz custos de R$ 200.000/ano → CoD = R$ 3.846/semana
- Projeto de compliance (evita multa de R$ 100k) → CoD = R$ 1.923/semana

**Dica:** Se não souber o valor exato, compare relativamente:
- Projeto crítico: R$ 10.000/semana
- Projeto importante: R$ 5.000/semana
- Projeto normal: R$ 2.000/semana

---

### WSJF Components

#### 1. Business Value (0-100)
**Pergunta:** Quanto valor este projeto traz para o negócio?

**Escala:**
- 90-100: Projeto estratégico, impacto direto na receita
- 70-89: Projeto importante, melhora significativa
- 50-69: Projeto relevante, benefício moderado
- 30-49: Projeto útil, benefício pequeno
- 0-29: Projeto de suporte, sem impacto direto

**Exemplos:**
- Sistema de vendas online: 95
- Melhoria de performance: 70
- Automação interna: 50
- Refactoring de código: 30

---

#### 2. Time Criticality (0-100)
**Pergunta:** Quão urgente é este projeto?

**Escala:**
- 90-100: Deadline externo rígido (regulatório, contrato)
- 70-89: Janela de oportunidade limitada
- 50-69: Importância temporal moderada
- 30-49: Pode esperar alguns meses
- 0-29: Sem urgência específica

**Exemplos:**
- Compliance LGPD (deadline): 100
- Black Friday (sazonal): 90
- Melhoria de UX: 50
- Documentação técnica: 20

---

#### 3. Risk Reduction (0-100)
**Pergunta:** Quanto este projeto reduz riscos para a organização?

**Escala:**
- 90-100: Elimina riscos críticos (segurança, compliance)
- 70-89: Reduz riscos significativos
- 50-69: Reduz riscos moderados
- 30-49: Reduz riscos pequenos
- 0-29: Não reduz riscos

**Exemplos:**
- Migração de servidor legado: 95
- Implementar backup automatizado: 85
- Adicionar monitoramento: 60
- Nova feature de UI: 10

---

## 📝 Passo a Passo Completo

### Etapa 1: Criar Portfolio
1. Acesse `/portfolio`
2. Clique "Novo Portfolio"
3. Preencha:
   - Nome: "Portfolio Q1 2025"
   - Orçamento: R$ 1.000.000
   - Capacidade: 15 FTE
4. Salvar

### Etapa 2: Adicionar Projetos
1. Selecione o portfolio criado
2. Clique "Adicionar Projeto"
3. Selecione um projeto da lista
4. Configure:
   - Prioridade: 1 (alta)
   - CoD: R$ 5.000/semana
   - Business Value: 85
   - Time Criticality: 70
   - Risk Reduction: 60
5. Clique "Adicionar"
6. Repita para 2-3 projetos

### Etapa 3: Executar Forecasts (CRÍTICO!)
Para **cada projeto** adicionado:
1. Vá em: Projetos → Selecione o projeto
2. Clique "Executar Forecast"
3. Aguarde simulação (10-30 segundos)
4. Verifique mensagem de sucesso
5. Repita para todos os projetos

⚠️ **Sem forecasts salvos, a análise CoD falhará!**

### Etapa 4: Executar CoD Analysis
1. Volte para `/portfolio`
2. Selecione o portfolio
3. Clique "CoD Analysis" (botão amarelo)
4. Aguarde 2-5 segundos
5. Veja os resultados!

---

## 📊 Interpretando os Resultados

### Ranking WSJF
A tabela mostra a **ordem recomendada de execução**:

| # | Projeto | WSJF | Duração | CoD |
|---|---------|------|---------|-----|
| 1 | Projeto A | 8.5 | 6 sem | R$ 10k/sem |
| 2 | Projeto B | 6.2 | 4 sem | R$ 5k/sem |
| 3 | Projeto C | 4.1 | 8 sem | R$ 2k/sem |

**Como ler:**
- **#1 = fazer primeiro** (maior WSJF)
- **Última posição = fazer por último** (menor WSJF)
- WSJF alto = máximo valor em mínimo tempo

---

### Comparação de Estratégias

O sistema compara 4 abordagens:

1. **WSJF** ⭐ Recomendado
   - Balanceia valor, urgência e duração
   - Geralmente a melhor economia

2. **SJF (Shortest Job First)**
   - Menor duração primeiro
   - Bom para "quick wins"

3. **CoD-First**
   - Maior CoD primeiro
   - Foco em evitar perdas

4. **BV-First (Business Value First)**
   - Maior valor de negócio primeiro
   - Ignora urgência e duração

---

### Economia Calculada

```
Exemplo de resultado:

CoD Sequencial (não otimizado): R$ 311.250 ❌
CoD Sequencial (WSJF otimizado): R$ 189.750 ✅
Economia: R$ 121.500 (39% redução)
```

**O que significa:**
- Executar na ordem atual: perda de R$ 311k
- Executar na ordem WSJF: perda de R$ 189k
- **Economia total: R$ 121k** simplesmente reordenando!

---

## ⚠️ Troubleshooting (Resolução de Problemas)

### Erro: "Nenhum projeto no portfolio"
**Causa:** Portfolio vazio

**Solução:**
1. Clique "Adicionar Projeto"
2. Adicione pelo menos 1 projeto
3. Tente novamente

---

### Erro: "X projeto(s) sem forecast"
**Causa:** Projetos sem forecast executado

**Solução:**
Para cada projeto listado no erro:
1. Vá em Projetos → [Nome do Projeto]
2. Clique "Executar Forecast"
3. Aguarde conclusão
4. Volte ao Portfolio
5. Execute CoD Analysis novamente

**Exemplo de erro:**
```
Não foi possível executar análise CoD

Projetos sem forecast:
• Projeto Marketing
• Projeto Mobile App

Ação: Vá em Projetos → Selecionar projeto → Executar forecast
```

---

### Warning: "X projeto(s) sem Cost of Delay configurado"
**Causa:** CoD não preenchido (não é bloqueante)

**Impacto:** Projetos sem CoD terão valor 0 na análise

**Solução (Opcional):**
1. Clique "Editar" no projeto
2. Preencha "Cost of Delay (R$/semana)"
3. Salve
4. Execute CoD Analysis novamente

---

### Forecasts estão desatualizados
**Sintoma:** Resultados não batem com mudanças recentes

**Solução:**
1. Re-execute forecasts dos projetos
2. Execute CoD Analysis novamente
3. Forecasts são salvos e não se atualizam automaticamente

---

## 💡 Dicas de Uso

### 1. Comece Simples
- Primeiro portfolio: 3-5 projetos
- Use valores estimados para CoD
- Ajuste conforme ganha experiência

### 2. Revise Regularmente
- Execute CoD Analysis a cada 2 semanas
- Ajuste métricas quando prioridades mudarem
- Re-execute forecasts se escopo mudar

### 3. Combine com Simulação
- Use "Simular" para ver duração paralela vs sequencial
- Use "CoD Analysis" para decidir ordem de execução
- Combinados = máximo poder de decisão

### 4. Documente Decisões
- Salve screenshots dos rankings WSJF
- Explique aos stakeholders usando os números
- Mostre a economia calculada

### 5. Calibre as Métricas
- Revise WSJF scores com o time
- Ajuste Business Value/Time Criticality se necessário
- Consistência é mais importante que precisão absoluta

---

## 📚 Fórmula WSJF Completa

```
WSJF = (BV + TC + RR) / Duration

Onde:
BV = Business Value (0-100)
TC = Time Criticality (0-100)
RR = Risk Reduction (0-100)
Duration = Duração do projeto em semanas (P85 do forecast)

Projeto com WSJF ALTO = fazer PRIMEIRO
```

**Exemplo:**
```
Projeto A:
BV = 85
TC = 70
RR = 60
Duration = 10 semanas

WSJF = (85 + 70 + 60) / 10 = 21.5

Projeto B:
BV = 50
TC = 90
RR = 40
Duration = 15 semanas

WSJF = (50 + 90 + 40) / 15 = 12.0

Resultado: Projeto A vai PRIMEIRO (WSJF maior)
```

---

## 🎯 Checklist Rápido

Antes de executar CoD Analysis, verifique:

- [ ] Portfolio criado
- [ ] Pelo menos 2 projetos adicionados
- [ ] Todos projetos têm forecasts salvos
- [ ] Métricas configuradas (CoD, BV, TC, RR)
- [ ] Forecasts estão atualizados

**Se todos checkboxes marcados → Execute CoD Analysis!**

---

## 📞 Suporte

**Dúvidas ou problemas?**
- Revise este guia
- Confira tooltips nos campos (ícone ℹ️)
- Veja mensagens de erro detalhadas
- Consulte documentação técnica: `PORTFOLIO_PHASE2_SUMMARY.md`

---

**Última atualização:** 2025-11-07
**Versão:** 1.0
**Autor:** Flow Forecaster Team
