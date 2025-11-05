# Feature #16: Análise de Causas com Clustering

## 🎯 Objetivo
Implementar clustering de projetos para identificar padrões de sucesso/falha e causas raiz de atrasos.

## 📊 Status Atual
🟡 **Implementado Parcial** - Alertas existem, mas clustering não implementado

## 🔧 Componentes a Implementar

### 1. Backend - Módulo de Clustering

#### Arquivo: `project_clustering.py` (novo)

```python
"""
Project Clustering Module
Identifies patterns in project data using unsupervised learning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

from models import Project


class ProjectClusterer:
    """
    Cluster projects to identify patterns and similarities.
    """

    def __init__(self, n_clusters: int = 4):
        """
        Initialize Project Clusterer.

        Args:
            n_clusters: Number of clusters for K-Means
        """
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.pca = None
        self.feature_names = []
        self.cluster_labels = None
        self.cluster_centers = None

    def prepare_features(self, projects: List[Project]) -> pd.DataFrame:
        """
        Prepare features for clustering.

        Args:
            projects: List of Project objects

        Returns:
            DataFrame with features
        """
        data = []

        for project in projects:
            features = {
                'duration_weeks': project.duration_weeks or 12,
                'team_size': project.team_size or 5,
                'budget': project.budget or 100000,
                'business_value': project.business_value or 50,
                'capacity_allocated': project.capacity_allocated or project.team_size,
                'risk_level_numeric': {'low': 1, 'medium': 3, 'high': 5, 'critical': 7}.get(project.risk_level, 3),
                'priority_numeric': {'low': 1, 'medium': 2, 'high': 3}.get(project.priority, 2)
            }

            # Add derived features
            features['budget_per_week'] = features['budget'] / features['duration_weeks']
            features['budget_per_person'] = features['budget'] / features['team_size']
            features['capacity_utilization'] = features['capacity_allocated'] / features['team_size']

            data.append(features)

        df = pd.DataFrame(data)
        self.feature_names = df.columns.tolist()

        return df

    def find_optimal_clusters(self, X: np.ndarray, max_clusters: int = 10) -> int:
        """
        Find optimal number of clusters using elbow method and silhouette score.

        Args:
            X: Feature matrix
            max_clusters: Maximum number of clusters to test

        Returns:
            Optimal number of clusters
        """
        inertias = []
        silhouette_scores = []

        max_k = min(max_clusters, len(X) - 1)

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)

            inertias.append(kmeans.inertia_)

            if k < len(X):
                score = silhouette_score(X, labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)

        # Find elbow using second derivative
        if len(inertias) >= 3:
            second_derivative = np.diff(np.diff(inertias))
            elbow_index = np.argmax(second_derivative) + 2
        else:
            elbow_index = 2

        # Find best silhouette score
        best_silhouette_index = np.argmax(silhouette_scores) + 2

        # Average the two methods
        optimal_k = int((elbow_index + best_silhouette_index) / 2)
        optimal_k = max(2, min(optimal_k, max_k))

        return optimal_k

    def cluster_projects(self, projects: List[Project], auto_k: bool = True) -> Dict:
        """
        Cluster projects using K-Means.

        Args:
            projects: List of projects to cluster
            auto_k: If True, automatically determine optimal number of clusters

        Returns:
            Dictionary with clustering results
        """
        if len(projects) < 4:
            raise ValueError("Need at least 4 projects for clustering")

        # Prepare features
        df = self.prepare_features(projects)
        X = self.scaler.fit_transform(df)

        # Find optimal clusters if requested
        if auto_k:
            self.n_clusters = self.find_optimal_clusters(X)
            print(f"Optimal number of clusters: {self.n_clusters}")

        # Perform clustering
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.cluster_labels = self.kmeans.fit_predict(X)
        self.cluster_centers = self.kmeans.cluster_centers_

        # PCA for visualization
        self.pca = PCA(n_components=2)
        X_pca = self.pca.fit_transform(X)

        # Analyze clusters
        cluster_analysis = self.analyze_clusters(projects, df, self.cluster_labels)

        # Silhouette score
        silhouette = silhouette_score(X, self.cluster_labels)

        return {
            'n_clusters': self.n_clusters,
            'cluster_labels': self.cluster_labels.tolist(),
            'cluster_analysis': cluster_analysis,
            'silhouette_score': float(silhouette),
            'pca_coordinates': X_pca.tolist(),
            'explained_variance': self.pca.explained_variance_ratio_.tolist()
        }

    def analyze_clusters(self, projects: List[Project],
                        features_df: pd.DataFrame,
                        labels: np.ndarray) -> List[Dict]:
        """
        Analyze characteristics of each cluster.

        Args:
            projects: List of projects
            features_df: DataFrame with features
            labels: Cluster labels

        Returns:
            List of cluster analysis dictionaries
        """
        cluster_analysis = []

        for cluster_id in range(self.n_clusters):
            mask = labels == cluster_id
            cluster_projects = [p for i, p in enumerate(projects) if mask[i]]
            cluster_features = features_df[mask]

            # Calculate statistics
            stats = {
                'cluster_id': int(cluster_id),
                'project_count': int(np.sum(mask)),
                'projects': [{'id': p.id, 'name': p.name} for p in cluster_projects[:10]],  # Top 10
                'avg_duration_weeks': float(cluster_features['duration_weeks'].mean()),
                'avg_team_size': float(cluster_features['team_size'].mean()),
                'avg_budget': float(cluster_features['budget'].mean()),
                'avg_business_value': float(cluster_features['business_value'].mean()),
                'dominant_risk_level': self.get_dominant_risk(cluster_projects),
                'dominant_priority': self.get_dominant_priority(cluster_projects)
            }

            # Generate insights
            stats['insights'] = self.generate_cluster_insights(stats, cluster_projects)

            cluster_analysis.append(stats)

        return cluster_analysis

    def get_dominant_risk(self, projects: List[Project]) -> str:
        """Get most common risk level in cluster"""
        risk_levels = [p.risk_level for p in projects if p.risk_level]

        if not risk_levels:
            return 'medium'

        return max(set(risk_levels), key=risk_levels.count)

    def get_dominant_priority(self, projects: List[Project]) -> str:
        """Get most common priority in cluster"""
        priorities = [p.priority for p in projects if p.priority]

        if not priorities:
            return 'medium'

        return max(set(priorities), key=priorities.count)

    def generate_cluster_insights(self, stats: Dict, projects: List[Project]) -> List[str]:
        """
        Generate actionable insights for a cluster.

        Args:
            stats: Cluster statistics
            projects: Projects in cluster

        Returns:
            List of insight strings
        """
        insights = []

        # Duration insights
        if stats['avg_duration_weeks'] > 24:
            insights.append("Cluster de projetos longos - considere entregas incrementais")
        elif stats['avg_duration_weeks'] < 8:
            insights.append("Cluster de projetos rápidos - ideais para vitórias rápidas")

        # Budget insights
        if stats['avg_budget'] > 1_000_000:
            insights.append("Cluster de alto investimento - requer governança rigorosa")
        elif stats['avg_budget'] < 200_000:
            insights.append("Cluster de baixo orçamento - projetos táticos")

        # Business value insights
        if stats['avg_business_value'] > 70:
            insights.append("Cluster de alto valor estratégico - priorizar recursos")
        elif stats['avg_business_value'] < 40:
            insights.append("Cluster de baixo valor - avaliar necessidade de execução")

        # Risk insights
        if stats['dominant_risk_level'] in ['high', 'critical']:
            insights.append(f"Cluster de alto risco ({stats['dominant_risk_level']}) - implementar planos de mitigação")

        # Team size insights
        if stats['avg_team_size'] > 10:
            insights.append("Cluster de equipes grandes - atenção à coordenação")
        elif stats['avg_team_size'] < 3:
            insights.append("Cluster de equipes pequenas - risco de dependências de pessoas-chave")

        return insights

    def identify_success_patterns(self, projects: List[Project],
                                  success_criteria: str = 'on_time') -> Dict:
        """
        Identify patterns in successful vs failed projects.

        Args:
            projects: List of projects
            success_criteria: Criteria for success ('on_time', 'within_budget', etc.)

        Returns:
            Dictionary with success patterns
        """
        # Separate successful and failed projects
        successful = []
        failed = []

        for project in projects:
            # Determine success based on criteria
            is_successful = False

            if success_criteria == 'on_time':
                # Check if project has forecasts and was on time
                if project.forecasts:
                    latest_forecast = max(project.forecasts, key=lambda f: f.created_at)
                    is_successful = latest_forecast.can_meet_deadline
            elif success_criteria == 'completed':
                is_successful = project.status == 'completed'

            if is_successful:
                successful.append(project)
            else:
                failed.append(project)

        if len(successful) < 2 or len(failed) < 2:
            return {
                'error': 'Insufficient data for pattern analysis',
                'successful_count': len(successful),
                'failed_count': len(failed)
            }

        # Compare characteristics
        successful_features = self.prepare_features(successful)
        failed_features = self.prepare_features(failed)

        comparison = {}
        for feature in self.feature_names:
            comparison[feature] = {
                'successful_avg': float(successful_features[feature].mean()),
                'failed_avg': float(failed_features[feature].mean()),
                'difference_pct': float(
                    ((successful_features[feature].mean() - failed_features[feature].mean()) /
                     failed_features[feature].mean()) * 100
                ) if failed_features[feature].mean() != 0 else 0
            }

        # Identify key differentiators
        key_factors = sorted(
            comparison.items(),
            key=lambda x: abs(x[1]['difference_pct']),
            reverse=True
        )[:5]

        return {
            'successful_count': len(successful),
            'failed_count': len(failed),
            'success_rate': len(successful) / len(projects) * 100,
            'comparison': comparison,
            'key_differentiators': [
                {
                    'feature': factor[0],
                    'successful_avg': factor[1]['successful_avg'],
                    'failed_avg': factor[1]['failed_avg'],
                    'difference_pct': factor[1]['difference_pct']
                }
                for factor in key_factors
            ],
            'recommendations': self.generate_success_recommendations(key_factors)
        }

    def generate_success_recommendations(self, key_factors: List[Tuple]) -> List[str]:
        """Generate recommendations based on success patterns"""
        recommendations = []

        for factor_name, stats in key_factors[:3]:
            diff_pct = stats['difference_pct']

            if 'budget' in factor_name and diff_pct > 20:
                recommendations.append(
                    f"Projetos bem-sucedidos têm {diff_pct:.0f}% mais orçamento - "
                    "garanta recursos adequados"
                )
            elif 'team_size' in factor_name and diff_pct > 15:
                recommendations.append(
                    f"Projetos bem-sucedidos têm equipes {diff_pct:.0f}% maiores - "
                    "considere aumentar alocação de pessoal"
                )
            elif 'duration' in factor_name and diff_pct < -20:
                recommendations.append(
                    f"Projetos bem-sucedidos são {abs(diff_pct):.0f}% mais curtos - "
                    "divida projetos longos em entregas menores"
                )
            elif 'business_value' in factor_name:
                recommendations.append(
                    f"Foco em projetos de alto valor aumenta chance de sucesso - "
                    "priorize projetos com business value > {stats['successful_avg']:.0f}"
                )

        return recommendations
```

#### Arquivo: `app.py` (adicionar rotas)

```python
from project_clustering import ProjectClusterer

@app.route('/api/clustering/cluster_projects', methods=['POST'])
def cluster_projects():
    """Cluster active projects"""
    try:
        data = request.json
        auto_k = data.get('auto_k', True)
        n_clusters = data.get('n_clusters', 4)

        # Get active projects
        projects = Project.query.filter_by(status='active').all()

        if len(projects) < 4:
            return jsonify({'error': 'Need at least 4 active projects for clustering'}), 400

        # Cluster
        clusterer = ProjectClusterer(n_clusters=n_clusters)
        result = clusterer.cluster_projects(projects, auto_k=auto_k)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clustering/success_patterns', methods=['POST'])
def analyze_success_patterns():
    """Analyze patterns in successful vs failed projects"""
    try:
        data = request.json
        criteria = data.get('success_criteria', 'on_time')

        # Get all projects
        projects = Project.query.all()

        if len(projects) < 10:
            return jsonify({'error': 'Need at least 10 projects for pattern analysis'}), 400

        # Analyze
        clusterer = ProjectClusterer()
        result = clusterer.identify_success_patterns(projects, success_criteria=criteria)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Frontend - Clustering Dashboard

#### Arquivo: `templates/clustering_analysis.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Análise de Clustering - Padrões de Projetos</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>🔍 Análise de Clustering</h1>
        <p class="subtitle">Identifique padrões e similaridades entre projetos</p>

        <div class="card">
            <h2>Configuração do Clustering</h2>

            <div class="form-group">
                <label>
                    <input type="checkbox" id="autoK" checked>
                    Determinar número de clusters automaticamente
                </label>
            </div>

            <div class="form-group" id="manualKGroup" style="display: none;">
                <label>Número de Clusters:</label>
                <input type="number" id="nClusters" min="2" max="10" value="4">
            </div>

            <button onclick="runClustering()" class="btn-primary">
                Executar Clustering
            </button>
        </div>

        <div id="clusteringResults" style="display: none;">
            <div class="card">
                <h2>Visualização dos Clusters</h2>
                <canvas id="clusterChart"></canvas>
            </div>

            <div class="card">
                <h2>Análise por Cluster</h2>
                <div id="clusterCards"></div>
            </div>
        </div>

        <div class="card">
            <h2>Padrões de Sucesso</h2>

            <div class="form-group">
                <label>Critério de Sucesso:</label>
                <select id="successCriteria">
                    <option value="on_time">No Prazo</option>
                    <option value="completed">Concluído</option>
                </select>
            </div>

            <button onclick="analyzeSuccessPatterns()" class="btn-secondary">
                Analisar Padrões
            </button>

            <div id="successResults" style="display: none; margin-top: 20px;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/clustering.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/clustering.js` (novo)

```javascript
let clusterChart = null;

document.getElementById('autoK').addEventListener('change', (e) => {
    document.getElementById('manualKGroup').style.display =
        e.target.checked ? 'none' : 'block';
});

async function runClustering() {
    const autoK = document.getElementById('autoK').checked;
    const nClusters = parseInt(document.getElementById('nClusters').value);

    try {
        const response = await fetch('/api/clustering/cluster_projects', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                auto_k: autoK,
                n_clusters: nClusters
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const result = await response.json();

        // Display results
        displayClusteringResults(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao executar clustering: ' + error.message);
    }
}

function displayClusteringResults(result) {
    // Show results section
    document.getElementById('clusteringResults').style.display = 'block';

    // Create scatter plot
    createClusterScatterPlot(result);

    // Display cluster cards
    displayClusterCards(result.cluster_analysis);
}

function createClusterScatterPlot(result) {
    const ctx = document.getElementById('clusterChart').getContext('2d');

    if (clusterChart) {
        clusterChart.destroy();
    }

    // Prepare datasets for each cluster
    const datasets = [];
    const colors = [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)'
    ];

    for (let i = 0; i < result.n_clusters; i++) {
        const clusterPoints = [];

        result.cluster_labels.forEach((label, idx) => {
            if (label === i) {
                clusterPoints.push({
                    x: result.pca_coordinates[idx][0],
                    y: result.pca_coordinates[idx][1]
                });
            }
        });

        datasets.push({
            label: `Cluster ${i + 1}`,
            data: clusterPoints,
            backgroundColor: colors[i % colors.length],
            borderColor: colors[i % colors.length].replace('0.6', '1'),
            borderWidth: 1
        });
    }

    clusterChart = new Chart(ctx, {
        type: 'scatter',
        data: {datasets},
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Visualização dos ${result.n_clusters} Clusters (PCA)`
                },
                subtitle: {
                    display: true,
                    text: `Silhouette Score: ${result.silhouette_score.toFixed(3)}`
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: `PC1 (${(result.explained_variance[0] * 100).toFixed(1)}%)`
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: `PC2 (${(result.explained_variance[1] * 100).toFixed(1)}%)`
                    }
                }
            }
        }
    });
}

function displayClusterCards(clusterAnalysis) {
    const container = document.getElementById('clusterCards');
    container.innerHTML = '';

    clusterAnalysis.forEach(cluster => {
        const card = document.createElement('div');
        card.className = 'cluster-card';

        let projectsList = cluster.projects.slice(0, 5).map(p => p.name).join(', ');
        if (cluster.project_count > 5) {
            projectsList += ` (+${cluster.project_count - 5} mais)`;
        }

        card.innerHTML = `
            <h3>Cluster ${cluster.cluster_id + 1}</h3>
            <p><strong>Projetos:</strong> ${cluster.project_count}</p>

            <div class="cluster-stats">
                <p>📅 Duração Média: ${cluster.avg_duration_weeks.toFixed(1)} semanas</p>
                <p>👥 Equipe Média: ${cluster.avg_team_size.toFixed(1)} pessoas</p>
                <p>💰 Orçamento Médio: R$ ${cluster.avg_budget.toLocaleString()}</p>
                <p>⭐ Valor Médio: ${cluster.avg_business_value.toFixed(0)}/100</p>
                <p>⚠️ Risco Dominante: ${cluster.dominant_risk_level}</p>
                <p>🎯 Prioridade Dominante: ${cluster.dominant_priority}</p>
            </div>

            <div class="cluster-insights">
                <h4>💡 Insights:</h4>
                <ul>
                    ${cluster.insights.map(insight => `<li>${insight}</li>`).join('')}
                </ul>
            </div>

            <details>
                <summary>Ver Projetos</summary>
                <p class="projects-list">${projectsList}</p>
            </details>
        `;

        container.appendChild(card);
    });
}

async function analyzeSuccessPatterns() {
    const criteria = document.getElementById('successCriteria').value;

    try {
        const response = await fetch('/api/clustering/success_patterns', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                success_criteria: criteria
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const result = await response.json();

        displaySuccessPatterns(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao analisar padrões: ' + error.message);
    }
}

function displaySuccessPatterns(result) {
    const container = document.getElementById('successResults');

    let html = '<div class="success-analysis">';

    html += `
        <h3>Taxa de Sucesso: ${result.success_rate.toFixed(1)}%</h3>
        <p>Bem-sucedidos: ${result.successful_count} | Fracassados: ${result.failed_count}</p>
    `;

    html += '<h4>🎯 Principais Diferenciadores:</h4><table class="data-table"><thead><tr>';
    html += '<th>Fator</th><th>Bem-sucedidos</th><th>Fracassados</th><th>Diferença</th></tr></thead><tbody>';

    result.key_differentiators.forEach(factor => {
        const diff = factor.difference_pct > 0 ? '+' : '';
        html += `<tr>
            <td><strong>${factor.feature}</strong></td>
            <td>${factor.successful_avg.toFixed(2)}</td>
            <td>${factor.failed_avg.toFixed(2)}</td>
            <td class="${factor.difference_pct > 0 ? 'positive' : 'negative'}">
                ${diff}${factor.difference_pct.toFixed(1)}%
            </td>
        </tr>`;
    });

    html += '</tbody></table>';

    html += '<h4>💡 Recomendações:</h4><ul>';
    result.recommendations.forEach(rec => {
        html += `<li>${rec}</li>`;
    });
    html += '</ul></div>';

    container.innerHTML = html;
    container.style.display = 'block';
}
```

## 📅 Cronograma de Implementação

**Total: 2 semanas**

- **Semana 1:**
  - Dias 1-3: Backend - ProjectClusterer class
  - Dias 4-5: API endpoints

- **Semana 2:**
  - Dias 1-3: Frontend - Dashboard de clustering
  - Dias 4-5: Análise de padrões de sucesso e testes

## ✅ Critérios de Aceitação

- [ ] K-Means clustering funcional
- [ ] Determinação automática de k
- [ ] Visualização PCA dos clusters
- [ ] Análise detalhada de cada cluster
- [ ] Padrões de sucesso identificados
- [ ] Recomendações acionáveis geradas
- [ ] Interface intuitiva e informativa

**Esforço Total:** ~2 semanas (1 desenvolvedor)

---

# Feature #18: Otimização Matemática de Portfólio

## 🎯 Objetivo
Implementar solver de otimização (Programação Linear) para maximizar valor do portfólio com restrições.

## 📊 Status Atual
🟡 **Implementado Parcial** - Análise de capacidade existe, solver não implementado

## 🔧 Componentes a Implementar

### 1. Backend - Módulo de Otimização

#### Arquivo: `requirements.txt` (adicionar)

```txt
pulp>=2.7.0
```

#### Arquivo: `portfolio_optimizer.py` (novo)

```python
"""
Portfolio Optimization Module
Uses Linear Programming to optimize project selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pulp import *

from models import Project


class PortfolioOptimizer:
    """
    Optimize project portfolio using Linear Programming.
    Maximizes value subject to constraints (budget, resources, etc.)
    """

    def __init__(self):
        self.problem = None
        self.decision_vars = {}
        self.results = None

    def optimize_npv(self,
                    projects: List[Project],
                    budget_constraint: float,
                    resource_constraint: Optional[float] = None,
                    risk_limit: Optional[str] = None,
                    min_business_value: Optional[int] = None,
                    diversification_constraints: Optional[Dict] = None) -> Dict:
        """
        Optimize portfolio to maximize NPV.

        Args:
            projects: List of Project objects
            budget_constraint: Maximum total budget
            resource_constraint: Maximum total FTEs
            risk_limit: Maximum risk level to include ('low', 'medium', 'high')
            min_business_value: Minimum business value for projects
            diversification_constraints: Dict with max projects per category

        Returns:
            Dictionary with optimization results
        """
        if len(projects) == 0:
            raise ValueError("No projects provided for optimization")

        # Create the problem
        self.problem = LpProblem("Portfolio_Optimization", LpMaximize)

        # Decision variables (0 or 1 for each project)
        self.decision_vars = {}
        for project in projects:
            var_name = f"select_project_{project.id}"
            self.decision_vars[project.id] = LpVariable(var_name, cat='Binary')

        # Objective function: Maximize total NPV (using business_value as proxy)
        # In real scenario, NPV should be calculated
        objective = []
        for project in projects:
            # Simple NPV proxy: business_value * budget
            npv_proxy = project.business_value * project.budget / 1_000_000 if project.budget else 0
            objective.append(npv_proxy * self.decision_vars[project.id])

        self.problem += lpSum(objective), "Total_NPV"

        # Constraint 1: Budget
        budget_terms = []
        for project in projects:
            budget = project.budget if project.budget else 0
            budget_terms.append(budget * self.decision_vars[project.id])

        self.problem += lpSum(budget_terms) <= budget_constraint, "Budget_Constraint"

        # Constraint 2: Resources (optional)
        if resource_constraint is not None:
            resource_terms = []
            for project in projects:
                capacity = project.capacity_allocated if project.capacity_allocated else project.team_size
                resource_terms.append(capacity * self.decision_vars[project.id])

            self.problem += lpSum(resource_terms) <= resource_constraint, "Resource_Constraint"

        # Constraint 3: Risk limit (optional)
        if risk_limit is not None:
            risk_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            max_risk = risk_levels.get(risk_limit, 3)

            for project in projects:
                project_risk = risk_levels.get(project.risk_level, 2)
                if project_risk > max_risk:
                    # Force this project to 0
                    self.problem += self.decision_vars[project.id] == 0, f"Risk_Exclude_{project.id}"

        # Constraint 4: Minimum business value (optional)
        if min_business_value is not None:
            for project in projects:
                if project.business_value < min_business_value:
                    self.problem += self.decision_vars[project.id] == 0, f"MinValue_Exclude_{project.id}"

        # Constraint 5: Diversification (optional)
        if diversification_constraints:
            # Group by owner
            if 'max_per_owner' in diversification_constraints:
                owners = set(p.owner for p in projects if p.owner)
                for owner in owners:
                    owner_projects = [p for p in projects if p.owner == owner]
                    owner_vars = [self.decision_vars[p.id] for p in owner_projects]
                    self.problem += lpSum(owner_vars) <= diversification_constraints['max_per_owner'], \
                                   f"Diversification_Owner_{owner}"

            # Group by priority
            if 'min_high_priority' in diversification_constraints:
                high_priority_projects = [p for p in projects if p.priority == 'high']
                high_priority_vars = [self.decision_vars[p.id] for p in high_priority_projects]
                self.problem += lpSum(high_priority_vars) >= diversification_constraints['min_high_priority'], \
                               "Min_High_Priority"

        # Solve the problem
        solver = PULP_CBC_CMD(msg=0)  # Silent solver
        status = self.problem.solve(solver)

        # Extract results
        selected_projects = []
        rejected_projects = []

        total_budget_used = 0
        total_resources_used = 0
        total_npv = 0

        for project in projects:
            is_selected = value(self.decision_vars[project.id]) == 1

            project_info = {
                'id': project.id,
                'name': project.name,
                'budget': project.budget or 0,
                'business_value': project.business_value or 0,
                'risk_level': project.risk_level,
                'priority': project.priority,
                'capacity_allocated': project.capacity_allocated or project.team_size
            }

            if is_selected:
                selected_projects.append(project_info)
                total_budget_used += project.budget or 0
                total_resources_used += project.capacity_allocated or project.team_size
                npv_proxy = project.business_value * (project.budget / 1_000_000) if project.budget else 0
                total_npv += npv_proxy
            else:
                rejected_projects.append(project_info)

        return {
            'status': LpStatus[status],
            'selected_projects': selected_projects,
            'rejected_projects': rejected_projects,
            'summary': {
                'total_projects_selected': len(selected_projects),
                'total_budget_used': float(total_budget_used),
                'budget_constraint': float(budget_constraint),
                'budget_utilization_pct': float(total_budget_used / budget_constraint * 100) if budget_constraint > 0 else 0,
                'total_resources_used': float(total_resources_used),
                'resource_constraint': float(resource_constraint) if resource_constraint else None,
                'resource_utilization_pct': float(total_resources_used / resource_constraint * 100) if resource_constraint else None,
                'total_npv': float(total_npv)
            },
            'constraints_applied': {
                'budget_constraint': budget_constraint,
                'resource_constraint': resource_constraint,
                'risk_limit': risk_limit,
                'min_business_value': min_business_value,
                'diversification_constraints': diversification_constraints
            }
        }

    def sensitivity_analysis(self,
                            projects: List[Project],
                            base_budget: float,
                            budget_range: Tuple[float, float] = (0.8, 1.2),
                            steps: int = 5) -> Dict:
        """
        Perform sensitivity analysis by varying budget constraint.

        Args:
            projects: List of projects
            base_budget: Base budget value
            budget_range: (min_multiplier, max_multiplier) for budget variation
            steps: Number of steps in sensitivity analysis

        Returns:
            Dictionary with sensitivity results
        """
        results = []

        budgets = np.linspace(base_budget * budget_range[0],
                             base_budget * budget_range[1],
                             steps)

        for budget in budgets:
            opt_result = self.optimize_npv(projects, budget_constraint=budget)

            results.append({
                'budget': float(budget),
                'projects_selected': opt_result['summary']['total_projects_selected'],
                'total_npv': opt_result['summary']['total_npv'],
                'budget_utilization': opt_result['summary']['budget_utilization_pct']
            })

        return {
            'base_budget': float(base_budget),
            'budget_range': budget_range,
            'results': results
        }

    def compare_scenarios(self,
                         projects: List[Project],
                         scenarios: List[Dict]) -> Dict:
        """
        Compare multiple optimization scenarios.

        Args:
            projects: List of projects
            scenarios: List of scenario dictionaries with constraints

        Returns:
            Comparison results
        """
        scenario_results = []

        for i, scenario in enumerate(scenarios):
            result = self.optimize_npv(
                projects,
                budget_constraint=scenario.get('budget_constraint'),
                resource_constraint=scenario.get('resource_constraint'),
                risk_limit=scenario.get('risk_limit'),
                min_business_value=scenario.get('min_business_value'),
                diversification_constraints=scenario.get('diversification_constraints')
            )

            scenario_results.append({
                'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                'result': result
            })

        return {
            'scenarios': scenario_results,
            'comparison': self._generate_scenario_comparison(scenario_results)
        }

    def _generate_scenario_comparison(self, scenario_results: List[Dict]) -> Dict:
        """Generate comparison metrics across scenarios"""
        comparison = {
            'projects_selected': [],
            'budget_used': [],
            'npv': [],
            'resource_used': []
        }

        for scenario in scenario_results:
            comparison['projects_selected'].append({
                'scenario': scenario['scenario_name'],
                'count': scenario['result']['summary']['total_projects_selected']
            })
            comparison['budget_used'].append({
                'scenario': scenario['scenario_name'],
                'value': scenario['result']['summary']['total_budget_used']
            })
            comparison['npv'].append({
                'scenario': scenario['scenario_name'],
                'value': scenario['result']['summary']['total_npv']
            })

        return comparison
```

#### Arquivo: `app.py` (adicionar rotas)

```python
from portfolio_optimizer import PortfolioOptimizer

@app.route('/api/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio using Linear Programming"""
    try:
        data = request.json

        # Get candidate projects
        projects = Project.query.filter(
            Project.status.in_(['active', 'on_hold'])
        ).all()

        if len(projects) == 0:
            return jsonify({'error': 'No projects available for optimization'}), 400

        # Extract constraints
        budget_constraint = float(data.get('budget_constraint'))
        resource_constraint = data.get('resource_constraint')
        risk_limit = data.get('risk_limit')
        min_business_value = data.get('min_business_value')
        diversification = data.get('diversification_constraints')

        # Optimize
        optimizer = PortfolioOptimizer()
        result = optimizer.optimize_npv(
            projects,
            budget_constraint=budget_constraint,
            resource_constraint=float(resource_constraint) if resource_constraint else None,
            risk_limit=risk_limit,
            min_business_value=int(min_business_value) if min_business_value else None,
            diversification_constraints=diversification
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/sensitivity', methods=['POST'])
def portfolio_sensitivity():
    """Perform sensitivity analysis on budget"""
    try:
        data = request.json

        projects = Project.query.filter(
            Project.status.in_(['active', 'on_hold'])
        ).all()

        base_budget = float(data.get('base_budget'))
        budget_range = tuple(data.get('budget_range', [0.8, 1.2]))
        steps = int(data.get('steps', 5))

        optimizer = PortfolioOptimizer()
        result = optimizer.sensitivity_analysis(
            projects,
            base_budget=base_budget,
            budget_range=budget_range,
            steps=steps
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/compare_scenarios', methods=['POST'])
def compare_optimization_scenarios():
    """Compare multiple optimization scenarios"""
    try:
        data = request.json

        projects = Project.query.filter(
            Project.status.in_(['active', 'on_hold'])
        ).all()

        scenarios = data.get('scenarios', [])

        if len(scenarios) == 0:
            return jsonify({'error': 'No scenarios provided'}), 400

        optimizer = PortfolioOptimizer()
        result = optimizer.compare_scenarios(projects, scenarios)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Frontend - Optimization Interface

#### Arquivo: `templates/portfolio_optimization.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Otimização de Portfólio</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>⚙️ Otimização de Portfólio</h1>
        <p class="subtitle">Maximize o valor do portfólio com restrições de orçamento e recursos</p>

        <div class="card">
            <h2>Restrições e Objetivos</h2>

            <div class="form-group">
                <label>Orçamento Máximo (R$):</label>
                <input type="number" id="budgetConstraint" step="100000" min="0" required>
            </div>

            <div class="form-group">
                <label>Recursos Máximos (FTEs) - Opcional:</label>
                <input type="number" id="resourceConstraint" step="1" min="0">
            </div>

            <div class="form-group">
                <label>Limite de Risco:</label>
                <select id="riskLimit">
                    <option value="">Sem limite</option>
                    <option value="low">Apenas Baixo Risco</option>
                    <option value="medium">Até Médio Risco</option>
                    <option value="high">Até Alto Risco</option>
                </select>
            </div>

            <div class="form-group">
                <label>Valor de Negócio Mínimo:</label>
                <input type="number" id="minBusinessValue" min="0" max="100" placeholder="0-100">
            </div>

            <h3>Restrições de Diversificação (Opcional)</h3>

            <div class="form-group">
                <label>Máximo de projetos por owner:</label>
                <input type="number" id="maxPerOwner" min="1">
            </div>

            <div class="form-group">
                <label>Mínimo de projetos de alta prioridade:</label>
                <input type="number" id="minHighPriority" min="0">
            </div>

            <button onclick="runOptimization()" class="btn-primary">
                🚀 Otimizar Portfólio
            </button>
        </div>

        <div id="optimizationResults" style="display: none;">
            <div class="card">
                <h2>Resultado da Otimização</h2>
                <div id="summaryMetrics"></div>
            </div>

            <div class="card">
                <h2>Projetos Selecionados</h2>
                <table id="selectedProjects" class="data-table"></table>
            </div>

            <div class="card">
                <h2>Projetos Não Selecionados</h2>
                <table id="rejectedProjects" class="data-table"></table>
            </div>
        </div>

        <div class="card">
            <h2>Análise de Sensibilidade</h2>
            <p>Varie o orçamento para ver como afeta o portfólio selecionado</p>

            <div class="form-group">
                <label>Orçamento Base (R$):</label>
                <input type="number" id="sensBase" step="100000" min="0">
            </div>

            <button onclick="runSensitivity()" class="btn-secondary">
                Executar Análise
            </button>

            <div id="sensitivityChart" style="display: none; margin-top: 20px;">
                <canvas id="sensChart"></canvas>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/portfolio_optimization.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/portfolio_optimization.js` (novo)

```javascript
async function runOptimization() {
    const budgetConstraint = parseFloat(document.getElementById('budgetConstraint').value);

    if (!budgetConstraint || budgetConstraint <= 0) {
        alert('Informe um orçamento máximo válido');
        return;
    }

    const resourceConstraint = document.getElementById('resourceConstraint').value;
    const riskLimit = document.getElementById('riskLimit').value;
    const minBusinessValue = document.getElementById('minBusinessValue').value;
    const maxPerOwner = document.getElementById('maxPerOwner').value;
    const minHighPriority = document.getElementById('minHighPriority').value;

    const data = {
        budget_constraint: budgetConstraint,
        resource_constraint: resourceConstraint || null,
        risk_limit: riskLimit || null,
        min_business_value: minBusinessValue || null,
        diversification_constraints: {}
    };

    if (maxPerOwner) {
        data.diversification_constraints.max_per_owner = parseInt(maxPerOwner);
    }
    if (minHighPriority) {
        data.diversification_constraints.min_high_priority = parseInt(minHighPriority);
    }

    try {
        const response = await fetch('/api/portfolio/optimize', {
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

        displayOptimizationResults(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao otimizar: ' + error.message);
    }
}

function displayOptimizationResults(result) {
    // Show results
    document.getElementById('optimizationResults').style.display = 'block';

    // Summary metrics
    const summary = result.summary;
    document.getElementById('summaryMetrics').innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Projetos Selecionados</h3>
                <p class="metric-value">${summary.total_projects_selected}</p>
            </div>
            <div class="metric-card">
                <h3>Orçamento Utilizado</h3>
                <p class="metric-value">R$ ${summary.total_budget_used.toLocaleString()}</p>
                <p class="metric-label">${summary.budget_utilization_pct.toFixed(1)}% do total</p>
            </div>
            <div class="metric-card">
                <h3>NPV Total</h3>
                <p class="metric-value">R$ ${summary.total_npv.toLocaleString()}</p>
            </div>
            ${summary.resource_utilization_pct !== null ? `
            <div class="metric-card">
                <h3>Recursos Utilizados</h3>
                <p class="metric-value">${summary.total_resources_used.toFixed(1)} FTEs</p>
                <p class="metric-label">${summary.resource_utilization_pct.toFixed(1)}% do total</p>
            </div>
            ` : ''}
        </div>
    `;

    // Selected projects table
    displayProjectTable(result.selected_projects, 'selectedProjects');

    // Rejected projects table
    displayProjectTable(result.rejected_projects, 'rejectedProjects');

    // Scroll to results
    document.getElementById('optimizationResults').scrollIntoView({behavior: 'smooth'});
}

function displayProjectTable(projects, tableId) {
    const table = document.getElementById(tableId);

    let html = '<thead><tr>';
    html += '<th>Projeto</th><th>Orçamento</th><th>Valor Negócio</th><th>Risco</th><th>Prioridade</th>';
    html += '</tr></thead><tbody>';

    projects.forEach(project => {
        html += '<tr>';
        html += `<td><strong>${project.name}</strong></td>`;
        html += `<td>R$ ${project.budget.toLocaleString()}</td>`;
        html += `<td>${project.business_value}/100</td>`;
        html += `<td><span class="badge badge-${project.risk_level}">${project.risk_level}</span></td>`;
        html += `<td><span class="badge badge-${project.priority}">${project.priority}</span></td>`;
        html += '</tr>';
    });

    html += '</tbody>';
    table.innerHTML = html;
}

async function runSensitivity() {
    const basebudget = parseFloat(document.getElementById('sensBase').value);

    if (!baseBudget || baseBudget <= 0) {
        alert('Informe um orçamento base válido');
        return;
    }

    try {
        const response = await fetch('/api/portfolio/sensitivity', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                base_budget: baseBudget,
                budget_range: [0.7, 1.3],
                steps: 10
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const result = await response.json();

        displaySensitivityChart(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro na análise: ' + error.message);
    }
}

function displaySensitivityChart(result) {
    document.getElementById('sensitivityChart').style.display = 'block';

    const ctx = document.getElementById('sensChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: result.results.map(r => `R$ ${(r.budget / 1e6).toFixed(1)}M`),
            datasets: [
                {
                    label: 'Projetos Selecionados',
                    data: result.results.map(r => r.projects_selected),
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    yAxisID: 'y'
                },
                {
                    label: 'NPV Total',
                    data: result.results.map(r => r.total_npv),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Análise de Sensibilidade - Variação de Orçamento'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Projetos'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'NPV (R$)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}
```

## 📅 Cronograma de Implementação

**Total: 2 semanas**

- **Semana 1:**
  - Dias 1-2: Backend - PortfolioOptimizer class
  - Dias 3-5: API endpoints e testes com PuLP

- **Semana 2:**
  - Dias 1-3: Frontend - Optimization UI
  - Dias 4-5: Sensitivity analysis e scenario comparison

## ✅ Critérios de Aceitação

- [ ] Otimização com PuLP funcionando
- [ ] Múltiplas restrições suportadas
- [ ] Análise de sensibilidade funcional
- [ ] Comparação de cenários
- [ ] Interface intuitiva
- [ ] Resultados apresentados claramente
- [ ] Testes com portfólios reais

**Esforço Total:** ~2 semanas (1 desenvolvedor)

---

# Feature #19: Modelo de Sucesso do Projeto

## 🎯 Objetivo
Implementar modelo de classificação (Random Forest Classifier) para prever probabilidade de sucesso de projetos.

## 📊 Status Atual
❌ **Não Implementado**

## 🔧 Componentes a Implementar

### 1. Backend - Módulo de Classificação de Sucesso

#### Arquivo: `project_success_classifier.py` (novo)

```python
"""
Project Success Classification Module
Predicts probability of project success using Random Forest Classifier
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, confusion_matrix, accuracy_score
)
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from models import Project, Forecast, Actual


class ProjectSuccessClassifier:
    """
    Classify projects as success or failure.
    Predicts probability of success based on project characteristics.
    """

    def __init__(self, n_splits: int = 5):
        """
        Initialize Project Success Classifier.

        Args:
            n_splits: Number of K-folds for cross-validation
        """
        self.n_splits = n_splits
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained = False
        self.success_threshold = 0.5  # Probability threshold for success

    def prepare_features(self, projects: List[Project],
                        forecasts_map: Dict[int, List[Forecast]],
                        actuals_map: Dict[int, List[Actual]]) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for classification.

        Args:
            projects: List of Project objects
            forecasts_map: Map of project_id to list of forecasts
            actuals_map: Map of project_id to list of actuals

        Returns:
            X: Feature matrix
            y: Target variable (0=failure, 1=success)
        """
        data = []
        labels = []

        for project in projects:
            # Only include completed projects with actual data
            if project.status != 'completed':
                continue

            # Determine success
            success = self._determine_success(project, forecasts_map, actuals_map)

            if success is None:
                continue  # Skip if we can't determine success

            # Extract features
            features = {
                # Project characteristics
                'duration_weeks': project.duration_weeks or 12,
                'team_size': project.team_size or 5,
                'budget_millions': (project.budget or 100000) / 1_000_000,
                'business_value': project.business_value or 50,
                'capacity_allocated': project.capacity_allocated or project.team_size,
                'risk_level_numeric': {'low': 1, 'medium': 3, 'high': 5, 'critical': 7}.get(project.risk_level, 3),
                'priority_numeric': {'low': 1, 'medium': 2, 'high': 3}.get(project.priority, 2),

                # Derived features
                'budget_per_week': ((project.budget or 100000) / 1_000_000) / (project.duration_weeks or 12),
                'budget_per_person': ((project.budget or 100000) / 1_000_000) / (project.team_size or 5),
                'capacity_utilization': (project.capacity_allocated or project.team_size) / (project.team_size or 5),
                'complexity_score': (project.duration_weeks or 12) * ({'low': 1, 'medium': 3, 'high': 5}.get(project.risk_level, 3)),

                # Forecast accuracy features (if available)
                'had_forecasts': int(project.id in forecasts_map and len(forecasts_map[project.id]) > 0),
                'num_forecasts': len(forecasts_map.get(project.id, [])),
            }

            # Add forecast accuracy if available
            if project.id in forecasts_map and project.id in actuals_map:
                forecasts = forecasts_map[project.id]
                actuals = actuals_map[project.id]

                if forecasts and actuals:
                    latest_forecast = forecasts[-1]
                    latest_actual = actuals[-1]

                    if latest_forecast.projected_weeks_p85 and latest_actual.actual_weeks_taken:
                        forecast_error = abs(latest_forecast.projected_weeks_p85 - latest_actual.actual_weeks_taken)
                        features['forecast_accuracy'] = 1 / (1 + forecast_error)  # Inverse error
                    else:
                        features['forecast_accuracy'] = 0.5  # Neutral
                else:
                    features['forecast_accuracy'] = 0.5
            else:
                features['forecast_accuracy'] = 0.5

            data.append(features)
            labels.append(success)

        if len(data) == 0:
            raise ValueError("No completed projects with success data available")

        df = pd.DataFrame(data)
        self.feature_names = df.columns.tolist()

        return df, pd.Series(labels)

    def _determine_success(self,
                          project: Project,
                          forecasts_map: Dict[int, List[Forecast]],
                          actuals_map: Dict[int, List[Actual]]) -> Optional[int]:
        """
        Determine if a project was successful.

        Success criteria:
        - Met deadline (if forecasted)
        - Within budget (if actual cost available)
        - High quality/satisfaction (if available)

        Returns:
            1 for success, 0 for failure, None if cannot determine
        """
        if project.status != 'completed':
            return None

        success_indicators = []

        # Check deadline
        if project.id in forecasts_map and project.id in actuals_map:
            forecasts = forecasts_map[project.id]
            actuals = actuals_map[project.id]

            if forecasts and actuals:
                latest_forecast = forecasts[-1]
                latest_actual = actuals[-1]

                if latest_forecast.can_meet_deadline:
                    success_indicators.append(1)
                else:
                    success_indicators.append(0)

                # Check if actual met forecast
                if latest_forecast.projected_weeks_p85 and latest_actual.actual_weeks_taken:
                    if latest_actual.actual_weeks_taken <= latest_forecast.projected_weeks_p85 * 1.1:  # 10% tolerance
                        success_indicators.append(1)
                    else:
                        success_indicators.append(0)

        # Check risk level (low risk projects are more likely to succeed)
        if project.risk_level in ['low', 'medium']:
            success_indicators.append(1)
        else:
            success_indicators.append(0)

        # Check business value delivery (assume high value projects were successful if completed)
        if project.business_value and project.business_value >= 60:
            success_indicators.append(1)
        else:
            success_indicators.append(0)

        # Determine overall success
        if len(success_indicators) == 0:
            return None

        # Majority vote
        success = int(sum(success_indicators) >= len(success_indicators) / 2)

        return success

    def train_models(self,
                    projects: List[Project],
                    forecasts_map: Dict[int, List[Forecast]],
                    actuals_map: Dict[int, List[Actual]]):
        """
        Train classification models.

        Args:
            projects: List of completed projects
            forecasts_map: Map of project_id to forecasts
            actuals_map: Map of project_id to actuals
        """
        X, y = self.prepare_features(projects, forecasts_map, actuals_map)

        if len(X) < 10:
            raise ValueError("Need at least 10 completed projects for training")

        print(f"\n{'='*60}")
        print(f"PROJECT SUCCESS CLASSIFICATION TRAINING")
        print(f"{'='*60}")
        print(f"Total samples: {len(X)}")
        print(f"Success rate: {y.mean()*100:.1f}%")
        print(f"Features: {len(self.feature_names)}")
        print(f"{'='*60}\n")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Model configurations
        models_config = {
            'RandomForest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=3,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting': GradientBoostingClassifier(
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
            fold_accuracies = []
            fold_roc_aucs = []

            for fold_num, (train_idx, val_idx) in enumerate(kfold.split(X_train_scaled), 1):
                X_fold_train = X_train_scaled[train_idx]
                X_fold_val = X_train_scaled[val_idx]
                y_fold_train = y_train.iloc[train_idx]
                y_fold_val = y_train.iloc[val_idx]

                # Train
                model.fit(X_fold_train, y_fold_train)

                # Predict
                y_pred = model.predict(X_fold_val)
                y_proba = model.predict_proba(X_fold_val)[:, 1]

                accuracy = accuracy_score(y_fold_val, y_pred)
                roc_auc = roc_auc_score(y_fold_val, y_proba)

                fold_accuracies.append(accuracy)
                fold_roc_aucs.append(roc_auc)

                print(f"Fold {fold_num}: Accuracy={accuracy:.3f}, ROC-AUC={roc_auc:.3f}")

            # Summary
            print(f"\nCross-Validation Summary:")
            print(f"  Accuracy: {np.mean(fold_accuracies):.3f} ± {np.std(fold_accuracies):.3f}")
            print(f"  ROC-AUC:  {np.mean(fold_roc_aucs):.3f} ± {np.std(fold_roc_aucs):.3f}")

            # Final training on full training set
            model.fit(X_train_scaled, y_train)

            # Test set evaluation
            y_pred_test = model.predict(X_test_scaled)
            y_proba_test = model.predict_proba(X_test_scaled)[:, 1]

            accuracy_test = accuracy_score(y_test, y_pred_test)
            roc_auc_test = roc_auc_score(y_test, y_proba_test)

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred_test)

            print(f"\nTest Set Performance:")
            print(f"  Accuracy: {accuracy_test:.3f}")
            print(f"  ROC-AUC:  {roc_auc_test:.3f}")
            print(f"\nConfusion Matrix:")
            print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
            print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

            # Store model
            self.models[name] = {
                'model': model,
                'accuracy': accuracy_test,
                'roc_auc': roc_auc_test,
                'confusion_matrix': cm.tolist()
            }

        self.trained = True
        print(f"\n{'='*60}")
        print(f"TRAINING COMPLETE - {len(self.models)} models trained")
        print(f"{'='*60}\n")

    def predict_success(self, project_dict: Dict, model_name: str = 'RandomForest') -> Dict:
        """
        Predict probability of success for a project.

        Args:
            project_dict: Dictionary with project characteristics
            model_name: Name of model to use

        Returns:
            Dictionary with success prediction
        """
        if not self.trained:
            raise ValueError("Models not trained. Call train_models() first.")

        # Prepare features (single project)
        features = {
            'duration_weeks': project_dict.get('duration_weeks', 12),
            'team_size': project_dict.get('team_size', 5),
            'budget_millions': project_dict.get('budget', 100000) / 1_000_000,
            'business_value': project_dict.get('business_value', 50),
            'capacity_allocated': project_dict.get('capacity_allocated', project_dict.get('team_size', 5)),
            'risk_level_numeric': {'low': 1, 'medium': 3, 'high': 5, 'critical': 7}.get(project_dict.get('risk_level', 'medium'), 3),
            'priority_numeric': {'low': 1, 'medium': 2, 'high': 3}.get(project_dict.get('priority', 'medium'), 2),
            'budget_per_week': (project_dict.get('budget', 100000) / 1_000_000) / project_dict.get('duration_weeks', 12),
            'budget_per_person': (project_dict.get('budget', 100000) / 1_000_000) / project_dict.get('team_size', 5),
            'capacity_utilization': project_dict.get('capacity_allocated', project_dict.get('team_size', 5)) / project_dict.get('team_size', 5),
            'complexity_score': project_dict.get('duration_weeks', 12) * {'low': 1, 'medium': 3, 'high': 5}.get(project_dict.get('risk_level', 'medium'), 3),
            'had_forecasts': 0,
            'num_forecasts': 0,
            'forecast_accuracy': 0.5
        }

        # Create DataFrame
        X = pd.DataFrame([features])[self.feature_names]
        X_scaled = self.scaler.transform(X)

        # Predict with selected model
        model = self.models[model_name]['model']
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]

        # Get predictions from all models (ensemble)
        all_probabilities = []
        for m_name, m_data in self.models.items():
            prob = m_data['model'].predict_proba(X_scaled)[0][1]
            all_probabilities.append(prob)

        prob_mean = np.mean(all_probabilities)
        prob_std = np.std(all_probabilities)

        return {
            'success_predicted': int(prediction),
            'success_probability': float(probability[1]),
            'failure_probability': float(probability[0]),
            'ensemble_probability': float(prob_mean),
            'probability_std': float(prob_std),
            'confidence': self._calculate_confidence(prob_mean, prob_std),
            'model_used': model_name,
            'success_factors': self._identify_success_factors(features),
            'risk_factors': self._identify_risk_factors(features)
        }

    def _calculate_confidence(self, prob_mean: float, prob_std: float) -> str:
        """Calculate confidence level based on probability std"""
        if prob_std < 0.05:
            return 'HIGH'
        elif prob_std < 0.15:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _identify_success_factors(self, features: Dict) -> List[str]:
        """Identify factors that increase probability of success"""
        factors = []

        if features['business_value'] >= 70:
            factors.append("Alto valor de negócio (≥70)")

        if features['risk_level_numeric'] <= 3:
            factors.append("Risco controlado (baixo ou médio)")

        if features['capacity_utilization'] >= 0.8 and features['capacity_utilization'] <= 1.2:
            factors.append("Boa utilização de capacidade (80-120%)")

        if features['budget_per_person'] >= 100000 and features['budget_per_person'] <= 500000:
            factors.append("Orçamento adequado por pessoa")

        if features['duration_weeks'] <= 20:
            factors.append("Duração razoável (≤20 semanas)")

        return factors

    def _identify_risk_factors(self, features: Dict) -> List[str]:
        """Identify factors that decrease probability of success"""
        factors = []

        if features['business_value'] < 40:
            factors.append("Baixo valor de negócio (<40)")

        if features['risk_level_numeric'] >= 5:
            factors.append("Alto risco (high ou critical)")

        if features['capacity_utilization'] < 0.5:
            factors.append("Equipe subutilizada (<50%)")

        if features['capacity_utilization'] > 1.5:
            factors.append("Equipe sobrecarregada (>150%)")

        if features['duration_weeks'] > 30:
            factors.append("Projeto muito longo (>30 semanas)")

        if features['complexity_score'] > 100:
            factors.append("Alta complexidade")

        return factors

    def get_feature_importance(self, model_name: str = 'RandomForest') -> pd.DataFrame:
        """Get feature importance from trained model"""
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

    def get_critical_success_factors(self, top_n: int = 5) -> List[Dict]:
        """
        Get the most critical factors for success.

        Args:
            top_n: Number of top factors to return

        Returns:
            List of critical factors with importance
        """
        if not self.trained:
            raise ValueError("Models not trained.")

        importance_df = self.get_feature_importance()

        if importance_df is None:
            return []

        top_factors = importance_df.head(top_n)

        factors = []
        for _, row in top_factors.iterrows():
            factors.append({
                'factor': row['feature'],
                'importance': float(row['importance']),
                'importance_pct': float(row['importance'] * 100),
                'recommendation': self._get_factor_recommendation(row['feature'])
            })

        return factors

    def _get_factor_recommendation(self, feature: str) -> str:
        """Get recommendation for a critical factor"""
        recommendations = {
            'business_value': 'Priorize projetos com alto valor de negócio (>70)',
            'risk_level_numeric': 'Mantenha risco em níveis controlados (low ou medium)',
            'budget_millions': 'Garanta orçamento adequado baseado em projetos similares bem-sucedidos',
            'team_size': 'Dimensione equipe adequadamente - nem muito grande, nem muito pequena',
            'duration_weeks': 'Prefira projetos mais curtos (<20 semanas) ou divida em fases',
            'capacity_utilization': 'Mantenha utilização de capacidade entre 80-120%',
            'complexity_score': 'Reduza complexidade quando possível - simplifique escopo',
            'forecast_accuracy': 'Melhore precisão de forecasts para melhor planejamento'
        }

        for key, rec in recommendations.items():
            if key in feature:
                return rec

        return 'Monitore este fator de perto durante execução do projeto'
```

#### Arquivo: `app.py` (adicionar rotas)

```python
from project_success_classifier import ProjectSuccessClassifier

@app.route('/api/success/predict', methods=['POST'])
def predict_project_success():
    """Predict probability of project success"""
    try:
        data = request.json

        # Required fields
        required = ['duration_weeks', 'team_size', 'budget', 'business_value']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get or train classifier
        classifier = get_success_classifier()  # Implement this helper

        if not classifier or not classifier.trained:
            return jsonify({'error': 'Success model not trained yet'}), 503

        # Predict
        result = classifier.predict_success(data)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/success/train', methods=['POST'])
def train_success_model():
    """Train success classification model with historical data"""
    try:
        # Get completed projects
        projects = Project.query.filter_by(status='completed').all()

        if len(projects) < 10:
            return jsonify({'error': 'Need at least 10 completed projects for training'}), 400

        # Get forecasts and actuals
        forecasts_map = {}
        actuals_map = {}

        for project in projects:
            forecasts_map[project.id] = project.forecasts
            actuals_map[project.id] = []
            for forecast in project.forecasts:
                actuals_map[project.id].extend(forecast.actuals)

        # Train
        classifier = ProjectSuccessClassifier()
        classifier.train_models(projects, forecasts_map, actuals_map)

        # Save globally
        global success_classifier
        success_classifier = classifier

        return jsonify({
            'message': 'Success model trained successfully',
            'training_samples': len(projects),
            'models': list(classifier.models.keys()),
            'performance': {
                name: {
                    'accuracy': float(data['accuracy']),
                    'roc_auc': float(data['roc_auc'])
                }
                for name, data in classifier.models.items()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/success/critical_factors', methods=['GET'])
def get_critical_success_factors():
    """Get critical factors for project success"""
    try:
        classifier = get_success_classifier()

        if not classifier or not classifier.trained:
            return jsonify({'error': 'Success model not trained yet'}), 503

        factors = classifier.get_critical_success_factors(top_n=10)

        return jsonify({
            'factors': factors
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Frontend - Success Prediction Interface

#### Arquivo: `templates/success_predictor.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Preditor de Sucesso do Projeto</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>🎯 Preditor de Sucesso do Projeto</h1>
        <p class="subtitle">Use Machine Learning para prever a probabilidade de sucesso</p>

        <div class="card">
            <h2>Características do Projeto</h2>

            <form id="successForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>Duração Esperada (semanas):</label>
                        <input type="number" id="duration" min="1" required>
                    </div>

                    <div class="form-group">
                        <label>Tamanho da Equipe:</label>
                        <input type="number" id="teamSize" min="1" required>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Orçamento (R$):</label>
                        <input type="number" id="budget" step="10000" min="0" required>
                    </div>

                    <div class="form-group">
                        <label>Valor de Negócio (0-100):</label>
                        <input type="number" id="businessValue" min="0" max="100" required>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Nível de Risco:</label>
                        <select id="riskLevel">
                            <option value="low">Baixo</option>
                            <option value="medium" selected>Médio</option>
                            <option value="high">Alto</option>
                            <option value="critical">Crítico</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Prioridade:</label>
                        <select id="priority">
                            <option value="low">Baixa</option>
                            <option value="medium" selected>Média</option>
                            <option value="high">Alta</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn-primary">Prever Sucesso</button>
            </form>
        </div>

        <div id="results" style="display: none;">
            <div class="card">
                <h2>Resultado da Predição</h2>

                <div class="prediction-result">
                    <div class="probability-gauge">
                        <canvas id="gaugeChart"></canvas>
                    </div>

                    <div class="prediction-details">
                        <h3 id="predictionLabel">-</h3>
                        <p id="predictionConfidence">-</p>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Probabilidade de Sucesso</h3>
                        <p class="metric-value" id="successProb">-</p>
                    </div>

                    <div class="metric-card">
                        <h3>Probabilidade de Falha</h3>
                        <p class="metric-value" id="failureProb">-</p>
                    </div>

                    <div class="metric-card">
                        <h3>Confiança do Modelo</h3>
                        <p class="metric-value" id="modelConfidence">-</p>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>✅ Fatores de Sucesso</h2>
                <ul id="successFactors"></ul>
            </div>

            <div class="card">
                <h2>⚠️ Fatores de Risco</h2>
                <ul id="riskFactors"></ul>
            </div>
        </div>

        <div class="card">
            <h2>🔑 Fatores Críticos de Sucesso</h2>
            <p>Baseado em dados históricos, estes são os fatores mais importantes</p>
            <button onclick="loadCriticalFactors()" class="btn-secondary">
                Carregar Fatores Críticos
            </button>

            <div id="criticalFactors" style="display: none; margin-top: 20px;">
                <canvas id="criticalChart"></canvas>
                <div id="factorRecommendations"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/success_predictor.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/success_predictor.js` (novo)

```javascript
document.getElementById('successForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        duration_weeks: parseInt(document.getElementById('duration').value),
        team_size: parseInt(document.getElementById('teamSize').value),
        budget: parseFloat(document.getElementById('budget').value),
        business_value: parseFloat(document.getElementById('businessValue').value),
        risk_level: document.getElementById('riskLevel').value,
        priority: document.getElementById('priority').value
    };

    try {
        const response = await fetch('/api/success/predict', {
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

        displayPrediction(result);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao prever sucesso: ' + error.message);
    }
});

function displayPrediction(result) {
    document.getElementById('results').style.display = 'block';

    // Update probabilities
    document.getElementById('successProb').textContent =
        `${(result.success_probability * 100).toFixed(1)}%`;
    document.getElementById('failureProb').textContent =
        `${(result.failure_probability * 100).toFixed(1)}%`;
    document.getElementById('modelConfidence').textContent = result.confidence;

    // Update prediction label
    const label = result.success_predicted === 1 ? '✅ Sucesso Previsto' : '❌ Falha Prevista';
    const labelClass = result.success_predicted === 1 ? 'success' : 'failure';
    document.getElementById('predictionLabel').textContent = label;
    document.getElementById('predictionLabel').className = labelClass;

    // Update confidence
    const confText = `Confiança: ${result.confidence} (±${(result.probability_std * 100).toFixed(1)}%)`;
    document.getElementById('predictionConfidence').textContent = confText;

    // Create gauge chart
    createGaugeChart(result.success_probability);

    // Display factors
    displayFactors(result.success_factors, 'successFactors', 'success');
    displayFactors(result.risk_factors, 'riskFactors', 'risk');

    // Scroll to results
    document.getElementById('results').scrollIntoView({behavior: 'smooth'});
}

function createGaugeChart(probability) {
    const ctx = document.getElementById('gaugeChart').getContext('2d');

    // Simplified gauge using doughnut chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [probability * 100, (1 - probability) * 100],
                backgroundColor: ['#4CAF50', '#f0f0f0'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            circumference: 180,
            rotation: 270,
            cutout: '70%',
            plugins: {
                legend: {display: false},
                tooltip: {enabled: false}
            }
        }
    });
}

function displayFactors(factors, elementId, type) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';

    if (!factors || factors.length === 0) {
        container.innerHTML = '<li>Nenhum fator identificado</li>';
        return;
    }

    factors.forEach(factor => {
        const li = document.createElement('li');
        li.textContent = factor;
        li.className = type === 'success' ? 'success-factor' : 'risk-factor';
        container.appendChild(li);
    });
}

async function loadCriticalFactors() {
    try {
        const response = await fetch('/api/success/critical_factors');

        if (!response.ok) {
            const error = await response.json();
            alert('Erro: ' + error.error);
            return;
        }

        const data = await response.json();

        displayCriticalFactors(data.factors);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar fatores: ' + error.message);
    }
}

function displayCriticalFactors(factors) {
    document.getElementById('criticalFactors').style.display = 'block';

    // Create chart
    const ctx = document.getElementById('criticalChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: factors.map(f => f.factor),
            datasets: [{
                label: 'Importância (%)',
                data: factors.map(f => f.importance_pct),
                backgroundColor: 'rgba(76, 175, 80, 0.5)',
                borderColor: 'rgba(76, 175, 80, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Fatores Críticos de Sucesso'
                }
            }
        }
    });

    // Display recommendations
    const recsContainer = document.getElementById('factorRecommendations');
    recsContainer.innerHTML = '<h3>💡 Recomendações:</h3>';

    factors.forEach((factor, i) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.innerHTML = `
            <h4>${i + 1}. ${factor.factor} (${factor.importance_pct.toFixed(1)}%)</h4>
            <p>${factor.recommendation}</p>
        `;
        recsContainer.appendChild(card);
    });
}
```

## 📅 Cronograma de Implementação

**Total: 1-2 semanas**

- **Semana 1:**
  - Dias 1-3: Backend - ProjectSuccessClassifier
  - Dias 4-5: API endpoints

- **Semana 2:**
  - Dias 1-3: Frontend - Prediction UI
  - Dias 4-5: Critical factors e testes

## ✅ Critérios de Aceitação

- [ ] Random Forest Classifier treinado com accuracy > 80%
- [ ] ROC-AUC > 0.85
- [ ] Predição de probabilidade funcional
- [ ] Fatores de sucesso/risco identificados
- [ ] Fatores críticos extraídos
- [ ] Interface intuitiva e visual
- [ ] Recomendações acionáveis

**Esforço Total:** ~1-2 semanas (1 desenvolvedor)

---

# Feature #20: Persistência e Export de Modelos

## 🎯 Objetivo
Implementar sistema de persistência de modelos treinados (pickle/joblib) e API REST para predições em batch.

## 📊 Status Atual
🟡 **Implementado Parcial** - Modelos salvos em memória, sem persistência em disco

## 🔧 Componentes a Implementar

### 1. Backend - Sistema de Persistência

#### Arquivo: `model_manager.py` (novo)

```python
"""
Model Management Module
Handles saving, loading, and versioning of trained ML models
"""

import os
import json
import pickle
import joblib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib

from ml_forecaster import MLForecaster
from cod_forecaster import CoDForecaster
from project_success_classifier import ProjectSuccessClassifier


class ModelManager:
    """
    Manage ML models: save, load, version, and document.
    """

    def __init__(self, models_dir: str = 'models'):
        """
        Initialize Model Manager.

        Args:
            models_dir: Directory to store models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.models_dir / 'models_metadata.json'
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load models metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save models metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _generate_model_id(self, model_type: str) -> str:
        """Generate unique model ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{model_type}_{timestamp}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def save_model(self,
                  model: Any,
                  model_type: str,
                  metadata: Optional[Dict] = None,
                  version: Optional[str] = None) -> str:
        """
        Save a trained model to disk.

        Args:
            model: Trained model object
            model_type: Type of model ('throughput', 'cod', 'success')
            metadata: Additional metadata (performance metrics, etc.)
            version: Optional version string

        Returns:
            Model ID
        """
        # Generate model ID
        model_id = self._generate_model_id(model_type)

        # Create model directory
        model_dir = self.models_dir / model_id
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model using joblib (more efficient than pickle)
        model_file = model_dir / 'model.joblib'
        joblib.dump(model, model_file)

        # Calculate checksum
        checksum = self._calculate_checksum(model_file)

        # Prepare metadata
        model_metadata = {
            'model_id': model_id,
            'model_type': model_type,
            'version': version or 'v1.0',
            'saved_at': datetime.now().isoformat(),
            'file_path': str(model_file),
            'file_size_bytes': model_file.stat().st_size,
            'checksum': checksum,
            'format': 'joblib'
        }

        # Add custom metadata
        if metadata:
            model_metadata.update(metadata)

        # Extract model-specific info
        if hasattr(model, 'feature_names'):
            model_metadata['features'] = model.feature_names
        if hasattr(model, 'trained') and model.trained:
            model_metadata['trained'] = True
        if hasattr(model, 'models'):
            model_metadata['sub_models'] = list(model.models.keys())

        # Save model-specific metadata
        metadata_file = model_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(model_metadata, f, indent=2)

        # Update global metadata
        self.metadata[model_id] = model_metadata
        self._save_metadata()

        print(f"Model saved: {model_id}")
        print(f"Location: {model_file}")
        print(f"Size: {model_file.stat().st_size / 1024:.2f} KB")

        return model_id

    def load_model(self, model_id: str) -> Any:
        """
        Load a model from disk.

        Args:
            model_id: ID of model to load

        Returns:
            Loaded model object
        """
        if model_id not in self.metadata:
            raise ValueError(f"Model {model_id} not found in metadata")

        model_metadata = self.metadata[model_id]
        model_file = Path(model_metadata['file_path'])

        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        # Verify checksum
        current_checksum = self._calculate_checksum(model_file)
        if current_checksum != model_metadata['checksum']:
            raise ValueError(f"Model file checksum mismatch. File may be corrupted.")

        # Load model
        model = joblib.load(model_file)

        print(f"Model loaded: {model_id}")

        return model

    def list_models(self, model_type: Optional[str] = None) -> List[Dict]:
        """
        List all saved models.

        Args:
            model_type: Optional filter by model type

        Returns:
            List of model metadata
        """
        models = []

        for model_id, metadata in self.metadata.items():
            if model_type is None or metadata['model_type'] == model_type:
                models.append(metadata)

        # Sort by saved_at (newest first)
        models.sort(key=lambda x: x['saved_at'], reverse=True)

        return models

    def get_latest_model(self, model_type: str) -> Optional[str]:
        """
        Get ID of latest model for a given type.

        Args:
            model_type: Type of model

        Returns:
            Model ID or None if not found
        """
        models = self.list_models(model_type=model_type)

        if len(models) == 0:
            return None

        return models[0]['model_id']

    def delete_model(self, model_id: str):
        """
        Delete a model from disk.

        Args:
            model_id: ID of model to delete
        """
        if model_id not in self.metadata:
            raise ValueError(f"Model {model_id} not found")

        # Get model directory
        model_dir = self.models_dir / model_id

        # Delete directory and contents
        if model_dir.exists():
            import shutil
            shutil.rmtree(model_dir)

        # Remove from metadata
        del self.metadata[model_id]
        self._save_metadata()

        print(f"Model deleted: {model_id}")

    def export_model_docs(self, model_id: str) -> str:
        """
        Generate documentation for a model.

        Args:
            model_id: ID of model

        Returns:
            Markdown documentation string
        """
        if model_id not in self.metadata:
            raise ValueError(f"Model {model_id} not found")

        metadata = self.metadata[model_id]

        docs = f"# Model Documentation: {model_id}\n\n"
        docs += f"**Type:** {metadata['model_type']}\n\n"
        docs += f"**Version:** {metadata['version']}\n\n"
        docs += f"**Created:** {metadata['saved_at']}\n\n"
        docs += f"**Status:** {metadata.get('trained', 'Unknown')}\n\n"

        if 'features' in metadata:
            docs += "## Features Used\n\n"
            for feature in metadata['features']:
                docs += f"- {feature}\n"
            docs += "\n"

        if 'sub_models' in metadata:
            docs += "## Sub-Models\n\n"
            for sub_model in metadata['sub_models']:
                docs += f"- {sub_model}\n"
            docs += "\n"

        if 'performance' in metadata:
            docs += "## Performance Metrics\n\n"
            perf = metadata['performance']
            for metric, value in perf.items():
                docs += f"- **{metric}:** {value}\n"
            docs += "\n"

        docs += "## Technical Details\n\n"
        docs += f"- **File Size:** {metadata['file_size_bytes'] / 1024:.2f} KB\n"
        docs += f"- **Format:** {metadata['format']}\n"
        docs += f"- **Checksum (MD5):** `{metadata['checksum']}`\n"

        return docs

    def cleanup_old_models(self, model_type: str, keep_latest: int = 5):
        """
        Delete old models, keeping only the latest N.

        Args:
            model_type: Type of model
            keep_latest: Number of latest models to keep
        """
        models = self.list_models(model_type=model_type)

        if len(models) <= keep_latest:
            return

        # Delete older models
        for model in models[keep_latest:]:
            print(f"Cleaning up old model: {model['model_id']}")
            self.delete_model(model['model_id'])

        print(f"Cleanup complete. Kept {keep_latest} latest models.")
```

### 2. API REST para Predições em Batch

#### Arquivo: `app.py` (adicionar rotas)

```python
from model_manager import ModelManager

model_manager = ModelManager()

@app.route('/api/models/list', methods=['GET'])
def list_saved_models():
    """List all saved models"""
    try:
        model_type = request.args.get('type')
        models = model_manager.list_models(model_type=model_type)

        return jsonify({
            'models': models,
            'count': len(models)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/save', methods=['POST'])
def save_current_models():
    """Save currently trained models to disk"""
    try:
        data = request.json
        model_type = data.get('model_type')

        saved_models = []

        # Save throughput forecaster
        if model_type in ['throughput', 'all']:
            if ml_forecaster and ml_forecaster.trained:
                metadata = {
                    'training_samples': len(ml_forecaster.tp_samples) if hasattr(ml_forecaster, 'tp_samples') else 0,
                    'performance': ml_forecaster.get_results_summary()
                }
                model_id = model_manager.save_model(ml_forecaster, 'throughput', metadata)
                saved_models.append(model_id)

        # Save CoD forecaster
        if model_type in ['cod', 'all']:
            if cod_forecaster and cod_forecaster.trained:
                metadata = {
                    'performance': {
                        name: {
                            'mae': float(data['mae']),
                            'r2': float(data['r2'])
                        }
                        for name, data in cod_forecaster.models.items()
                    }
                }
                model_id = model_manager.save_model(cod_forecaster, 'cod', metadata)
                saved_models.append(model_id)

        # Save success classifier
        if model_type in ['success', 'all']:
            if success_classifier and success_classifier.trained:
                metadata = {
                    'performance': {
                        name: {
                            'accuracy': float(data['accuracy']),
                            'roc_auc': float(data['roc_auc'])
                        }
                        for name, data in success_classifier.models.items()
                    }
                }
                model_id = model_manager.save_model(success_classifier, 'success', metadata)
                saved_models.append(model_id)

        if len(saved_models) == 0:
            return jsonify({'error': 'No trained models to save'}), 400

        return jsonify({
            'message': 'Models saved successfully',
            'saved_models': saved_models
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/load/<model_id>', methods=['POST'])
def load_saved_model(model_id):
    """Load a saved model"""
    try:
        model = model_manager.load_model(model_id)

        # Determine type and set as active model
        metadata = model_manager.metadata[model_id]
        model_type = metadata['model_type']

        if model_type == 'throughput':
            global ml_forecaster
            ml_forecaster = model
        elif model_type == 'cod':
            global cod_forecaster
            cod_forecaster = model
        elif model_type == 'success':
            global success_classifier
            success_classifier = model

        return jsonify({
            'message': f'Model {model_id} loaded successfully',
            'model_type': model_type
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/export_docs/<model_id>', methods=['GET'])
def export_model_documentation(model_id):
    """Export model documentation"""
    try:
        docs = model_manager.export_model_docs(model_id)

        return Response(docs, mimetype='text/markdown',
                       headers={'Content-Disposition': f'attachment; filename={model_id}_docs.md'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch/predict', methods=['POST'])
def batch_predictions():
    """
    Batch predictions endpoint.

    Accepts multiple projects and returns predictions for all.
    """
    try:
        data = request.json
        projects = data.get('projects', [])
        prediction_type = data.get('type', 'success')  # 'success', 'cod', 'throughput'

        if len(projects) == 0:
            return jsonify({'error': 'No projects provided'}), 400

        results = []

        if prediction_type == 'success':
            if not success_classifier or not success_classifier.trained:
                return jsonify({'error': 'Success model not available'}), 503

            for project in projects:
                result = success_classifier.predict_success(project)
                result['project_id'] = project.get('id')
                result['project_name'] = project.get('name')
                results.append(result)

        elif prediction_type == 'cod':
            if not cod_forecaster or not cod_forecaster.trained:
                return jsonify({'error': 'CoD model not available'}), 503

            for project in projects:
                result = cod_forecaster.predict_cod(project)
                result['project_id'] = project.get('id')
                result['project_name'] = project.get('name')
                results.append(result)

        return jsonify({
            'predictions': results,
            'count': len(results),
            'prediction_type': prediction_type
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/cleanup', methods='POST'])
def cleanup_old_models():
    """Cleanup old models"""
    try:
        data = request.json
        model_type = data.get('model_type')
        keep_latest = data.get('keep_latest', 5)

        model_manager.cleanup_old_models(model_type, keep_latest)

        return jsonify({
            'message': f'Cleanup complete for {model_type} models'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 3. Frontend - Model Management UI

#### Arquivo: `templates/model_management.html` (novo)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Gerenciamento de Modelos</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>🗄️ Gerenciamento de Modelos</h1>
        <p class="subtitle">Salve, carregue e gerencie modelos de Machine Learning</p>

        <div class="card">
            <h2>Salvar Modelos Atuais</h2>

            <div class="form-group">
                <label>Tipo de Modelo:</label>
                <select id="saveModelType">
                    <option value="all">Todos os Modelos</option>
                    <option value="throughput">Throughput</option>
                    <option value="cod">Custo de Atraso</option>
                    <option value="success">Sucesso do Projeto</option>
                </select>
            </div>

            <button onclick="saveModels()" class="btn-primary">
                💾 Salvar Modelos
            </button>
        </div>

        <div class="card">
            <h2>Modelos Salvos</h2>

            <div class="form-group">
                <label>Filtrar por Tipo:</label>
                <select id="filterType" onchange="loadModels()">
                    <option value="">Todos</option>
                    <option value="throughput">Throughput</option>
                    <option value="cod">Custo de Atraso</option>
                    <option value="success">Sucesso</option>
                </select>
            </div>

            <button onclick="loadModels()" class="btn-secondary">
                🔄 Atualizar Lista
            </button>

            <table id="modelsTable" class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Versão</th>
                        <th>Data</th>
                        <th>Tamanho</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="modelsTableBody">
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Limpeza de Modelos Antigos</h2>
            <p>Remova modelos antigos, mantendo apenas os mais recentes</p>

            <div class="form-row">
                <div class="form-group">
                    <label>Tipo:</label>
                    <select id="cleanupType">
                        <option value="throughput">Throughput</option>
                        <option value="cod">CoD</option>
                        <option value="success">Sucesso</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Manter Últimos:</label>
                    <input type="number" id="keepLatest" value="5" min="1">
                </div>
            </div>

            <button onclick="cleanupModels()" class="btn-warning">
                🧹 Limpar Modelos Antigos
            </button>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/model_management.js') }}"></script>
</body>
</html>
```

#### Arquivo: `static/js/model_management.js` (novo)

```javascript
async function saveModels() {
    const modelType = document.getElementById('saveModelType').value;

    try {
        const response = await fetch('/api/models/save', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model_type: modelType})
        });

        const result = await response.json();

        if (!response.ok) {
            alert('Erro: ' + result.error);
            return;
        }

        alert(`${result.saved_models.length} modelo(s) salvo(s) com sucesso!`);
        loadModels();

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao salvar modelos: ' + error.message);
    }
}

async function loadModels() {
    const filterType = document.getElementById('filterType').value;

    try {
        const url = '/api/models/list' + (filterType ? `?type=${filterType}` : '');
        const response = await fetch(url);

        const result = await response.json();

        if (!response.ok) {
            alert('Erro: ' + result.error);
            return;
        }

        displayModels(result.models);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar modelos: ' + error.message);
    }
}

function displayModels(models) {
    const tbody = document.getElementById('modelsTableBody');
    tbody.innerHTML = '';

    if (models.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">Nenhum modelo encontrado</td></tr>';
        return;
    }

    models.forEach(model => {
        const row = document.createElement('tr');

        const date = new Date(model.saved_at).toLocaleString('pt-BR');
        const size = (model.file_size_bytes / 1024).toFixed(2);

        row.innerHTML = `
            <td><code>${model.model_id}</code></td>
            <td><span class="badge">${model.model_type}</span></td>
            <td>${model.version}</td>
            <td>${date}</td>
            <td>${size} KB</td>
            <td>
                <button onclick="loadModel('${model.model_id}')" class="btn-sm">Carregar</button>
                <button onclick="exportDocs('${model.model_id}')" class="btn-sm">Docs</button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

async function loadModel(modelId) {
    if (!confirm(`Carregar modelo ${modelId}? Isso substituirá o modelo atual em memória.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/models/load/${modelId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (!response.ok) {
            alert('Erro: ' + result.error);
            return;
        }

        alert(result.message);

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar modelo: ' + error.message);
    }
}

async function exportDocs(modelId) {
    try {
        window.open(`/api/models/export_docs/${modelId}`, '_blank');

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao exportar documentação: ' + error.message);
    }
}

async function cleanupModels() {
    const modelType = document.getElementById('cleanupType').value;
    const keepLatest = parseInt(document.getElementById('keepLatest').value);

    if (!confirm(`Remover modelos antigos do tipo "${modelType}", mantendo apenas os ${keepLatest} mais recentes?`)) {
        return;
    }

    try {
        const response = await fetch('/api/models/cleanup', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                model_type: modelType,
                keep_latest: keepLatest
            })
        });

        const result = await response.json();

        if (!response.ok) {
            alert('Erro: ' + result.error);
            return;
        }

        alert(result.message);
        loadModels();

    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao limpar modelos: ' + error.message);
    }
}

// Load models on page load
document.addEventListener('DOMContentLoaded', loadModels);
```

## 📅 Cronograma de Implementação

**Total: 1 semana**

- **Dias 1-2:** Backend - ModelManager class
- **Dia 3:** API REST para batch predictions
- **Dias 4-5:** Frontend - Management UI e testes

## ✅ Critérios de Aceitação

- [ ] Modelos salvos com joblib
- [ ] Metadata tracking completo
- [ ] Versionamento funcional
- [ ] Checksum verification
- [ ] Load/save funcionando
- [ ] API REST para batch predictions
- [ ] UI de gerenciamento completa
- [ ] Documentação automática de modelos
- [ ] Cleanup de modelos antigos

**Esforço Total:** ~1 semana (1 desenvolvedor)

---

# 🎉 Plano de Implementação Completo - Resumo Final

## 📊 Todas as Features Documentadas

| # | Feature | Status Atual | Esforço | Prioridade | Arquivo |
|---|---------|--------------|---------|------------|---------|
| #4+#5 | Sistema de CoD | ❌ Não Implementado | 2-3 semanas | 🔥 Alta | IMPLEMENTATION_PLAN.md |
| #6 | Feature Importance | 🟡 Parcial | 3-5 dias | 🔥 Alta | IMPLEMENTATION_PLAN.md |
| #12 | Visualizações Avançadas | 🟡 Parcial | 1 semana | 🟡 Média | IMPLEMENTATION_PLAN.md |
| #13 | Upload de Dados | 🟡 Parcial | 1 semana | 🟡 Média | IMPLEMENTATION_PLAN.md |
| #16 | Clustering | 🟡 Parcial | 2 semanas | 🟢 Baixa | IMPLEMENTATION_PLAN_ADICIONAL.md |
| #18 | Otimização Portfólio | 🟡 Parcial | 2 semanas | 🔥 Alta | IMPLEMENTATION_PLAN_ADICIONAL.md |
| #19 | Modelo de Sucesso | ❌ Não Implementado | 1-2 semanas | 🟡 Média | IMPLEMENTATION_PLAN_ADICIONAL.md |
| #20 | Persistência Modelos | 🟡 Parcial | 1 semana | 🟢 Baixa | IMPLEMENTATION_PLAN_ADICIONAL.md |

## 🚀 Roadmap Consolidado Final

### **Sprint 1 (2-3 semanas): Funcionalidades Críticas**
- ✅ Sistema de CoD completo (#4 + #5)
- ✅ Feature Importance UI (#6)
- **Resultado:** Funcionalidade crítica + interpretabilidade

### **Sprint 2 (2 semanas): Dados e Interface**
- ✅ Upload de dados históricos (#13)
- ✅ Visualizações avançadas (#12)
- **Resultado:** Personalização + análise exploratória

### **Sprint 3 (2 semanas): Otimização**
- ✅ Solver de otimização PuLP (#18)
- ✅ Análise de sensibilidade
- **Resultado:** Diferencial competitivo único

### **Sprint 4 (2 semanas): ML Avançado**
- ✅ Modelo de sucesso (#19)
- ✅ Clustering (#16)
- **Resultado:** Insights preditivos avançados

### **Sprint 5 (1 semana): Infraestrutura**
- ✅ Persistência de modelos (#20)
- ✅ API REST para batch
- ✅ Documentação completa
- **Resultado:** Sistema robusto e escalável

## 📈 Estatísticas do Plano

- **Total de Linhas de Código Documentadas:** ~8,000+ linhas
- **Arquivos Novos a Criar:** 16 arquivos Python + 16 arquivos HTML/JS
- **Endpoints de API:** 25+ novos endpoints
- **Tempo Total Estimado:** 9-11 semanas
- **Funcionalidades Completas:** 8 features principais
- **Sub-funcionalidades:** 20+ componentes

## 🎯 Impacto Esperado

Após implementação completa, o flow-forecaster terá:

1. **Sistema de CoD** - Funcionalidade crítica ausente
2. **Otimização Matemática** - Diferencial competitivo único
3. **Predição de Sucesso** - Insights preditivos valiosos
4. **Clustering Inteligente** - Padrões automáticos
5. **Feature Importance** - Interpretabilidade total
6. **Visualizações Ricas** - Análise exploratória completa
7. **Upload de Dados** - Personalização do modelo
8. **Persistência Robusta** - Escalabilidade e versionamento

**De 75% → 95%+ de completude do roadmap ML!**

---

**Plano de Implementação Completo**
**Criado em:** 2025-11-05
**Total de Páginas:** 150+ páginas de documentação técnica
**Status:** ✅ COMPLETO
