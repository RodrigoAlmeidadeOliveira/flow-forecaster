# 📊 Project Forecaster - ML & Monte Carlo Edition

> Previsão probabilística de projetos usando **Machine Learning** e **Simulações Monte Carlo**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Uma ferramenta web avançada para forecasting de projetos que combina técnicas estatísticas tradicionais com Machine Learning moderno.

## 🎯 Funcionalidades

### Monte Carlo Tradicional
- ✅ Simulação probabilística com milhares de cenários
- ✅ Modelagem de riscos e incertezas
- ✅ Curva-S de produtividade
- ✅ Análise de throughput e lead-times
- ✅ Compartilhamento via URL

### Machine Learning (NOVO!)
- 🤖 **4 modelos**: Random Forest, XGBoost, Gradient Boosting
- 📈 **Ensemble forecasting** com intervalos de confiança
- 🎯 **Risk assessment** automático (LOW/MEDIUM/HIGH)
- 📊 **Visualizações avançadas** com matplotlib/seaborn
- 🔍 **Time series validation** com cross-validation

### Visualizações
- 📉 Gráficos de previsão ML com intervalos P10-P90
- 📊 Análise histórica (distribuição, autocorrelação, tendências)
- 🎲 Distribuição Monte Carlo e burn-down trajectories
- ⚖️ Comparação lado a lado ML vs Monte Carlo

## 🚀 Quick Start

### Instalação

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/project-forecaster-py.git
cd project-forecaster-py

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app.py
```

Acesse: **http://localhost:8080**

### Docker (Opcional)

```bash
docker build -t project-forecaster .
docker run -p 8080:8080 project-forecaster
```

## 📖 Como Usar

### Forecast Básico
1. Acesse `/` para simulações Monte Carlo tradicionais
2. Insira dados do projeto e histórico de throughput
3. Configure riscos e parâmetros de simulação
4. Execute e visualize resultados probabilísticos

### Forecast Avançado (ML + Monte Carlo)
1. Acesse `/advanced` para análise combinada
2. Insira pelo menos **8 semanas** de throughput histórico
3. Configure backlog e parâmetros
4. Escolha entre:
   - **ML Only**: Previsão baseada em tendências
   - **Monte Carlo Only**: Análise probabilística
   - **Combined**: Comparação completa

## 🧠 Modelos de Machine Learning

| Modelo | Características | Quando Usar |
|--------|----------------|-------------|
| **Random Forest** | Robusto, ensemble de árvores | Baseline, dados não-lineares |
| **XGBoost** | Alta precisão, auto-tuning | Máxima acurácia |
| **Hist Gradient Boosting** | Quantile regression (P10, P90) | Intervalos de confiança |

## 📊 Exemplo de API

### ML Forecast
```python
import requests

data = {
    "tpSamples": [5, 6, 7, 4, 8, 6, 5, 7, 6, 8],
    "forecastSteps": 4,
    "startDate": "2024-01-01"
}

response = requests.post('http://localhost:8080/api/ml-forecast', json=data)
results = response.json()

print(f"Risk: {results['risk_assessment']['risk_level']}")
print(f"Forecast: {results['ensemble_stats']['mean']}")
```

### Monte Carlo
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

## 📁 Estrutura do Projeto

```
project-forecaster-py/
├── app.py                      # Flask application
├── monte_carlo.py              # Simulações Monte Carlo
├── ml_forecaster.py            # Modelos de Machine Learning
├── visualization.py            # Geração de gráficos
├── requirements.txt            # Dependências Python
├── templates/
│   ├── index.html              # Interface básica
│   └── advanced_forecast.html  # Interface ML/MC avançada
└── static/
    ├── css/style.css
    └── js/
        ├── ui.js
        ├── charts.js
        └── advanced_forecast.js
```

## 🔧 APIs RESTful

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/simulate` | POST | Simulação Monte Carlo tradicional |
| `/api/ml-forecast` | POST | Previsão Machine Learning |
| `/api/mc-throughput` | POST | Monte Carlo simplificado |
| `/api/combined-forecast` | POST | Análise combinada ML + MC |

## 📚 Documentação Completa

Para documentação detalhada, veja [README_ADVANCED.md](README_ADVANCED.md)

## 🎓 Quando Usar Cada Método

### Use Machine Learning quando:
- ✅ Existem tendências claras nos dados
- ✅ Você tem 8+ semanas de histórico
- ✅ Precisa de previsões pontuais
- ✅ Risk assessment é LOW ou MEDIUM

### Use Monte Carlo quando:
- ✅ Dados são voláteis ou instáveis
- ✅ Precisa modelar riscos e incertezas
- ✅ Quer intervalos probabilísticos
- ✅ Risk assessment é HIGH

### Use Combined quando:
- ✅ Quer validar uma abordagem com a outra
- ✅ Precisa de análise robusta para stakeholders
- ✅ Deseja o melhor dos dois mundos

## 🛠️ Tecnologias

- **Backend**: Flask 3.0
- **ML**: scikit-learn, XGBoost
- **Visualização**: matplotlib, seaborn
- **Estatística**: NumPy, SciPy, Pandas
- **Frontend**: Bootstrap 4, jQuery, Chart.js

## 📈 Screenshots

### Interface Avançada
![Advanced Forecast](docs/screenshot-advanced.png)

### Gráficos ML
![ML Charts](docs/screenshot-ml.png)

### Comparação
![Comparison](docs/screenshot-comparison.png)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## 🙏 Créditos

- **Conceito Original**: [Troy Magennis](https://github.com/FocusedObjective/FocusedObjective.Resources) - Throughput Forecaster
- **Versão JavaScript**: [Rodrigo Rosauro](https://github.com/rodrigozr/ProjectForecaster) - ProjectForecaster
- **Migração Python + ML**: Esta versão

## 📧 Contato

- Issues: [GitHub Issues](https://github.com/SEU-USUARIO/project-forecaster-py/issues)
- Documentação: [Wiki](https://github.com/rodrigozr/ProjectForecaster/wiki)

## ⭐ Star History

Se este projeto foi útil, considere dar uma ⭐ no GitHub!

---

**Versão**: 2.0.0 - Advanced ML & Monte Carlo Edition
# project-forecaster-py
# project-forecaster-py
# project-forecaster-py
