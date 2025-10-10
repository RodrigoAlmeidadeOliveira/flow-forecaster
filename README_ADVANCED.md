# Project Forecaster - Advanced ML & Monte Carlo Edition

Previsão probabilística de esforço e duração de projetos usando **Simulações Monte Carlo** e **Machine Learning**.

Esta é uma versão avançada que combina:
- **Simulação Monte Carlo** tradicional para análise probabilística
- **Machine Learning** (Random Forest, XGBoost, Gradient Boosting) para previsões baseadas em tendências
- **Visualizações avançadas** com matplotlib e seaborn

## 🚀 Novos Recursos

### Machine Learning Forecasting
- **Múltiplos modelos**: Random Forest, XGBoost, Hist Gradient Boosting
- **Ensemble forecasting**: Combina previsões de vários modelos
- **Intervalos de confiança**: P10, P25, P50, P75, P90
- **Avaliação de risco**: Analisa volatilidade e tendências insustentáveis
- **Validação temporal**: Cross-validation com time series split

### Visualizações Avançadas
- **Gráficos ML**: Previsões ensemble com intervalos de confiança
- **Análise histórica**: Distribuição, autocorrelação, tendências
- **Monte Carlo**: Distribuição de tempos, burn-down trajectories
- **Comparação**: ML vs Monte Carlo side-by-side

### APIs RESTful
- `/api/ml-forecast` - Previsão Machine Learning
- `/api/mc-throughput` - Simulação Monte Carlo de throughput
- `/api/combined-forecast` - Análise combinada ML + Monte Carlo

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Setup

1. Clone/baixe o repositório

2. Instale as dependências:
```bash
cd project-forecaster-py
pip install -r requirements.txt
```

As dependências incluem:
- Flask 3.0.0
- NumPy 1.26.2
- Pandas 2.1.4
- Matplotlib 3.8.2
- Seaborn 0.13.0
- scikit-learn 1.3.2
- XGBoost 2.0.3
- SciPy 1.11.4

## 🎯 Como Usar

### 1. Iniciar o Servidor

```bash
python app.py
```

Acesse: `http://localhost:8080`

### 2. Forecast Básico (Original)

Acesse a página principal `/` para:
- Simulações Monte Carlo tradicionais
- Análise de projetos com tarefas e riscos
- Curva-S de produtividade
- Compartilhamento de dados via URL

### 3. Forecast Avançado (Novo!)

Acesse `/advanced` para:

#### ML Forecast
1. Insira dados históricos de throughput (mínimo 8 semanas)
2. Configure parâmetros de previsão
3. Clique em "ML Forecast Only"

Você receberá:
- Previsões de 4+ modelos de ML
- Ensemble com intervalos de confiança
- Avaliação de risco (LOW/MEDIUM/HIGH)
- Métricas de performance (MAE, RMSE)
- Gráficos interativos

#### Monte Carlo Forecast
1. Insira throughput histórico
2. Defina o backlog de tarefas
3. Configure número de simulações
4. Clique em "Monte Carlo Only"

Você receberá:
- Distribuição de tempos de conclusão
- Percentis (P10, P50, P85, P90)
- Visualização de burn-downs
- Estatísticas detalhadas

#### Combined Forecast
Clique em "Run Combined Forecast" para executar ambas as análises e obter:
- Comparação lado a lado
- Gráfico comparativo ML vs MC
- Recomendações baseadas em risk assessment
- Análise completa com múltiplas visualizações

## 📊 Exemplos de Uso

### Exemplo 1: Previsão ML Simples

```python
# Via API
import requests

data = {
    "tpSamples": [5, 6, 7, 4, 8, 6, 5, 7, 6, 8],
    "forecastSteps": 4,
    "startDate": "2024-01-01"
}

response = requests.post('http://localhost:8080/api/ml-forecast', json=data)
results = response.json()

print(f"Risk Level: {results['risk_assessment']['risk_level']}")
print(f"Forecast: {results['ensemble_stats']['mean']}")
```

### Exemplo 2: Monte Carlo Throughput

```python
data = {
    "tpSamples": [5, 6, 7, 4, 8, 6, 5],
    "backlog": 50,
    "nSimulations": 10000
}

response = requests.post('http://localhost:8080/api/mc-throughput', json=data)
results = response.json()

print(f"P50: {results['percentile_stats']['p50']} weeks")
print(f"P85: {results['percentile_stats']['p85']} weeks")
```

## 🧠 Modelos de Machine Learning

### Random Forest
- Ensemble de árvores de decisão
- Robusto a outliers
- Bom para dados não-lineares

### XGBoost
- Gradient boosting otimizado
- Hyperparameter tuning automático
- Alta precisão

### Hist Gradient Boosting
- Quantile regression (P10, P50, P90)
- Rápido para datasets grandes
- Intervalos de confiança nativos

## 📈 Interpretação dos Resultados

### Risk Assessment
- **LOW**: Dados estáveis, ML confiável
- **MEDIUM**: Alguma volatilidade, use com cuidado
- **HIGH**: Alta incerteza, prefira Monte Carlo

### MAE (Mean Absolute Error)
- Erro médio absoluto em unidades de throughput
- Quanto menor, melhor
- MAE% mostra o erro relativo

### Percentis Monte Carlo
- **P50**: 50% de chance de terminar antes
- **P85**: 85% de confiança (recomendado para commitments)
- **P90**: 90% de confiança (cenário conservador)

## 🏗️ Arquitetura

```
project-forecaster-py/
├── app.py                      # Flask app e endpoints API
├── monte_carlo.py              # Simulações Monte Carlo
├── ml_forecaster.py            # Modelos de Machine Learning
├── visualization.py            # Geração de gráficos
├── requirements.txt            # Dependências Python
├── templates/
│   ├── index.html              # Página básica
│   └── advanced_forecast.html  # Página avançada ML/MC
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── ui.js               # UI básica
        ├── charts.js           # Charts.js básicos
        └── advanced_forecast.js # UI avançada
```

## 🔬 Metodologia

### Machine Learning
1. **Feature Engineering**: Lags (t-1, t-2, ..., t-n), rolling statistics
2. **Time Series Split**: Validação temporal (não aleatória)
3. **Hyperparameter Tuning**: RandomizedSearchCV
4. **Ensemble**: Combina previsões de múltiplos modelos
5. **Risk Assessment**: Analisa volatilidade, trends, outliers

### Monte Carlo
1. **Amostragem**: Seleciona aleatoriamente throughput histórico
2. **Simulação**: Executa milhares de cenários
3. **Distribuição**: Calcula percentis e estatísticas
4. **Burn-down**: Modela trajetórias de conclusão

## ⚠️ Limitações e Cuidados

### Machine Learning
- **Mínimo 8 amostras**: ML precisa de dados históricos
- **Extrapolação**: ML pode falhar em tendências extremas
- **Overfitting**: Validação cruzada mitiga mas não elimina
- **Concept drift**: Performance degrada se processo muda

### Monte Carlo
- **Estacionariedade**: Assume processo estável
- **Sample size**: Mais amostras = melhor distribuição
- **Riscos**: Modelagem de riscos é aproximada

## 🎓 Quando Usar Cada Método

### Use Machine Learning quando:
- Há tendências claras nos dados
- Deseja previsões pontuais
- Tem 8+ semanas de dados históricos
- Risk assessment é LOW ou MEDIUM

### Use Monte Carlo quando:
- Dados são voláteis ou instáveis
- Precisa de intervalos probabilísticos
- Modelar riscos e incertezas
- Risk assessment é HIGH

### Use Combined quando:
- Quer o melhor dos dois mundos
- Validar uma abordagem com a outra
- Apresentar para stakeholders (mais robusto)

## 🔧 Produção

Para deploy em produção, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 --timeout 120 app:app
```

Configurações recomendadas:
- Workers: 4-8 (dependendo do CPU)
- Timeout: 120s (para simulações grandes)
- Nginx como reverse proxy
- HTTPS/SSL obrigatório

## 📚 Referências

- **Monte Carlo**: Troy Magennis' Throughput Forecaster
- **ML**: scikit-learn, XGBoost documentation
- **Kanban Metrics**: "Actionable Agile Metrics" by Daniel Vacanti

## 📝 Licença

MIT License

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro.

## 📧 Suporte

- Issues: GitHub Issues
- Documentação: Consulte MIGRATION_GUIDE.md para detalhes sobre a unificação dos métodos Monte Carlo

---

**Versão**: 2.0.0 - Advanced ML & Monte Carlo Edition
**Desenvolvido**: Python ML Edition
