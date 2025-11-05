# Features de Machine Learning para Flow-Forecaster

**Baseado em:** Análise do notebook `03_ferramentas_machine_learning.ipynb`
**Data:** 2025-11-05

---

## 🎯 **Prioridade Alta - Predição de Prazos**

### 1. Regressão Linear para Duração de Projetos
- Implementar modelo de predição baseado em características do projeto (escopo, equipe, complexidade)
- Adicionar features:
  - `tamanho_equipe`: Número de pessoas no time
  - `experiencia_pm`: Anos de experiência do PM
  - `orcamento_inicial`: Budget em R$
  - `num_stakeholders`: Quantidade de stakeholders
  - `escopo_inicial`: Story points ou tamanho estimado
  - `mudancas_escopo`: Número de mudanças esperadas/ocorridas
  - `indice_maturidade_org`: Maturidade da organização (1-5)
  - `tipo_projeto`: Categoria (ERP, CRM, Analytics, Mobile, Web)
  - `complexidade`: Baixa, Média, Alta
- Exibir intervalos de confiança (P50, P90, P95) para as predições
- Permitir calibração do modelo com dados históricos do usuário

**Métricas esperadas:** MAE de 1-2 meses, R² > 0.70

### 2. Pipeline de Pré-processamento
- `StandardScaler` para normalização de features numéricas
- `PolynomialFeatures` para capturar relações não-lineares (interações)
- Encoding de variáveis categóricas (one-hot encoding)
- Pipeline sklearn completo: `Pipeline([scaler, poly, regressor])`

### 3. Validação e Métricas de Qualidade
- Cross-validation (k-fold) para avaliar performance dos modelos
- Exibir métricas na UI:
  - **MAE** (Mean Absolute Error): Erro médio em meses
  - **RMSE** (Root Mean Squared Error): Penaliza erros grandes
  - **R² Score**: Qualidade do ajuste (0-1)
- Análise de resíduos e detecção de outliers
- Gráficos: Predito vs Real, Distribuição de resíduos

---

## 🔥 **Prioridade Alta - Custo de Atraso (CoD)**

### 4. Random Forest para Estimativa de CoD
- Modelo para prever custo de atraso semanal (R$/semana)
- Features incluem:
  - Todas as features de duração
  - `duracao_real` ou `duracao_predita`
  - `atraso_semanas`: Calculado como `(duração_real - duração_baseline) × 4.33`
- Feature importance automática para identificar fatores críticos
- Melhor performance que regressão linear para relações complexas

**Vantagens do RF:**
- Captura não-linearidades
- Robusto a outliers
- Não requer normalização
- Feature importance nativa

### 5. Cálculo Dinâmico de CoD
- Integrar duração predita para estimar custo total de atraso
- Fórmula: `custo_total_atraso = custo_semanal × semanas_atraso`
- Permitir input customizado de fatores de CoD por projeto:
  - Impacto no mercado (perda de share)
  - Penalidades contratuais
  - Custo de oportunidade
  - Impacto reputacional

### 6. Visualização de Feature Importance
- Gráfico de barras mostrando quais fatores mais impactam o CoD
- Insights acionáveis:
  - Exemplo: "Reduzir mudanças de escopo diminui 30% do risco"
  - "Aumentar experiência do PM reduz 20% do CoD esperado"
- Comparação de importância entre modelos diferentes

---

## ⚙️ **Prioridade Média - Otimização e Modelos Avançados**

### 7. Grid Search para Hiperparâmetros
- Otimização automática de Random Forest:
  - `n_estimators`: [50, 100, 200]
  - `max_depth`: [8, 10, 12, None]
  - `min_samples_split`: [2, 5, 10]
  - `min_samples_leaf`: [1, 2, 4]
- Salvar/carregar configurações otimizadas (pickle/joblib)
- Interface para ajuste manual de parâmetros (modo avançado)
- Exibir melhor score de cross-validation

### 8. Gradient Boosting como Alternativa
- Implementar `GradientBoostingRegressor` para comparação
- Parâmetros:
  - `n_estimators=100`
  - `learning_rate=0.1`
  - `max_depth=8`
- Seleção automática do melhor modelo (RF vs GB)
- Comparação lado a lado das métricas

### 9. Modelos de Ensemble
- Combinar predições de múltiplos modelos (voting/averaging)
- Estratégias:
  - **Voting**: Média ponderada por performance
  - **Stacking**: Meta-modelo que aprende a combinar
- Melhorar robustez das estimativas
- Reduzir variância das predições

---

## 🔬 **Prioridade Média - Integração ML + Monte Carlo**

### 10. Simulação Unificada ML + Monte Carlo
- Classe `PreditorProjetos` que combina ML e simulações estocásticas
- Fluxo:
  1. ML prediz duração e CoD base
  2. Monte Carlo gera variações probabilísticas
  3. Cada simulação usa ML para refinar predições
- Gerar distribuições de resultados usando predições ML como base
- Variar parâmetros de entrada com incerteza:
  - `np.random.triangular(0.8, 1.0, 1.3)` para escopo
  - `np.random.poisson(2)` para mudanças de escopo
  - `np.random.normal(1.0, 0.1)` para orçamento

**Exemplo de código:**
```python
def simular_projeto_completo(projeto_base, n_simulacoes=1000):
    for _ in range(n_simulacoes):
        # Variar parâmetros com incerteza
        sim_projeto = aplicar_incerteza(projeto_base)

        # Predição ML de duração
        duracao = modelo_duracao.predict(sim_projeto)

        # Predição ML de CoD
        sim_projeto['duracao_real'] = duracao
        cod = modelo_cod.predict(sim_projeto)

        resultados.append({duracao, cod, custo_total})
```

### 11. Métricas de Risco Avançadas
- Probabilidade de atraso > X meses
- Probabilidade de custo de atraso > R$ Y
- Análise de sensibilidade (quais variáveis têm maior impacto)
- Métricas por percentil:
  - P50 (mediana)
  - P90 (pessimista)
  - P95 (muito pessimista)
  - P99 (worst case)

### 12. Visualizações Integradas
- **Histogramas de distribuição:**
  - Duração do projeto
  - CoD semanal
  - Custo total de atraso
- **Scatter plots de correlação:**
  - Duração vs Custo
  - Features vs Target
- **Box plots por categoria:**
  - Tipo de projeto
  - Complexidade
  - Tamanho de equipe
- **Heatmap de correlação** entre features
- **Gráficos de predição vs real** (após projeto concluir)

---

## 📊 **Prioridade Baixa - Dados Históricos e Aprendizado**

### 13. Sistema de Dados Históricos
- Permitir upload de CSV/Excel com projetos passados
- Formato esperado:
  - Colunas de features (tamanho_equipe, escopo, etc.)
  - Colunas de targets (duracao_real, custo_final, cod)
- Auto-treinamento dos modelos com dados do usuário
- Versionamento de modelos treinados (timestamp, hash)
- Comparação de performance: modelo genérico vs modelo customizado

### 14. Comparação Predição vs Real
- Após conclusão do projeto, comparar predição com resultado real
- Gráficos de "Predito vs Real" com linha de referência
- Calcular erro absoluto e percentual
- Melhorar modelos automaticamente com feedback:
  - Re-treinar com novos dados
  - Ajustar pesos do ensemble
- Dashboard de acurácia histórica

### 15. Gerador de Dados Sintéticos
- Função `gerar_dados_projetos(n=500)` para demonstração
- Permitir usuários testarem sem dados históricos
- Parâmetros configuráveis:
  - Tipo de organização (startup, enterprise)
  - Maturidade da organização
  - Mix de tipos de projeto
  - Distribuição de complexidade
- Dados sintéticos seguem regras realistas do notebook

---

## 🧪 **Prioridade Baixa - Features Experimentais**

### 16. Análise de Causas de Atraso
- Identificar padrões em projetos atrasados
- Clustering (K-Means, DBSCAN) para agrupar projetos similares
- Análise de clusters:
  - "Projetos com muitas mudanças de escopo"
  - "Projetos com equipes pequenas em projetos complexos"
- Recomendações baseadas em projetos bem-sucedidos:
  - "Projetos similares que deram certo tinham PM com +10 anos"

### 17. Alertas Preditivos
- Notificar quando projeto tem alta probabilidade de atraso
- Sistema de "semáforo":
  - 🟢 Verde: P(atraso) < 30%
  - 🟡 Amarelo: 30% ≤ P(atraso) < 60%
  - 🔴 Vermelho: P(atraso) ≥ 60%
- Integração com email/Slack para alertas automáticos
- Dashboard de projetos em risco

### 18. Otimização de Portfólio
- Usar ML para sugerir priorização de projetos
- Maximizar valor entregue vs risco total
- Formulação como problema de otimização:
  - Restrições: orçamento, recursos, prazos
  - Objetivo: maximizar NPV ou minimizar risco agregado
- Algoritmos: Programação Linear, Algoritmos Genéticos

### 19. Modelo de Sucesso do Projeto
- Classificação binária (sucesso/falha)
- Features:
  - Todas as features anteriores
  - Métricas de qualidade
  - Satisfação do cliente
- Identificar fatores críticos de sucesso
- Probabilidade de sucesso em tempo real

### 20. Export de Modelos Treinados
- Salvar modelos em formato pickle/joblib
- Compartilhar modelos entre equipes
- API REST para predições em batch
- Documentação automática do modelo:
  - Features utilizadas
  - Performance (MAE, R²)
  - Data de treinamento
  - Número de amostras

---

## 🎓 **Sugestões de Implementação Incremental**

### **Fase 1 (MVP ML) - 2-3 semanas**
- ✅ Feature #1: Regressão Linear para duração
- ✅ Feature #4: Random Forest para CoD
- ✅ Feature #10: Integração básica ML + Monte Carlo
- ✅ UI básica para input de features
- ✅ Visualização de resultados (histogramas)

**Entregável:** Usuário pode inserir características do projeto e receber predição de duração e CoD com distribuições probabilísticas.

### **Fase 2 (Otimização) - 2 semanas**
- ✅ Feature #7: Grid Search para hiperparâmetros
- ✅ Feature #3: Métricas de validação (MAE, R², CV)
- ✅ Feature #12: Visualizações integradas (scatter, boxplot, heatmap)
- ✅ Comparação de modelos lado a lado
- ✅ Documentação de uso

**Entregável:** Modelos otimizados com métricas de qualidade visíveis. Visualizações ricas para análise.

### **Fase 3 (Dados Históricos) - 3-4 semanas**
- ✅ Feature #13: Sistema de upload de dados (CSV/Excel)
- ✅ Feature #14: Comparação predição vs real
- ✅ Feature #2: Pipeline completo de pré-processamento
- ✅ Auto-treinamento com dados do usuário
- ✅ Persistência de modelos

**Entregável:** Sistema que aprende com dados da organização. Acurácia melhora com uso.

### **Fase 4 (Avançado) - 4-6 semanas**
- ✅ Features #16-20: Análise de causas, alertas, otimização de portfólio
- ✅ API REST para integrações
- ✅ Dashboard executivo
- ✅ Sistema de alertas automáticos
- ✅ Clustering e análise de padrões

**Entregável:** Plataforma completa de gestão de portfólio com ML.

---

## 📚 **Referências Técnicas**

### Bibliotecas Python Necessárias
```python
numpy >= 1.20.0
pandas >= 1.3.0
matplotlib >= 3.5.0
seaborn >= 0.11.0
scipy >= 1.7.0
scikit-learn >= 1.0.0
joblib >= 1.1.0  # Para salvar modelos
```

### Modelos Implementados no Notebook
1. **LinearRegression** - Baseline simples
2. **Ridge** - Regressão linear com regularização L2
3. **ElasticNet** - Regularização L1 + L2
4. **RandomForestRegressor** - Ensemble de árvores de decisão
5. **GradientBoostingRegressor** - Boosting sequencial

### Métricas de Avaliação
- **MAE** (Mean Absolute Error): Erro médio absoluto
- **RMSE** (Root Mean Squared Error): Penaliza erros grandes
- **R² Score**: Proporção da variância explicada (0-1)
- **Cross-validation score**: Validação cruzada k-fold

### Estrutura de Dados Esperada
```python
{
    'tamanho_equipe': int,
    'experiencia_pm': int (anos),
    'orcamento_inicial': float (R$ milhões),
    'num_stakeholders': int,
    'escopo_inicial': float (story points),
    'mudancas_escopo': int,
    'indice_maturidade_org': float (1-5),
    'tipo_projeto': str ['ERP', 'CRM', 'Analytics', 'Mobile', 'Web'],
    'complexidade': str ['Baixa', 'Média', 'Alta']
}
```

---

## 🚀 **Impacto Esperado**

Implementar estas features transformaria o **flow-forecaster** de uma ferramenta de simulação Monte Carlo pura em uma **plataforma completa de gestão de riscos e portfólio** que:

1. **Aprende com dados históricos** da organização
2. **Prediz com acurácia** duração e custos de atraso
3. **Identifica fatores críticos** de sucesso/falha
4. **Alerta proativamente** sobre riscos
5. **Otimiza priorização** de portfólio
6. **Melhora continuamente** com feedback

**Diferencial competitivo:** Combinação única de ML + Monte Carlo que nenhuma ferramenta similar oferece hoje.

---

## 📝 **Próximos Passos**

1. Revisar e priorizar features com stakeholders
2. Criar protótipo da Fase 1 (MVP ML)
3. Validar UX/UI com usuários
4. Implementar testes automatizados
5. Documentar API e modelos
6. Preparar ambiente de produção

**Estimativa total:** 11-16 semanas para implementação completa (Fases 1-4)
