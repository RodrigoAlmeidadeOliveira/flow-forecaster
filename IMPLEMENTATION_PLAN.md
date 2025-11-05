# Plano de Implementação - Features Faltantes do Flow-Forecaster

**Data:** 2025-11-05
**Versão:** 1.0
**Baseado em:** FEATURES_IMPLEMENTED_VS_ROADMAP.md

---

## 📋 Índice

1. [Feature #4 + #5: Sistema de Custo de Atraso (CoD)](#feature-4--5-sistema-de-custo-de-atraso-cod)
2. [Feature #6: Visualização de Feature Importance](#feature-6-visualização-de-feature-importance)
3. [Feature #12: Visualizações Avançadas](#feature-12-visualizações-avançadas)
4. [Feature #13: Upload de Dados Históricos](#feature-13-upload-de-dados-históricos)
5. [Feature #16: Análise de Causas com Clustering](#feature-16-análise-de-causas-com-clustering)
6. [Feature #18: Otimização Matemática de Portfólio](#feature-18-otimização-matemática-de-portfólio)
7. [Feature #19: Modelo de Sucesso do Projeto](#feature-19-modelo-de-sucesso-do-projeto)
8. [Feature #20: Persistência e Export de Modelos](#feature-20-persistência-e-export-de-modelos)

---

# Feature #4 + #5: Sistema de Custo de Atraso (CoD)

## 🎯 Objetivo
Implementar sistema completo de previsão e cálculo de Custo de Atraso (Cost of Delay) usando Random Forest.

## 📊 Status Atual
❌ **Não Implementado**

## 🔧 Componentes a Implementar

### 1. Backend - Módulo de CoD

#### Arquivo: `cod_forecaster.py`

```python
"""
Cost of Delay (CoD) Forecaster
Random Forest model for predicting weekly delay cost
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings('ignore')


class CoDForecaster:
    """
    Machine Learning forecaster for Cost of Delay (CoD) estimation.
    Predicts weekly delay cost (R$/week) based on project characteristics.
    """

    def __init__(self, n_splits: int = 5):
        """
        Initialize CoD Forecaster.

        Args:
            n_splits: Number of K-folds for cross-validation
        """
        self.n_splits = n_splits
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained = False

    def prepare_features(self, projects_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for CoD prediction.

        Args:
            projects_df: DataFrame with project characteristics

        Expected columns:
            - budget_millions: Budget in R$ millions
            - duration_weeks: Expected duration in weeks
            - team_size: Number of people
            - num_stakeholders: Number of stakeholders
            - business_value: Business value score (0-100)
            - complexity: Complexity level (1-5)
            - project_type: Type (encoded)
            - risk_level: Risk level (encoded)
            - cod_weekly: Target - weekly CoD in R$ (for training)

        Returns:
            X: Feature matrix
            y: Target variable (cod_weekly)
        """
        # Feature engineering
        features = pd.DataFrame()

        # Direct features
        features['budget_millions'] = projects_df['budget_millions']
        features['duration_weeks'] = projects_df['duration_weeks']
        features['team_size'] = projects_df['team_size']
        features['num_stakeholders'] = projects_df['num_stakeholders']
        features['business_value'] = projects_df['business_value']
        features['complexity'] = projects_df['complexity']

        # Derived features
        features['budget_per_week'] = projects_df['budget_millions'] * 1_000_000 / projects_df['duration_weeks']
        features['budget_per_person'] = projects_df['budget_millions'] * 1_000_000 / projects_df['team_size']
        features['stakeholder_density'] = projects_df['num_stakeholders'] / projects_df['team_size']
        features['value_per_week'] = projects_df['business_value'] / projects_df['duration_weeks']
        features['risk_complexity_score'] = projects_df['risk_level'] * projects_df['complexity']

        # One-hot encoding for categorical
        if 'project_type' in projects_df.columns:
            type_dummies = pd.get_dummies(projects_df['project_type'], prefix='type')
            features = pd.concat([features, type_dummies], axis=1)

        # Store feature names
        self.feature_names = features.columns.tolist()

        # Target
        y = projects_df['cod_weekly'] if 'cod_weekly' in projects_df.columns else None

        return features, y

    def train_models(self, projects_df: pd.DataFrame):
        """
        Train multiple CoD prediction models.

        Args:
            projects_df: Historical projects with actual CoD data
        """
        X, y = self.prepare_features(projects_df)

        if y is None or len(X) < 10:
            raise ValueError("Insufficient training data. Need at least 10 projects with CoD data.")

        print(f"\n{'='*60}")
        print(f"CoD MODEL TRAINING - K-FOLD CROSS-VALIDATION")
        print(f"{'='*60}")
        print(f"Total samples: {len(X)}")
        print(f"Features: {len(self.feature_names)}")
        print(f"{'='*60}\n")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Model configurations
        models_config = {
            'RandomForest': RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=3,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=150,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            )
        }

        # Train and evaluate each model
        for name, model in models_config.items():
            print(f"\n{name} - Training:")
            print("-" * 60)

            # K-Fold Cross-Validation
            kfold = KFold(n_splits=self.n_splits, shuffle=True, random_state=42)
            fold_maes = []

            for fold_num, (train_idx, val_idx) in enumerate(kfold.split(X_train_scaled), 1):
                X_fold_train = X_train_scaled[train_idx]
                X_fold_val = X_train_scaled[val_idx]
                y_fold_train = y_train.iloc[train_idx]
                y_fold_val = y_train.iloc[val_idx]

                # Train
                model.fit(X_fold_train, y_fold_train)

                # Predict
                y_pred = model.predict(X_fold_val)
                mae = mean_absolute_error(y_fold_val, y_pred)
                fold_maes.append(mae)

                print(f"Fold {fold_num}: MAE = R$ {mae:,.0f}/semana")

            # Summary
            print(f"\nCross-Validation Summary:")
            print(f"  MAE: R$ {np.mean(fold_maes):,.0f} ± {np.std(fold_maes):,.0f}")

            # Final training on full training set
            model.fit(X_train_scaled, y_train)

            # Test set evaluation
            y_pred_test = model.predict(X_test_scaled)
            mae_test = mean_absolute_error(y_test, y_pred_test)
            rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
            r2_test = r2_score(y_test, y_pred_test)
            mape_test = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

            print(f"\nTest Set Performance:")
            print(f"  MAE:  R$ {mae_test:,.0f}/semana")
            print(f"  RMSE: R$ {rmse_test:,.0f}/semana")
            print(f"  R²:   {r2_test:.3f}")
            print(f"  MAPE: {mape_test:.1f}%")

            # Store model
            self.models[name] = {
                'model': model,
                'mae': mae_test,
                'rmse': rmse_test,
                'r2': r2_test,
                'mape': mape_test
            }

        self.trained = True
        print(f"\n{'='*60}")
        print(f"CoD TRAINING COMPLETE - {len(self.models)} models trained")
        print(f"{'='*60}\n")

    def predict_cod(self, project: Dict, model_name: str = 'RandomForest') -> Dict:
        """
        Predict Cost of Delay for a project.

        Args:
            project: Dictionary with project characteristics
            model_name: Name of model to use

        Returns:
            Dictionary with CoD predictions
        """
        if not self.trained:
            raise ValueError("Models not trained. Call train_models() first.")

        # Prepare features
        project_df = pd.DataFrame([project])
        X, _ = self.prepare_features(project_df)
        X_scaled = self.scaler.transform(X)

        # Predict with selected model
        model = self.models[model_name]['model']
        cod_weekly = model.predict(X_scaled)[0]

        # Get predictions from all models (for ensemble)
        all_predictions = []
        for m_name, m_data in self.models.items():
            pred = m_data['model'].predict(X_scaled)[0]
            all_predictions.append(pred)

        cod_weekly_mean = np.mean(all_predictions)
        cod_weekly_std = np.std(all_predictions)

        return {
            'cod_weekly': float(cod_weekly),
            'cod_weekly_mean': float(cod_weekly_mean),
            'cod_weekly_std': float(cod_weekly_std),
            'cod_daily': float(cod_weekly / 7),
            'cod_monthly': float(cod_weekly * 4.33),
            'model_used': model_name,
            'confidence_interval_95': (
                float(cod_weekly_mean - 1.96 * cod_weekly_std),
                float(cod_weekly_mean + 1.96 * cod_weekly_std)
            )
        }

    def calculate_total_cod(self, cod_weekly: float, delay_weeks: float) -> Dict:
        """
        Calculate total Cost of Delay.

        Args:
            cod_weekly: Weekly CoD in R$
            delay_weeks: Number of weeks delayed

        Returns:
            Dictionary with total CoD calculations
        """
        total_cod = cod_weekly * delay_weeks

        return {
            'cod_weekly': float(cod_weekly),
            'delay_weeks': float(delay_weeks),
            'total_cod': float(total_cod),
            'total_cod_formatted': f"R$ {total_cod:,.2f}"
        }

    def get_feature_importance(self, model_name: str = 'RandomForest') -> pd.DataFrame:
        """
        Get feature importance from trained model.

        Args:
            model_name: Name of model

        Returns:
            DataFrame with feature importance
        """
        if not self.trained:
            raise ValueError("Models not trained.")

        model = self.models[model_name]['model']

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_

            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)

            return importance_df
        else:
            return None
```

#### Arquivo: `models.py` (adicionar ao existente)

```python
# Adicionar ao models.py existente

class CoDConfiguration(Base):
    """Configuration for Cost of Delay calculation"""
    __tablename__ = 'cod_configurations'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))

    # CoD Factors
    market_impact_weight = Column(Float, default=1.0)  # Loss of market share
    contractual_penalties = Column(Float, default=0.0)  # R$/week
    opportunity_cost = Column(Float, default=0.0)  # R$/week
    reputational_impact = Column(Float, default=0.0)  # R$/week

    # Calculated CoD
    predicted_cod_weekly = Column(Float)
    actual_cod_weekly = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    project = relationship('Project', back_populates='cod_config')

# Add to Project model
# cod_config = relationship('CoDConfiguration', back_populates='project', uselist=False)
```

### 2. Backend - Endpoints da API

#### Arquivo: `app.py` (adicionar rotas)

```python
# Adicionar imports
from cod_forecaster import CoDForecaster

# Inicializar forecaster (pode ser lazy loading)
cod_forecaster = None

def get_cod_forecaster():
    global cod_forecaster
    if cod_forecaster is None:
        # Load or train model
        cod_forecaster = CoDForecaster()
        # TODO: Load pre-trained model or train with historical data
    return cod_forecaster

@app.route('/api/cod/predict', methods=['POST'])
def predict_cod():
    """Predict Cost of Delay for a project"""
    try:
        data = request.json

        # Validate required fields
        required = ['budget_millions', 'duration_weeks', 'team_size',
                   'num_stakeholders', 'business_value', 'complexity']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get forecaster
        forecaster = get_cod_forecaster()

        if not forecaster.trained:
            return jsonify({'error': 'CoD model not trained yet'}), 503

        # Predict
        result = forecaster.predict_cod(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cod/calculate_total', methods=['POST'])
def calculate_total_cod():
    """Calculate total CoD for a given delay"""
    try:
        data = request.json

        cod_weekly = float(data['cod_weekly'])
        delay_weeks = float(data['delay_weeks'])

        forecaster = get_cod_forecaster()
        result = forecaster.calculate_total_cod(cod_weekly, delay_weeks)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cod/feature_importance', methods=['GET'])
def cod_feature_importance():
    """Get feature importance for CoD model"""
    try:
        forecaster = get_cod_forecaster()

        if not forecaster.trained:
            return jsonify({'error': 'CoD model not trained yet'}), 503

        importance_df = forecaster.get_feature_importance()

        if importance_df is None:
            return jsonify({'error': 'Feature importance not available'}), 404

        return jsonify({
            'features': importance_df.to_dict('records')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cod/train', methods=['POST'])
def train_cod_model():
    """Train CoD model with historical data"""
    try:
        # Get historical projects with CoD data
        projects = Project.query.filter(
            Project.cod_config != None
        ).all()

        if len(projects) < 10:
            return jsonify({'error': 'Insufficient training data (need at least 10 projects)'}), 400

        # Prepare training data
        training_data = []
        for project in projects:
            if project.cod_config and project.cod_config.actual_cod_weekly:
                training_data.append({
                    'budget_millions': project.budget / 1_000_000 if project.budget else 1.0,
                    'duration_weeks': project.duration_weeks or 12,
                    'team_size': project.team_size or 5,
                    'num_stakeholders': 5,  # Default, should be in DB
                    'business_value': project.business_value or 50,
                    'complexity': {'low': 1, 'medium': 3, 'high': 5}.get(project.risk_level, 3),
                    'cod_weekly': project.cod_config.actual_cod_weekly
                })

        if len(training_data) < 10:
            return jsonify({'error': 'Insufficient valid training data'}), 400

        # Train
        forecaster = CoDForecaster()
        forecaster.train_models(pd.DataFrame(training_data))

        # Save globally
        global cod_forecaster
        cod_forecaster = forecaster

        return jsonify({
            'message': 'CoD model trained successfully',
            'training_samples': len(training_data),
            'models': list(forecaster.models.keys())
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 3. Frontend - Interface do Usuário

#### Arquivo: `templates/cod_calculator.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora de Custo de Atraso (CoD)</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>📊 Calculadora de Custo de Atraso (CoD)</h1>

        <div class="card">
            <h2>Características do Projeto</h2>

            <form id="codForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="budget">Orçamento (R$ milhões)</label>
                        <input type="number" id="budget" step="0.1" min="0.1" required>
                    </div>

                    <div class="form-group">
                        <label for="duration">Duração Esperada (semanas)</label>
                        <input type="number" id="duration" min="1" required>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="teamSize">Tamanho da Equipe</label>
                        <input type="number" id="teamSize" min="1" required>
                    </div>

                    <div class="form-group">
                        <label for="stakeholders">Número de Stakeholders</label>
                        <input type="number" id="stakeholders" min="1" required>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="businessValue">Valor de Negócio (0-100)</label>
                        <input type="number" id="businessValue" min="0" max="100" required>
                    </div>

                    <div class="form-group">
                        <label for="complexity">Complexidade (1-5)</label>
                        <select id="complexity" required>
                            <option value="1">1 - Muito Baixa</option>
                            <option value="2">2 - Baixa</option>
                            <option value="3" selected>3 - Média</option>
                            <option value="4">4 - Alta</option>
                            <option value="5">5 - Muito Alta</option>
                        </select>
                    </div>
                </div>

                <h3>Fatores de CoD (Opcional)</h3>

                <div class="form-row">
                    <div class="form-group">
                        <label for="marketImpact">Impacto no Mercado (R$/semana)</label>
                        <input type="number" id="marketImpact" step="1000" min="0" placeholder="0">
                    </div>

                    <div class="form-group">
                        <label for="penalties">Penalidades Contratuais (R$/semana)</label>
                        <input type="number" id="penalties" step="1000" min="0" placeholder="0">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="opportunityCost">Custo de Oportunidade (R$/semana)</label>
                        <input type="number" id="opportunityCost" step="1000" min="0" placeholder="0">
                    </div>

                    <div class="form-group">
                        <label for="reputational">Impacto Reputacional (R$/semana)</label>
                        <input type="number" id="reputational" step="1000" min="0" placeholder="0">
                    </div>
                </div>

                <button type="submit" class="btn-primary">Calcular CoD</button>
            </form>
        </div>

        <div id="results" class="card" style="display: none;">
            <h2>Resultados da Previsão</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>CoD Semanal</h3>
                    <p class="metric-value" id="codWeekly">-</p>
                    <p class="metric-label">R$/semana</p>
                </div>

                <div class="metric-card">
                    <h3>CoD Diário</h3>
                    <p class="metric-value" id="codDaily">-</p>
                    <p class="metric-label">R$/dia</p>
                </div>

                <div class="metric-card">
                    <h3>CoD Mensal</h3>
                    <p class="metric-value" id="codMonthly">-</p>
                    <p class="metric-label">R$/mês</p>
                </div>
            </div>

            <div class="form-group">
                <label for="delayWeeks">Simular Atraso de Quantas Semanas?</label>
                <input type="number" id="delayWeeks" min="1" value="4">
                <button onclick="calculateTotalCod()" class="btn-secondary">Calcular Impacto</button>
            </div>

            <div id="totalCodResult" style="display: none;">
                <h3>Impacto Total do Atraso</h3>
                <div class="alert alert-warning">
                    <p><strong>Atraso de <span id="delayWeeksDisplay">-</span> semanas</strong></p>
                    <p class="total-cod">Custo Total: <span id="totalCod">-</span></p>
                </div>
            </div>

            <h3>Intervalo de Confiança (95%)</h3>
            <div class="confidence-interval">
                <p>Mínimo: R$ <span id="ciMin">-</span></p>
                <p>Máximo: R$ <span id="ciMax">-</span></p>
            </div>
        </div>

        <div id="featureImportance" class="card">
            <h2>Fatores Mais Importantes para CoD</h2>
            <canvas id="importanceChart"></canvas>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/cod_calculator.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/cod_calculator.js` (novo)

```javascript
// CoD Calculator JavaScript

let currentCodWeekly = 0;

document.getElementById('codForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        budget_millions: parseFloat(document.getElementById('budget').value),
        duration_weeks: parseInt(document.getElementById('duration').value),
        team_size: parseInt(document.getElementById('teamSize').value),
        num_stakeholders: parseInt(document.getElementById('stakeholders').value),
        business_value: parseFloat(document.getElementById('businessValue').value),
        complexity: parseInt(document.getElementById('complexity').value),
        project_type: 'web'  // Default, can be dropdown
    };

    try {
        const response = await fetch('/api/cod/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const result = await response.json();

        // Display results
        document.getElementById('codWeekly').textContent =
            formatCurrency(result.cod_weekly);
        document.getElementById('codDaily').textContent =
            formatCurrency(result.cod_daily);
        document.getElementById('codMonthly').textContent =
            formatCurrency(result.cod_monthly);

        document.getElementById('ciMin').textContent =
            formatCurrency(result.confidence_interval_95[0]);
        document.getElementById('ciMax').textContent =
            formatCurrency(result.confidence_interval_95[1]);

        currentCodWeekly = result.cod_weekly;

        document.getElementById('results').style.display = 'block';

        // Load feature importance
        loadFeatureImportance();

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao calcular CoD: ' + error.message);
    }
});

async function calculateTotalCod() {
    const delayWeeks = parseInt(document.getElementById('delayWeeks').value);

    try {
        const response = await fetch('/api/cod/calculate_total', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cod_weekly: currentCodWeekly,
                delay_weeks: delayWeeks
            })
        });

        const result = await response.json();

        document.getElementById('delayWeeksDisplay').textContent = delayWeeks;
        document.getElementById('totalCod').textContent = result.total_cod_formatted;
        document.getElementById('totalCodResult').style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao calcular impacto total: ' + error.message);
    }
}

async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/cod/feature_importance');

        if (!response.ok) return;

        const data = await response.json();
        const features = data.features.slice(0, 10);  // Top 10

        const ctx = document.getElementById('importanceChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: features.map(f => f.feature),
                datasets: [{
                    label: 'Importância',
                    data: features.map(f => f.importance),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Top 10 Fatores que Mais Impactam o CoD'
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}
```

### 4. Testes

#### Arquivo: `test_cod_forecaster.py` (novo)

```python
import pytest
import pandas as pd
import numpy as np
from cod_forecaster import CoDForecaster

def generate_synthetic_projects(n=100):
    """Generate synthetic project data for testing"""
    np.random.seed(42)

    projects = []
    for i in range(n):
        budget = np.random.uniform(0.5, 10.0)
        duration = np.random.uniform(4, 52)
        team_size = np.random.randint(3, 15)

        # Synthetic CoD calculation
        cod_base = (
            budget * 10000 +
            team_size * 2000 +
            duration * 500
        )
        cod_weekly = max(5000, cod_base + np.random.normal(0, 5000))

        projects.append({
            'budget_millions': budget,
            'duration_weeks': duration,
            'team_size': team_size,
            'num_stakeholders': np.random.randint(2, 10),
            'business_value': np.random.uniform(20, 100),
            'complexity': np.random.randint(1, 6),
            'project_type': np.random.choice(['web', 'mobile', 'erp', 'analytics']),
            'risk_level': np.random.randint(1, 6),
            'cod_weekly': cod_weekly
        })

    return pd.DataFrame(projects)

def test_forecaster_initialization():
    forecaster = CoDForecaster()
    assert forecaster.n_splits == 5
    assert not forecaster.trained

def test_feature_preparation():
    forecaster = CoDForecaster()
    projects_df = generate_synthetic_projects(20)

    X, y = forecaster.prepare_features(projects_df)

    assert len(X) == 20
    assert y is not None
    assert len(y) == 20
    assert 'budget_millions' in X.columns
    assert 'budget_per_week' in X.columns  # Derived feature

def test_model_training():
    forecaster = CoDForecaster()
    projects_df = generate_synthetic_projects(50)

    forecaster.train_models(projects_df)

    assert forecaster.trained
    assert 'RandomForest' in forecaster.models
    assert 'GradientBoosting' in forecaster.models

def test_cod_prediction():
    forecaster = CoDForecaster()
    projects_df = generate_synthetic_projects(50)
    forecaster.train_models(projects_df)

    test_project = {
        'budget_millions': 5.0,
        'duration_weeks': 20,
        'team_size': 8,
        'num_stakeholders': 5,
        'business_value': 70,
        'complexity': 3,
        'project_type': 'web',
        'risk_level': 3
    }

    result = forecaster.predict_cod(test_project)

    assert 'cod_weekly' in result
    assert result['cod_weekly'] > 0
    assert 'cod_daily' in result
    assert 'cod_monthly' in result
    assert 'confidence_interval_95' in result

def test_total_cod_calculation():
    forecaster = CoDForecaster()

    result = forecaster.calculate_total_cod(cod_weekly=10000, delay_weeks=4)

    assert result['total_cod'] == 40000
    assert result['delay_weeks'] == 4
    assert 'total_cod_formatted' in result

def test_insufficient_training_data():
    forecaster = CoDForecaster()
    projects_df = generate_synthetic_projects(5)  # Too few

    with pytest.raises(ValueError):
        forecaster.train_models(projects_df)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

## 📅 Cronograma de Implementação

### Semana 1:
- **Dias 1-2:** Implementar `cod_forecaster.py` completo
- **Dias 3-4:** Adicionar rotas da API em `app.py`
- **Dia 5:** Escrever testes unitários

### Semana 2:
- **Dias 1-2:** Criar interface HTML/CSS
- **Dias 3-4:** Implementar JavaScript da calculadora
- **Dia 5:** Integração e testes end-to-end

### Semana 3:
- **Dias 1-2:** Adicionar suporte a banco de dados (CoDConfiguration)
- **Dias 3-4:** Sistema de treinamento com dados reais
- **Dia 5:** Documentação e refinamentos finais

## ✅ Critérios de Aceitação

- [ ] Modelo Random Forest treinado com MAE < 20% do CoD médio
- [ ] API endpoints funcionando corretamente
- [ ] Interface de calculadora intuitiva e responsiva
- [ ] Feature importance visível e interpretável
- [ ] Cálculo de impacto total de atrasos funcional
- [ ] Testes unitários com > 80% de cobertura
- [ ] Documentação completa

## 🎯 Resultado Esperado

Ao final, o flow-forecaster terá um sistema completo de CoD que permite:
1. Prever custo de atraso semanal com base em características do projeto
2. Calcular impacto financeiro total de atrasos
3. Identificar fatores que mais impactam o CoD
4. Fornecer intervalos de confiança para as predições
5. Treinar modelos com dados históricos da organização

**Esforço Total:** ~2-3 semanas (1 desenvolvedor)

---

# Feature #6: Visualização de Feature Importance

## 🎯 Objetivo
Expor feature importance dos modelos ML na UI para PMOs entenderem quais fatores mais impactam as previsões.

## 📊 Status Atual
🟡 **Implementado Parcial** - Modelos têm feature importance, mas não é exposto na UI

## 🔧 Componentes a Implementar

### 1. Backend - API Endpoint

#### Arquivo: `app.py` (adicionar)

```python
@app.route('/api/ml/feature_importance/<model_type>', methods=['GET'])
def get_feature_importance(model_type):
    """
    Get feature importance for ML models.

    Args:
        model_type: 'throughput' or 'deadline'
    """
    try:
        # Get forecaster based on type
        if model_type == 'throughput':
            # Get from ml_forecaster
            forecaster = get_ml_forecaster()  # Implement this helper

            if not forecaster or not forecaster.trained:
                return jsonify({'error': 'Model not trained yet'}), 503

            # Get feature importance from RandomForest model
            if 'RandomForest' in forecaster.models:
                model = forecaster.models['RandomForest']
                importances = model.feature_importances_
                feature_names = [f'lag_{i}' for i in range(1, forecaster.max_lag + 1)] + \
                               ['rolling_mean_3', 'rolling_std_3']

                importance_data = [
                    {'feature': name, 'importance': float(imp)}
                    for name, imp in zip(feature_names, importances)
                ]
                importance_data.sort(key=lambda x: x['importance'], reverse=True)

                # Generate insights
                insights = generate_feature_insights(importance_data)

                return jsonify({
                    'model_type': model_type,
                    'model_name': 'RandomForest',
                    'features': importance_data,
                    'insights': insights
                })
            else:
                return jsonify({'error': 'RandomForest model not available'}), 404

        elif model_type == 'cod':
            # Get from CoD forecaster
            forecaster = get_cod_forecaster()

            if not forecaster or not forecaster.trained:
                return jsonify({'error': 'CoD model not trained yet'}), 503

            importance_df = forecaster.get_feature_importance()

            if importance_df is None:
                return jsonify({'error': 'Feature importance not available'}), 404

            importance_data = importance_df.to_dict('records')
            insights = generate_cod_feature_insights(importance_data)

            return jsonify({
                'model_type': model_type,
                'model_name': 'RandomForest',
                'features': importance_data,
                'insights': insights
            })
        else:
            return jsonify({'error': 'Invalid model_type. Use: throughput, cod'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_feature_insights(importance_data):
    """Generate actionable insights from feature importance"""
    insights = []

    top_3 = importance_data[:3]

    for i, feature in enumerate(top_3, 1):
        feature_name = feature['feature']
        importance = feature['importance'] * 100

        if 'lag_' in feature_name:
            lag_num = feature_name.split('_')[1]
            insights.append({
                'rank': i,
                'message': f"O throughput de {lag_num} semanas atrás é o {i}º fator mais importante ({importance:.1f}%)",
                'recommendation': f"Mantenha dados históricos de pelo menos {lag_num} semanas para previsões precisas"
            })
        elif 'rolling_mean' in feature_name:
            insights.append({
                'rank': i,
                'message': f"A média móvel é o {i}º fator mais importante ({importance:.1f}%)",
                'recommendation': "Tendências recentes são críticas - monitore mudanças no throughput médio"
            })
        elif 'rolling_std' in feature_name:
            insights.append({
                'rank': i,
                'message': f"A volatilidade é o {i}º fator mais importante ({importance:.1f}%)",
                'recommendation': "Alta variabilidade aumenta incerteza - trabalhe para estabilizar o throughput"
            })

    return insights

def generate_cod_feature_insights(importance_data):
    """Generate actionable insights for CoD features"""
    insights = []

    top_5 = importance_data[:5]

    insight_map = {
        'budget_millions': {
            'message': 'Orçamento é o principal driver do CoD',
            'recommendation': 'Projetos maiores têm CoD mais alto - priorize por ROI'
        },
        'business_value': {
            'message': 'Valor de negócio impacta diretamente o CoD',
            'recommendation': 'Quantifique bem o valor de negócio para estimativas precisas'
        },
        'num_stakeholders': {
            'message': 'Mais stakeholders = maior CoD',
            'recommendation': 'Atrasos em projetos com muitos stakeholders custam caro'
        },
        'complexity': {
            'message': 'Complexidade aumenta o CoD',
            'recommendation': 'Simplifique o escopo quando possível para reduzir risco financeiro'
        },
        'duration_weeks': {
            'message': 'Projetos longos têm CoD mais alto',
            'recommendation': 'Divida projetos longos em entregas incrementais'
        }
    }

    for i, feature in enumerate(top_5, 1):
        feature_name = feature['feature']
        importance = feature['importance'] * 100

        if feature_name in insight_map:
            insight_info = insight_map[feature_name]
            insights.append({
                'rank': i,
                'feature': feature_name,
                'importance_pct': importance,
                'message': insight_info['message'],
                'recommendation': insight_info['recommendation']
            })

    return insights
```

### 2. Frontend - Dashboard de Feature Importance

#### Arquivo: `templates/feature_importance_dashboard.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feature Importance - Fatores de Impacto</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>🎯 Análise de Fatores de Impacto</h1>
        <p class="subtitle">Descubra quais fatores mais influenciam as previsões dos modelos de Machine Learning</p>

        <div class="tabs">
            <button class="tab-button active" onclick="loadFeatureImportance('throughput')">
                Throughput
            </button>
            <button class="tab-button" onclick="loadFeatureImportance('cod')">
                Custo de Atraso (CoD)
            </button>
        </div>

        <div id="loading" class="loading" style="display: none;">
            <p>Carregando...</p>
        </div>

        <div id="content">
            <!-- Chart Container -->
            <div class="card">
                <h2>Importância das Features</h2>
                <canvas id="importanceChart" height="400"></canvas>
            </div>

            <!-- Insights Container -->
            <div class="card">
                <h2>💡 Insights Acionáveis</h2>
                <div id="insightsList"></div>
            </div>

            <!-- Detailed Table -->
            <div class="card">
                <h2>Ranking Completo</h2>
                <table id="featureTable" class="data-table">
                    <thead>
                        <tr>
                            <th>Ranking</th>
                            <th>Feature</th>
                            <th>Importância</th>
                            <th>Contribuição</th>
                        </tr>
                    </thead>
                    <tbody id="featureTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/feature_importance.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/feature_importance.js` (novo)

```javascript
let currentChart = null;
let currentModelType = 'throughput';

async function loadFeatureImportance(modelType) {
    currentModelType = modelType;

    // Update active tab
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';

    try {
        const response = await fetch(`/api/ml/feature_importance/${modelType}`);

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const data = await response.json();

        // Update chart
        updateChart(data.features);

        // Update insights
        updateInsights(data.insights);

        // Update table
        updateTable(data.features);

        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar feature importance: ' + error.message);
        document.getElementById('loading').style.display = 'none';
    }
}

function updateChart(features) {
    const ctx = document.getElementById('importanceChart').getContext('2d');

    // Destroy previous chart
    if (currentChart) {
        currentChart.destroy();
    }

    // Take top 10 features
    const topFeatures = features.slice(0, 10);

    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topFeatures.map(f => f.feature),
            datasets: [{
                label: 'Importância (%)',
                data: topFeatures.map(f => f.importance * 100),
                backgroundColor: topFeatures.map((_, i) =>
                    `rgba(54, 162, 235, ${1 - (i * 0.07)})`
                ),
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Fatores Mais Importantes',
                    font: {size: 16}
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Importância: ' + context.parsed.x.toFixed(2) + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Importância (%)'
                    }
                }
            }
        }
    });
}

function updateInsights(insights) {
    const container = document.getElementById('insightsList');
    container.innerHTML = '';

    if (!insights || insights.length === 0) {
        container.innerHTML = '<p>Nenhum insight disponível.</p>';
        return;
    }

    insights.forEach(insight => {
        const insightCard = document.createElement('div');
        insightCard.className = 'insight-card';

        insightCard.innerHTML = `
            <div class="insight-rank">
                <span class="rank-badge">#${insight.rank}</span>
            </div>
            <div class="insight-content">
                <h3>${insight.message}</h3>
                <p class="insight-recommendation">
                    <strong>Recomendação:</strong> ${insight.recommendation}
                </p>
            </div>
        `;

        container.appendChild(insightCard);
    });
}

function updateTable(features) {
    const tbody = document.getElementById('featureTableBody');
    tbody.innerHTML = '';

    features.forEach((feature, index) => {
        const row = document.createElement('tr');

        const importance = feature.importance * 100;

        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${feature.feature}</strong></td>
            <td>${importance.toFixed(2)}%</td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${importance}%"></div>
                </div>
            </td>
        `;

        tbody.appendChild(row);
    });
}

// Load throughput importance on page load
document.addEventListener('DOMContentLoaded', () => {
    loadFeatureImportance('throughput');
});
```

### 3. CSS Styles

#### Arquivo: `static/css/style.css` (adicionar)

```css
/* Feature Importance Styles */

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tab-button {
    padding: 12px 24px;
    background: #f5f5f5;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
}

.tab-button:hover {
    background: #e0e0e0;
}

.tab-button.active {
    background: #2196F3;
    color: white;
}

.insight-card {
    display: flex;
    gap: 15px;
    padding: 15px;
    margin-bottom: 15px;
    background: #f9f9f9;
    border-left: 4px solid #2196F3;
    border-radius: 5px;
}

.rank-badge {
    display: inline-block;
    width: 40px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    background: #2196F3;
    color: white;
    border-radius: 50%;
    font-weight: bold;
    font-size: 18px;
}

.insight-content h3 {
    margin: 0 0 10px 0;
    color: #333;
}

.insight-recommendation {
    color: #666;
    font-style: italic;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.data-table th {
    background: #f5f5f5;
    font-weight: bold;
}

.progress-bar {
    width: 100%;
    height: 20px;
    background: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2196F3, #64B5F6);
    transition: width 0.3s;
}

.loading {
    text-align: center;
    padding: 40px;
    font-size: 18px;
    color: #666;
}
```

### 4. Integração com Menu Principal

#### Arquivo: `templates/base.html` (modificar menu)

```html
<!-- Add to navigation menu -->
<nav>
    <ul>
        <li><a href="/">Dashboard</a></li>
        <li><a href="/forecasts">Forecasts</a></li>
        <li><a href="/cod_calculator">Custo de Atraso</a></li>
        <li><a href="/feature_importance">Fatores de Impacto</a></li>
        <li><a href="/portfolio">Portfolio</a></li>
    </ul>
</nav>
```

### 5. Testes

#### Arquivo: `test_feature_importance.py` (novo)

```python
import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_feature_importance_throughput(client):
    """Test throughput feature importance endpoint"""
    response = client.get('/api/ml/feature_importance/throughput')

    # May be 503 if model not trained
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'features' in data
        assert 'insights' in data
        assert len(data['features']) > 0

def test_feature_importance_cod(client):
    """Test CoD feature importance endpoint"""
    response = client.get('/api/ml/feature_importance/cod')

    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'features' in data
        assert len(data['features']) > 0

def test_feature_importance_invalid_type(client):
    """Test invalid model type"""
    response = client.get('/api/ml/feature_importance/invalid')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
```

## 📅 Cronograma de Implementação

**Total: 3-5 dias**

- **Dia 1:** Backend - API endpoints e helpers
- **Dia 2:** Frontend - HTML + CSS
- **Dia 3:** Frontend - JavaScript e charts
- **Dia 4:** Integração e testes
- **Dia 5:** Refinamentos e documentação

## ✅ Critérios de Aceitação

- [ ] API endpoint retorna feature importance corretamente
- [ ] Dashboard visualiza top 10 features com chart
- [ ] Insights acionáveis gerados automaticamente
- [ ] Tabela completa com todas as features
- [ ] Suporte para múltiplos modelos (throughput, CoD)
- [ ] Testes unitários passando
- [ ] Interface responsiva e intuitiva

**Esforço Total:** ~1 semana (1 desenvolvedor)

---

# Feature #12: Visualizações Avançadas

## 🎯 Objetivo
Adicionar visualizações avançadas (scatter plots, box plots, heatmaps) para análise exploratória.

## 📊 Status Atual
🟡 **Implementado Parcial** - Apenas histogramas básicos

## 🔧 Componentes a Implementar

### 1. Backend - Endpoints de Dados

#### Arquivo: `app.py` (adicionar)

```python
@app.route('/api/visualizations/scatter_data', methods=['POST'])
def get_scatter_data():
    """
    Get data for scatter plot visualization.

    Expected JSON:
    {
        "x_variable": "duration_weeks",
        "y_variable": "cod_weekly",
        "color_by": "risk_level",  # optional
        "filters": {...}  # optional
    }
    """
    try:
        data = request.json
        x_var = data.get('x_variable')
        y_var = data.get('y_variable')
        color_by = data.get('color_by')

        # Query projects
        projects = Project.query.filter_by(status='active').all()

        scatter_data = []
        for project in projects:
            point = {
                'id': project.id,
                'name': project.name,
                'x': getattr(project, x_var, None),
                'y': getattr(project, y_var, None)
            }

            if color_by:
                point['color'] = getattr(project, color_by, None)

            scatter_data.append(point)

        # Calculate correlation
        x_values = [p['x'] for p in scatter_data if p['x'] is not None]
        y_values = [p['y'] for p in scatter_data if p['y'] is not None]

        correlation = np.corrcoef(x_values, y_values)[0, 1] if len(x_values) > 1 else 0

        return jsonify({
            'data': scatter_data,
            'correlation': float(correlation),
            'x_variable': x_var,
            'y_variable': y_var
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/boxplot_data', methods=['POST'])
def get_boxplot_data():
    """
    Get data for box plot visualization.

    Expected JSON:
    {
        "variable": "duration_weeks",
        "group_by": "risk_level"
    }
    """
    try:
        data = request.json
        variable = data.get('variable')
        group_by = data.get('group_by')

        # Query projects
        projects = Project.query.filter_by(status='active').all()

        # Group data
        grouped_data = {}
        for project in projects:
            group_value = getattr(project, group_by, 'unknown')
            if group_value not in grouped_data:
                grouped_data[group_value] = []

            value = getattr(project, variable, None)
            if value is not None:
                grouped_data[group_value].append(value)

        # Calculate statistics for each group
        boxplot_data = []
        for group, values in grouped_data.items():
            if len(values) > 0:
                values_sorted = sorted(values)
                n = len(values_sorted)

                boxplot_data.append({
                    'group': str(group),
                    'min': float(np.min(values_sorted)),
                    'q1': float(np.percentile(values_sorted, 25)),
                    'median': float(np.median(values_sorted)),
                    'q3': float(np.percentile(values_sorted, 75)),
                    'max': float(np.max(values_sorted)),
                    'mean': float(np.mean(values_sorted)),
                    'count': n
                })

        return jsonify({
            'data': boxplot_data,
            'variable': variable,
            'group_by': group_by
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/correlation_matrix', methods=['POST'])
def get_correlation_matrix():
    """
    Get correlation matrix for multiple variables.

    Expected JSON:
    {
        "variables": ["duration_weeks", "budget", "team_size", "business_value"]
    }
    """
    try:
        data = request.json
        variables = data.get('variables', [])

        # Query projects
        projects = Project.query.filter_by(status='active').all()

        # Build data matrix
        data_matrix = []
        for project in projects:
            row = []
            for var in variables:
                value = getattr(project, var, None)
                row.append(value if value is not None else 0)
            data_matrix.append(row)

        # Calculate correlation matrix
        corr_matrix = np.corrcoef(np.array(data_matrix).T)

        # Format for frontend
        matrix_data = []
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                matrix_data.append({
                    'x': var1,
                    'y': var2,
                    'value': float(corr_matrix[i, j])
                })

        return jsonify({
            'data': matrix_data,
            'variables': variables
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Frontend - Visualizations Dashboard

#### Arquivo: `templates/advanced_visualizations.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizações Avançadas</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>📊 Visualizações Avançadas</h1>

        <div class="viz-selector">
            <button class="viz-btn active" onclick="showVisualization('scatter')">
                Scatter Plot
            </button>
            <button class="viz-btn" onclick="showVisualization('boxplot')">
                Box Plot
            </button>
            <button class="viz-btn" onclick="showVisualization('heatmap')">
                Correlation Heatmap
            </button>
        </div>

        <!-- Scatter Plot Section -->
        <div id="scatter-section" class="viz-section">
            <div class="card">
                <h2>Scatter Plot - Análise de Correlação</h2>

                <div class="controls">
                    <div class="control-group">
                        <label>Eixo X:</label>
                        <select id="scatterX">
                            <option value="duration_weeks">Duração (semanas)</option>
                            <option value="budget">Orçamento</option>
                            <option value="team_size">Tamanho da Equipe</option>
                            <option value="business_value">Valor de Negócio</option>
                        </select>
                    </div>

                    <div class="control-group">
                        <label>Eixo Y:</label>
                        <select id="scatterY">
                            <option value="cod_weekly">CoD Semanal</option>
                            <option value="duration_weeks">Duração (semanas)</option>
                            <option value="business_value">Valor de Negócio</option>
                        </select>
                    </div>

                    <div class="control-group">
                        <label>Colorir por:</label>
                        <select id="scatterColor">
                            <option value="">Nenhum</option>
                            <option value="risk_level">Nível de Risco</option>
                            <option value="priority">Prioridade</option>
                        </select>
                    </div>

                    <button onclick="loadScatterPlot()" class="btn-primary">Gerar</button>
                </div>

                <div class="chart-container">
                    <canvas id="scatterChart"></canvas>
                </div>

                <div id="scatterStats" class="stats-box"></div>
            </div>
        </div>

        <!-- Box Plot Section -->
        <div id="boxplot-section" class="viz-section" style="display: none;">
            <div class="card">
                <h2>Box Plot - Distribuição por Grupos</h2>

                <div class="controls">
                    <div class="control-group">
                        <label>Variável:</label>
                        <select id="boxplotVariable">
                            <option value="duration_weeks">Duração (semanas)</option>
                            <option value="cod_weekly">CoD Semanal</option>
                            <option value="budget">Orçamento</option>
                            <option value="business_value">Valor de Negócio</option>
                        </select>
                    </div>

                    <div class="control-group">
                        <label>Agrupar por:</label>
                        <select id="boxplotGroup">
                            <option value="risk_level">Nível de Risco</option>
                            <option value="priority">Prioridade</option>
                            <option value="owner">Owner</option>
                        </select>
                    </div>

                    <button onclick="loadBoxPlot()" class="btn-primary">Gerar</button>
                </div>

                <div class="chart-container">
                    <canvas id="boxplotChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Heatmap Section -->
        <div id="heatmap-section" class="viz-section" style="display: none;">
            <div class="card">
                <h2>Correlation Heatmap</h2>

                <div class="controls">
                    <label>Variáveis a Correlacionar:</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" value="duration_weeks" checked> Duração</label>
                        <label><input type="checkbox" value="budget" checked> Orçamento</label>
                        <label><input type="checkbox" value="team_size" checked> Tamanho Equipe</label>
                        <label><input type="checkbox" value="business_value" checked> Valor Negócio</label>
                        <label><input type="checkbox" value="cod_weekly" checked> CoD Semanal</label>
                    </div>

                    <button onclick="loadHeatmap()" class="btn-primary">Gerar</button>
                </div>

                <div class="chart-container">
                    <canvas id="heatmapChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/advanced_visualizations.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/advanced_visualizations.js` (novo)

```javascript
let currentCharts = {
    scatter: null,
    boxplot: null,
    heatmap: null
};

function showVisualization(type) {
    // Hide all sections
    document.querySelectorAll('.viz-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(`${type}-section`).style.display = 'block';

    // Update buttons
    document.querySelectorAll('.viz-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

async function loadScatterPlot() {
    const xVar = document.getElementById('scatterX').value;
    const yVar = document.getElementById('scatterY').value;
    const colorBy = document.getElementById('scatterColor').value;

    try {
        const response = await fetch('/api/visualizations/scatter_data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                x_variable: xVar,
                y_variable: yVar,
                color_by: colorBy || null
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }

        const result = await response.json();

        // Prepare data
        const datasets = [{
            label: 'Projetos',
            data: result.data.map(p => ({x: p.x, y: p.y})),
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }];

        // Destroy previous chart
        if (currentCharts.scatter) {
            currentCharts.scatter.destroy();
        }

        // Create chart
        const ctx = document.getElementById('scatterChart').getContext('2d');
        currentCharts.scatter = new Chart(ctx, {
            type: 'scatter',
            data: {datasets},
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${yVar} vs ${xVar}`
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = result.data[context.dataIndex];
                                return `${point.name}: (${point.x}, ${point.y})`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: xVar
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: yVar
                        }
                    }
                }
            }
        });

        // Display correlation
        document.getElementById('scatterStats').innerHTML = `
            <h3>Estatísticas</h3>
            <p><strong>Correlação de Pearson:</strong> ${result.correlation.toFixed(3)}</p>
            <p><strong>Interpretação:</strong> ${interpretCorrelation(result.correlation)}</p>
        `;

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar scatter plot: ' + error.message);
    }
}

async function loadBoxPlot() {
    const variable = document.getElementById('boxplotVariable').value;
    const groupBy = document.getElementById('boxplotGroup').value;

    try {
        const response = await fetch('/api/visualizations/boxplot_data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                variable: variable,
                group_by: groupBy
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }

        const result = await response.json();

        // Prepare data for box plot
        const labels = result.data.map(d => d.group);
        const datasets = [{
            label: variable,
            data: result.data.map(d => [d.min, d.q1, d.median, d.q3, d.max]),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }];

        // Destroy previous chart
        if (currentCharts.boxplot) {
            currentCharts.boxplot.destroy();
        }

        // Create chart (using custom box plot plugin or library)
        const ctx = document.getElementById('boxplotChart').getContext('2d');
        currentCharts.boxplot = new Chart(ctx, {
            type: 'bar',  // Simplified, use chart.js-boxplot plugin for proper box plots
            data: {
                labels: labels,
                datasets: [{
                    label: 'Mediana',
                    data: result.data.map(d => d.median),
                    backgroundColor: 'rgba(75, 192, 192, 0.5)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${variable} por ${groupBy}`
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar box plot: ' + error.message);
    }
}

async function loadHeatmap() {
    const checkboxes = document.querySelectorAll('.checkbox-group input:checked');
    const variables = Array.from(checkboxes).map(cb => cb.value);

    if (variables.length < 2) {
        alert('Selecione pelo menos 2 variáveis');
        return;
    }

    try {
        const response = await fetch('/api/visualizations/correlation_matrix', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                variables: variables
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }

        const result = await response.json();

        // Prepare heatmap data
        const matrix = [];
        const n = variables.length;

        for (let i = 0; i < n; i++) {
            matrix[i] = [];
            for (let j = 0; j < n; j++) {
                const point = result.data.find(d =>
                    d.x === variables[j] && d.y === variables[i]
                );
                matrix[i][j] = point ? point.value : 0;
            }
        }

        // Destroy previous chart
        if (currentCharts.heatmap) {
            currentCharts.heatmap.destroy();
        }

        // Create heatmap (simplified, use Chart.js Matrix plugin)
        const ctx = document.getElementById('heatmapChart').getContext('2d');

        // For now, display as table (proper heatmap requires additional library)
        displayCorrelationTable(variables, matrix);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar heatmap: ' + error.message);
    }
}

function displayCorrelationTable(variables, matrix) {
    const container = document.getElementById('heatmapChart').parentElement;

    let html = '<table class="correlation-table"><thead><tr><th></th>';
    variables.forEach(v => {
        html += `<th>${v}</th>`;
    });
    html += '</tr></thead><tbody>';

    variables.forEach((v1, i) => {
        html += `<tr><th>${v1}</th>`;
        variables.forEach((v2, j) => {
            const value = matrix[i][j];
            const color = getCorrelationColor(value);
            html += `<td style="background-color: ${color}">${value.toFixed(2)}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';

    container.innerHTML = html;
}

function getCorrelationColor(value) {
    // Red for negative, green for positive
    if (value >= 0) {
        const intensity = Math.floor(value * 255);
        return `rgba(0, ${intensity}, 0, 0.5)`;
    } else {
        const intensity = Math.floor(Math.abs(value) * 255);
        return `rgba(${intensity}, 0, 0, 0.5)`;
    }
}

function interpretCorrelation(r) {
    const abs_r = Math.abs(r);

    if (abs_r >= 0.9) return 'Correlação muito forte';
    if (abs_r >= 0.7) return 'Correlação forte';
    if (abs_r >= 0.5) return 'Correlação moderada';
    if (abs_r >= 0.3) return 'Correlação fraca';
    return 'Correlação muito fraca ou inexistente';
}
```

## 📅 Cronograma de Implementação

**Total: 1 semana**

- **Dias 1-2:** Backend - API endpoints
- **Dias 3-4:** Frontend - HTML/CSS/JS
- **Dia 5:** Integração e testes

## ✅ Critérios de Aceitação

- [ ] Scatter plot funcional com correlação
- [ ] Box plot por grupos funcionando
- [ ] Heatmap de correlação exibindo corretamente
- [ ] Interface intuitiva com controles claros
- [ ] Tooltips informativos em todos os gráficos
- [ ] Responsivo para diferentes tamanhos de tela

**Esforço Total:** ~1 semana (1 desenvolvedor)

---

# Feature #13: Upload de Dados Históricos

## 🎯 Objetivo
Permitir upload de dados históricos em CSV/Excel para treinar modelos com dados da organização.

## 📊 Status Atual
🟡 **Implementado Parcial** - Database existe, falta UI para upload

## 🔧 Componentes a Implementar

### 1. Backend - Upload e Parsing

#### Arquivo: `data_import.py` (novo)

```python
"""
Data Import Module
Handles CSV/Excel upload and parsing for historical project data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os

from models import Project, CoDConfiguration, db
from cod_forecaster import CoDForecaster


class DataImporter:
    """Handles import of historical project data"""

    def __init__(self):
        self.required_columns = [
            'project_name',
            'duration_weeks',
            'team_size',
            'budget'
        ]

        self.optional_columns = [
            'business_value',
            'risk_level',
            'priority',
            'owner',
            'status',
            'actual_cod_weekly',
            'complexity',
            'num_stakeholders'
        ]

    def validate_file(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate uploaded file.

        Args:
            file_path: Path to uploaded file

        Returns:
            (is_valid, message, dataframe)
        """
        try:
            # Determine file type and read
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return False, "Formato de arquivo não suportado. Use CSV ou Excel.", None

            # Check required columns
            missing_cols = [col for col in self.required_columns if col not in df.columns]

            if missing_cols:
                return False, f"Colunas obrigatórias faltando: {', '.join(missing_cols)}", None

            # Validate data types
            if not pd.api.types.is_numeric_dtype(df['duration_weeks']):
                return False, "Coluna 'duration_weeks' deve conter números", None

            if not pd.api.types.is_numeric_dtype(df['team_size']):
                return False, "Coluna 'team_size' deve conter números inteiros", None

            if not pd.api.types.is_numeric_dtype(df['budget']):
                return False, "Coluna 'budget' deve conter números", None

            # Check for empty data
            if len(df) == 0:
                return False, "Arquivo vazio", None

            return True, f"Arquivo válido com {len(df)} projetos", df

        except Exception as e:
            return False, f"Erro ao ler arquivo: {str(e)}", None

    def import_projects(self, df: pd.DataFrame, user_id: Optional[int] = None) -> Dict:
        """
        Import projects from DataFrame to database.

        Args:
            df: DataFrame with project data
            user_id: ID of user uploading (for tracking)

        Returns:
            Dictionary with import statistics
        """
        imported = 0
        skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # Create or update project
                project = Project(
                    name=str(row['project_name']),
                    duration_weeks=int(row['duration_weeks']),
                    team_size=int(row['team_size']),
                    budget=float(row['budget']),
                    business_value=int(row.get('business_value', 50)),
                    risk_level=str(row.get('risk_level', 'medium')).lower(),
                    priority=str(row.get('priority', 'medium')).lower(),
                    owner=str(row.get('owner', 'Imported')),
                    status=str(row.get('status', 'completed')).lower(),
                    capacity_allocated=float(row.get('capacity_allocated', row['team_size']))
                )

                db.session.add(project)
                db.session.flush()  # Get project ID

                # Add CoD configuration if available
                if 'actual_cod_weekly' in row and pd.notna(row['actual_cod_weekly']):
                    cod_config = CoDConfiguration(
                        project_id=project.id,
                        actual_cod_weekly=float(row['actual_cod_weekly']),
                        market_impact_weight=float(row.get('market_impact_weight', 1.0)),
                        contractual_penalties=float(row.get('contractual_penalties', 0)),
                        opportunity_cost=float(row.get('opportunity_cost', 0)),
                        reputational_impact=float(row.get('reputational_impact', 0))
                    )
                    db.session.add(cod_config)

                imported += 1

            except Exception as e:
                skipped += 1
                errors.append(f"Linha {idx + 2}: {str(e)}")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"Erro ao salvar no banco de dados: {str(e)}"
            }

        return {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'errors': errors[:10]  # Limit to 10 errors
        }

    def generate_template(self) -> pd.DataFrame:
        """
        Generate template DataFrame with example data.

        Returns:
            DataFrame with template structure
        """
        template_data = {
            'project_name': ['Projeto Exemplo 1', 'Projeto Exemplo 2'],
            'duration_weeks': [12, 24],
            'team_size': [5, 8],
            'budget': [500000, 1200000],
            'business_value': [70, 85],
            'risk_level': ['medium', 'high'],
            'priority': ['high', 'medium'],
            'owner': ['João Silva', 'Maria Santos'],
            'status': ['completed', 'completed'],
            'actual_cod_weekly': [50000, 80000],
            'complexity': [3, 4],
            'num_stakeholders': [5, 8]
        }

        return pd.DataFrame(template_data)
```

#### Arquivo: `app.py` (adicionar rotas)

```python
from werkzeug.utils import secure_filename
from data_import import DataImporter

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload folder if doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/data/upload', methods=['POST'])
def upload_data():
    """Upload and import historical data"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo não suportado. Use CSV ou Excel'}), 400

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Import data
        importer = DataImporter()

        # Validate
        is_valid, message, df = importer.validate_file(file_path)

        if not is_valid:
            os.remove(file_path)  # Clean up
            return jsonify({'error': message}), 400

        # Import
        result = importer.import_projects(df)

        # Clean up
        os.remove(file_path)

        if not result['success']:
            return jsonify({'error': result['error']}), 500

        return jsonify({
            'message': 'Importação concluída com sucesso',
            'imported': result['imported'],
            'skipped': result['skipped'],
            'errors': result['errors']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/template', methods=['GET'])
def download_template():
    """Download template CSV file"""
    try:
        importer = DataImporter()
        template_df = importer.generate_template()

        # Save to temporary file
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], 'template_import.csv')
        template_df.to_csv(template_path, index=False)

        return send_file(
            template_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='template_projetos.csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/auto_train', methods=['POST'])
def auto_train_models():
    """Automatically retrain models with new data"""
    try:
        # Get all completed projects with CoD data
        projects = Project.query.filter(
            Project.status == 'completed',
            Project.cod_config != None
        ).all()

        if len(projects) < 10:
            return jsonify({'error': 'Dados insuficientes para treinar (mínimo 10 projetos)'}), 400

        # Prepare training data
        training_data = []
        for project in projects:
            if project.cod_config and project.cod_config.actual_cod_weekly:
                training_data.append({
                    'budget_millions': project.budget / 1_000_000 if project.budget else 1.0,
                    'duration_weeks': project.duration_weeks or 12,
                    'team_size': project.team_size or 5,
                    'num_stakeholders': 5,  # Default
                    'business_value': project.business_value or 50,
                    'complexity': {'low': 1, 'medium': 3, 'high': 5}.get(project.risk_level, 3),
                    'cod_weekly': project.cod_config.actual_cod_weekly
                })

        # Train CoD model
        forecaster = CoDForecaster()
        forecaster.train_models(pd.DataFrame(training_data))

        # Save globally (in production, save to disk)
        global cod_forecaster
        cod_forecaster = forecaster

        return jsonify({
            'message': 'Modelos retreinados com sucesso',
            'training_samples': len(training_data),
            'models': list(forecaster.models.keys()),
            'performance': {
                name: {
                    'mae': float(data['mae']),
                    'r2': float(data['r2'])
                }
                for name, data in forecaster.models.items()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Frontend - Upload Interface

#### Arquivo: `templates/data_import.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Importar Dados Históricos</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>📂 Importar Dados Históricos</h1>
        <p class="subtitle">Importe seus dados históricos para treinar modelos personalizados</p>

        <div class="card">
            <h2>Passo 1: Baixe o Template</h2>
            <p>Baixe o template CSV para ver o formato esperado dos dados</p>
            <button onclick="downloadTemplate()" class="btn-secondary">
                📥 Baixar Template
            </button>
        </div>

        <div class="card">
            <h2>Passo 2: Upload do Arquivo</h2>

            <div class="upload-area" id="uploadArea">
                <div class="upload-content">
                    <svg class="upload-icon" xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <p>Arraste e solte seu arquivo aqui</p>
                    <p class="upload-hint">ou</p>
                    <input type="file" id="fileInput" accept=".csv,.xlsx,.xls" hidden>
                    <button onclick="document.getElementById('fileInput').click()" class="btn-primary">
                        Selecionar Arquivo
                    </button>
                    <p class="upload-formats">Formatos aceitos: CSV, Excel (.xlsx, .xls)</p>
                </div>
            </div>

            <div id="fileName" class="file-name" style="display: none;"></div>

            <div id="validationResult" style="display: none;"></div>

            <button id="uploadBtn" onclick="uploadFile()" class="btn-primary" disabled>
                Importar Dados
            </button>
        </div>

        <div id="resultsCard" class="card" style="display: none;">
            <h2>Resultado da Importação</h2>
            <div id="importResults"></div>
        </div>

        <div class="card">
            <h2>Passo 3: Retreinar Modelos</h2>
            <p>Após importar dados, retreine os modelos para usar seus dados históricos</p>
            <button onclick="autoTrainModels()" class="btn-success">
                🎯 Retreinar Modelos Automaticamente
            </button>

            <div id="trainingResults" style="display: none; margin-top: 20px;"></div>
        </div>

        <div class="card">
            <h2>ℹ️ Informações Importantes</h2>

            <h3>Colunas Obrigatórias:</h3>
            <ul>
                <li><strong>project_name:</strong> Nome do projeto</li>
                <li><strong>duration_weeks:</strong> Duração em semanas (número)</li>
                <li><strong>team_size:</strong> Tamanho da equipe (número)</li>
                <li><strong>budget:</strong> Orçamento em R$ (número)</li>
            </ul>

            <h3>Colunas Opcionais (mas recomendadas):</h3>
            <ul>
                <li><strong>business_value:</strong> Valor de negócio 0-100</li>
                <li><strong>risk_level:</strong> low, medium, high</li>
                <li><strong>priority:</strong> low, medium, high</li>
                <li><strong>owner:</strong> Nome do responsável</li>
                <li><strong>status:</strong> completed, active, on_hold</li>
                <li><strong>actual_cod_weekly:</strong> CoD real semanal em R$ (para treinar modelo de CoD)</li>
                <li><strong>complexity:</strong> 1-5</li>
                <li><strong>num_stakeholders:</strong> Número de stakeholders</li>
            </ul>

            <h3>Dicas:</h3>
            <ul>
                <li>✅ Importe pelo menos 10 projetos para treinar modelos</li>
                <li>✅ Quanto mais dados, melhor a precisão dos modelos</li>
                <li>✅ Inclua dados de CoD para treinar o modelo de custo de atraso</li>
                <li>✅ Use o template para garantir formato correto</li>
            </ul>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/data_import.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/data_import.js` (novo)

```javascript
let selectedFile = null;

// Set up drag and drop
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

document.getElementById('fileInput').addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['text/csv', 'application/vnd.ms-excel',
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];

    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
        alert('Formato de arquivo inválido. Use CSV ou Excel.');
        return;
    }

    selectedFile = file;

    // Display file name
    document.getElementById('fileName').textContent = `Arquivo selecionado: ${file.name}`;
    document.getElementById('fileName').style.display = 'block';

    // Enable upload button
    document.getElementById('uploadBtn').disabled = false;
}

async function downloadTemplate() {
    try {
        const response = await fetch('/api/data/template');

        if (!response.ok) {
            throw new Error('Erro ao baixar template');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'template_projetos.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao baixar template: ' + error.message);
    }
}

async function uploadFile() {
    if (!selectedFile) {
        alert('Selecione um arquivo primeiro');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    // Disable button and show loading
    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.textContent = 'Importando...';

    try {
        const response = await fetch('/api/data/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Erro ao importar dados');
        }

        // Display results
        displayImportResults(result);

        // Show results card
        document.getElementById('resultsCard').style.display = 'block';

        // Scroll to results
        document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao importar: ' + error.message);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = 'Importar Dados';
    }
}

function displayImportResults(result) {
    const container = document.getElementById('importResults');

    let html = '<div class="import-summary">';

    if (result.imported > 0) {
        html += `<div class="alert alert-success">
            ✅ ${result.imported} projeto(s) importado(s) com sucesso!
        </div>`;
    }

    if (result.skipped > 0) {
        html += `<div class="alert alert-warning">
            ⚠️ ${result.skipped} projeto(s) ignorado(s)
        </div>`;

        if (result.errors && result.errors.length > 0) {
            html += '<h4>Erros encontrados:</h4><ul class="error-list">';
            result.errors.forEach(error => {
                html += `<li>${error}</li>`;
            });
            html += '</ul>';
        }
    }

    html += '</div>';

    container.innerHTML = html;
}

async function autoTrainModels() {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = 'Treinando...';

    try {
        const response = await fetch('/api/data/auto_train', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Erro ao treinar modelos');
        }

        // Display results
        displayTrainingResults(result);

        document.getElementById('trainingResults').style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao treinar modelos: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '🎯 Retreinar Modelos Automaticamente';
    }
}

function displayTrainingResults(result) {
    const container = document.getElementById('trainingResults');

    let html = '<div class="alert alert-success">';
    html += `<h4>✅ ${result.message}</h4>`;
    html += `<p><strong>Amostras de treino:</strong> ${result.training_samples}</p>`;
    html += `<p><strong>Modelos treinados:</strong> ${result.models.join(', ')}</p>`;

    if (result.performance) {
        html += '<h4>Performance dos Modelos:</h4><ul>';
        for (const [model, metrics] of Object.entries(result.performance)) {
            html += `<li><strong>${model}:</strong> MAE = R$ ${metrics.mae.toFixed(0)}, R² = ${metrics.r2.toFixed(3)}</li>`;
        }
        html += '</ul>';
    }

    html += '</div>';

    container.innerHTML = html;
}
```

### 3. CSS Styles

#### Arquivo: `static/css/style.css` (adicionar)

```css
/* Upload Area */
.upload-area {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    transition: all 0.3s;
    cursor: pointer;
}

.upload-area:hover {
    border-color: #2196F3;
    background-color: #f9f9f9;
}

.upload-area.dragover {
    border-color: #2196F3;
    background-color: #e3f2fd;
}

.upload-icon {
    color: #666;
    margin-bottom: 20px;
}

.upload-hint {
    color: #999;
    font-size: 14px;
    margin: 10px 0;
}

.upload-formats {
    font-size: 12px;
    color: #999;
    margin-top: 10px;
}

.file-name {
    margin-top: 15px;
    padding: 10px;
    background: #f0f0f0;
    border-radius: 5px;
    font-weight: bold;
}

.import-summary {
    margin-top: 20px;
}

.error-list {
    max-height: 200px;
    overflow-y: auto;
    background: #f9f9f9;
    padding: 15px;
    border-radius: 5px;
}

.error-list li {
    margin-bottom: 5px;
    color: #d32f2f;
}
```

## 📅 Cronograma de Implementação

**Total: 1 semana**

- **Dias 1-2:** Backend - DataImporter class
- **Dias 3-4:** Frontend - Upload UI
- **Dia 5:** Auto-retrain functionality e testes

## ✅ Critérios de Aceitação

- [ ] Upload de CSV e Excel funcionando
- [ ] Validação de formato e dados
- [ ] Template disponível para download
- [ ] Import salva corretamente no database
- [ ] Auto-retrain funciona com novos dados
- [ ] Feedback claro de sucesso/erros
- [ ] Documentação das colunas esperadas

**Esforço Total:** ~1 semana (1 desenvolvedor)

---

# Resumo dos Planos de Implementação

## 📊 Visão Geral

| Feature | Prioridade | Esforço | Impacto |
|---------|-----------|---------|---------|
| #4 + #5: Sistema de CoD | 🔥 Alta | 2-3 semanas | Muito Alto |
| #6: Feature Importance | 🔥 Alta | 3-5 dias | Médio |
| #12: Visualizações Avançadas | 🟡 Média | 1 semana | Médio |
| #13: Upload de Dados | 🟡 Média | 1 semana | Médio |
| #16: Clustering | 🟢 Baixa | 2 semanas | Baixo-Médio |
| #18: Otimização Portfólio | 🔥 Alta | 2 semanas | Alto |
| #19: Modelo de Sucesso | 🟡 Média | 1-2 semanas | Médio |
| #20: Persistência | 🟢 Baixa | 1 semana | Baixo |

## 🚀 Roadmap Consolidado

### Sprint 1 (2-3 semanas): CoD + Feature Importance
- Implementar sistema completo de CoD
- Adicionar visualização de feature importance
- **Resultado:** Funcionalidade crítica de CoD + melhor interpretabilidade

### Sprint 2 (2 semanas): Dados e Visualizações
- Upload de dados históricos
- Visualizações avançadas (scatter, box, heatmap)
- **Resultado:** Personalização do modelo + análise exploratória rica

### Sprint 3 (2 semanas): Otimização de Portfólio
- Solver de otimização (PuLP)
- Maximização de valor com restrições
- **Resultado:** Diferencial competitivo único

### Sprint 4 (2 semanas): Modelos Avançados
- Modelo de sucesso do projeto
- Clustering e análise de causas
- **Resultado:** Insights avançados

### Sprint 5 (1 semana): Refinamentos
- Persistência de modelos
- API REST
- Documentação completa
- **Resultado:** Sistema robusto e escalável

**Total Estimado:** 9-11 semanas para implementação completa

---

**Documento criado em:** 2025-11-05
**Próxima revisão:** Após conclusão de cada sprint
**Contato:** [Seu contato]
