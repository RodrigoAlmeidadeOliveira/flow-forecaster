/**
 * Portfolio Executive Dashboard JavaScript
 * High-level executive view with key KPIs
 */

let currentPortfolioId = null;
let compositionChart = null;
let valueRiskChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolios();
});

/**
 * Load all portfolios for selector
 */
async function loadPortfolios() {
    try {
        const response = await fetch('/api/portfolios');
        if (!response.ok) throw new Error('Failed to load portfolios');

        const portfolios = await response.json();

        const selector = document.getElementById('portfolioSelector');
        selector.innerHTML = '<option value="">Selecione um portfolio...</option>';

        portfolios.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = `${p.name} (${p.projects_count} projetos)`;
            selector.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading portfolios:', error);
    }
}

/**
 * Load executive dashboard for selected portfolio
 */
async function loadExecutiveDashboard() {
    const selector = document.getElementById('portfolioSelector');
    const portfolioId = selector.value;

    if (!portfolioId) {
        document.getElementById('dashboardContent').style.display = 'none';
        document.getElementById('emptyState').style.display = 'block';
        return;
    }

    currentPortfolioId = portfolioId;

    try {
        const response = await fetch(`/api/portfolios/${portfolioId}/dashboard`);
        if (!response.ok) throw new Error('Failed to load dashboard');

        const data = await response.json();
        renderExecutiveDashboard(data);

        document.getElementById('dashboardContent').style.display = 'block';
        document.getElementById('emptyState').style.display = 'none';

    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Erro ao carregar executive dashboard: ' + error.message);
    }
}

/**
 * Render executive dashboard
 */
function renderExecutiveDashboard(data) {
    // Health Score KPI
    const healthScore = data.health.overall_score;
    document.getElementById('healthScore').textContent = healthScore.toFixed(0);

    const healthKPI = document.getElementById('healthKPI');
    healthKPI.className = 'kpi-card';
    if (healthScore >= 80) {
        healthKPI.classList.add('status-excellent');
        document.getElementById('healthStatus').textContent = 'Excellent';
    } else if (healthScore >= 60) {
        healthKPI.classList.add('status-good');
        document.getElementById('healthStatus').textContent = 'Good';
    } else if (healthScore >= 40) {
        healthKPI.classList.add('status-warning');
        document.getElementById('healthStatus').textContent = 'Needs Attention';
    } else {
        healthKPI.classList.add('status-critical');
        document.getElementById('healthStatus').textContent = 'Critical';
    }

    // Projects KPI
    document.getElementById('totalProjects').textContent = data.summary.total_projects;
    document.getElementById('activeStatus').textContent = `${data.summary.active_projects} active`;

    // Total Value KPI
    const totalValue = data.projects.reduce((sum, p) => sum + (p.business_value || 0), 0);
    document.getElementById('totalValue').textContent = `${totalValue}`;

    // Budget KPI
    const budgetUtil = data.health.budget_utilization || 0;
    document.getElementById('budgetUtilization').textContent = `${budgetUtil.toFixed(0)}%`;

    const budgetUsed = data.health.budget_allocated || 0;
    const budgetTotal = data.health.budget_available || 0;
    document.getElementById('budgetStatus').textContent = `R$ ${formatNumber(budgetUsed)} / R$ ${formatNumber(budgetTotal)}`;

    // Key Metrics
    document.getElementById('onTrackCount').textContent = data.health.on_track_count;
    document.getElementById('atRiskCount').textContent = data.health.at_risk_count;
    document.getElementById('criticalCount').textContent = data.health.critical_count;
    document.getElementById('capacityUsed').textContent = `${data.health.capacity_utilization.toFixed(0)}%`;
    document.getElementById('avgCompletion').textContent = `${data.summary.avg_completion_pct.toFixed(0)}%`;
    document.getElementById('timelineP85').textContent = `${data.timeline.projected_duration_weeks.toFixed(0)}w`;

    // Executive Summary
    renderExecutiveSummary(data);

    // Charts
    renderCompositionChart(data);
    renderValueRiskChart(data);

    // Critical Alerts
    renderCriticalAlerts(data.alerts);
}

/**
 * Render executive summary text
 */
function renderExecutiveSummary(data) {
    const summary = [];

    // Portfolio status
    const healthScore = data.health.overall_score;
    if (healthScore >= 80) {
        summary.push(`O portfólio está em <span class="highlight">excelente condição</span> com health score de ${healthScore.toFixed(0)}.`);
    } else if (healthScore >= 60) {
        summary.push(`O portfólio está em <span class="highlight">boa condição</span> com health score de ${healthScore.toFixed(0)}.`);
    } else {
        summary.push(`O portfólio requer <span class="highlight">atenção imediata</span> com health score de ${healthScore.toFixed(0)}.`);
    }

    // Projects status
    summary.push(`Dos <span class="highlight">${data.summary.total_projects} projetos</span> no portfólio, ${data.health.on_track_count} estão no prazo e ${data.health.at_risk_count} apresentam riscos.`);

    // Resource utilization
    const capUtil = data.health.capacity_utilization;
    if (capUtil > 100) {
        summary.push(`<span class="highlight">Atenção:</span> Capacidade sobre-alocada em ${capUtil.toFixed(0)}%.`);
    } else if (capUtil > 90) {
        summary.push(`Capacidade quase no limite com <span class="highlight">${capUtil.toFixed(0)}% de utilização</span>.`);
    } else {
        summary.push(`Capacidade utilizada: ${capUtil.toFixed(0)}%.`);
    }

    // Budget status
    const budgetUtil = data.health.budget_utilization || 0;
    if (budgetUtil > 100) {
        summary.push(`<span class="highlight">Atenção:</span> Orçamento excedido em ${(budgetUtil - 100).toFixed(0)}%.`);
    } else if (budgetUtil > 90) {
        summary.push(`Orçamento quase esgotado com <span class="highlight">${budgetUtil.toFixed(0)}% de utilização</span>.`);
    }

    // Timeline
    summary.push(`Previsão de conclusão (P85): <span class="highlight">${data.timeline.projected_duration_weeks.toFixed(1)} semanas</span>.`);

    // Critical alerts
    const criticalAlerts = data.alerts.filter(a => a.severity === 'critical');
    if (criticalAlerts.length > 0) {
        summary.push(`<span class="highlight">Existem ${criticalAlerts.length} alertas críticos</span> que requerem ação imediata.`);
    }

    document.getElementById('executiveSummary').innerHTML = summary.join(' ');
}

/**
 * Render portfolio composition chart
 */
function renderCompositionChart(data) {
    const ctx = document.getElementById('compositionChart');

    if (compositionChart) {
        compositionChart.destroy();
    }

    // Group projects by status
    const statusCounts = {};
    data.projects.forEach(p => {
        const status = p.on_track ? 'On Track' : 'At Risk';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
    });

    compositionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCounts),
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: [
                    'rgba(17, 153, 142, 0.8)',
                    'rgba(250, 112, 154, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = (context.parsed / total * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + pct + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render value vs risk chart
 */
function renderValueRiskChart(data) {
    const ctx = document.getElementById('valueRiskChart');

    if (valueRiskChart) {
        valueRiskChart.destroy();
    }

    // Prepare data: top 10 projects by value
    const topProjects = data.projects
        .filter(p => p.business_value > 0)
        .sort((a, b) => b.business_value - a.business_value)
        .slice(0, 10);

    valueRiskChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topProjects.map(p => p.project_name.substring(0, 20)),
            datasets: [
                {
                    label: 'Business Value',
                    data: topProjects.map(p => p.business_value),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Value: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Business Value'
                    }
                }
            }
        }
    });
}

/**
 * Render critical alerts
 */
function renderCriticalAlerts(alerts) {
    const criticalAlerts = alerts.filter(a => a.severity === 'critical');

    if (criticalAlerts.length === 0) {
        document.getElementById('alertsSection').style.display = 'none';
        return;
    }

    document.getElementById('alertsSection').style.display = 'block';

    const html = criticalAlerts.map(alert => `
        <div class="alert alert-danger" role="alert">
            <h5 class="alert-heading">
                <i class="fas fa-exclamation-circle"></i> ${alert.title}
            </h5>
            <p>${alert.message}</p>
            ${alert.project_name ? `<small>Projeto: <strong>${alert.project_name}</strong></small>` : ''}
        </div>
    `).join('');

    document.getElementById('criticalAlerts').innerHTML = html;
}

/**
 * Export portfolio to Excel
 */
function exportToExcel() {
    if (!currentPortfolioId) {
        alert('Por favor, selecione um portfolio primeiro');
        return;
    }

    window.open(`/api/portfolios/${currentPortfolioId}/export/excel`, '_blank');
}

/**
 * Export portfolio to PDF
 */
function exportToPDF() {
    if (!currentPortfolioId) {
        alert('Por favor, selecione um portfolio primeiro');
        return;
    }

    window.open(`/api/portfolios/${currentPortfolioId}/export/pdf`, '_blank');
}

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(num);
}
