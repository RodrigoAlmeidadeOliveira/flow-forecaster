/**
 * Portfolio Dashboard Module
 * Manages portfolio-level visualization and analysis
 */

// Initialize portfolio when Dashboard & Portfolio tab is shown
$(document).ready(function() {
    $('#tab-dashboard-link').on('shown.bs.tab', function() {
        loadPortfolioDashboard();
    });
});

async function loadPortfolioDashboard() {
    try {
        const response = await fetch('/api/portfolio/dashboard');
        const data = await response.json();

        if (!data.has_data) {
            renderEmptyState(data.message);
            return;
        }

        renderPortfolioDashboard(data);
    } catch (error) {
        console.error('Error loading portfolio:', error);
        renderError('Erro ao carregar portfolio: ' + error.message);
    }
}

function renderEmptyState(message) {
    $('#portfolio-content').html(`
        <div class="text-center py-5">
            <i class="fas fa-briefcase fa-4x text-muted mb-3"></i>
            <h3>${message}</h3>
            <p class="text-muted">Crie projetos na seção "Dashboard Executivo" ou use a API</p>
        </div>
    `);
}

function renderError(message) {
    $('#portfolio-content').html(`
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `);
}

function renderPortfolioDashboard(data) {
    const html = `
        <!-- Summary Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card border-primary">
                    <div class="card-body text-center">
                        <h6 class="text-muted">Total de Projetos</h6>
                        <h2 class="text-primary">${data.summary.total_projects}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-success">
                    <div class="card-body text-center">
                        <h6 class="text-muted">Projetos Ativos</h6>
                        <h2 class="text-success">${data.summary.active_projects}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-info">
                    <div class="card-body text-center">
                        <h6 class="text-muted">Health Score Médio</h6>
                        <h2 class="text-info">${data.summary.avg_health_score}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card border-warning">
                    <div class="card-body text-center">
                        <h6 class="text-muted">Valor Total de Negócio</h6>
                        <h2 class="text-warning">${data.summary.total_business_value}</h2>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alerts -->
        ${renderAlerts(data.alerts)}

        <!-- Capacity Analysis -->
        ${renderCapacityAnalysis(data.capacity_analysis)}

        <!-- Projects Health Table -->
        ${renderHealthScoresTable(data.health_scores)}

        <!-- Prioritization Matrix -->
        ${renderPrioritizationMatrix(data.prioritization_matrix)}
    `;

    $('#portfolio-content').html(html);

    // Load WSJF/CoD analysis
    loadWSJFAnalysis(data.projects);
}

function renderAlerts(alerts) {
    if (!alerts || alerts.length === 0) {
        return `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i> <strong>Portfolio saudável!</strong> Nenhum alerta crítico detectado.
            </div>
        `;
    }

    let html = '<div class="row mb-4"><div class="col-12"><h4><i class="fas fa-exclamation-triangle"></i> Alertas do Portfolio</h4></div>';

    alerts.forEach(alert => {
        const severityClass = {
            'critical': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'secondary'
        }[alert.severity] || 'info';

        html += `
            <div class="col-md-6 mb-2">
                <div class="alert alert-${severityClass}">
                    <strong>${alert.type.toUpperCase()}:</strong> ${alert.message}
                    ${alert.action ? `<br><small><i class="fas fa-arrow-right"></i> ${alert.action}</small>` : ''}
                </div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}

function renderCapacityAnalysis(capacity) {
    const statusClass = {
        'optimal': 'success',
        'over_utilized': 'danger',
        'under_utilized': 'warning'
    }[capacity.status] || 'info';

    // Helper function to safely format numbers
    const safeFixed = (value, decimals = 1) => {
        return (value !== null && value !== undefined) ? Number(value).toFixed(decimals) : '0.0';
    };

    return `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-${statusClass} text-white">
                        <h5 class="mb-0"><i class="fas fa-users"></i> Análise de Capacidade</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3 text-center">
                                <h6>Capacidade Total</h6>
                                <h3>${safeFixed(capacity.total_capacity)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Capacidade Alocada</h6>
                                <h3>${safeFixed(capacity.allocated_capacity)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Capacidade Disponível</h6>
                                <h3>${safeFixed(capacity.available_capacity)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Taxa de Utilização</h6>
                                <h3>${safeFixed(capacity.utilization_rate)}%</h3>
                            </div>
                        </div>
                        <hr>
                        <h6>Recomendações:</h6>
                        <ul>
                            ${capacity.recommendations.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderHealthScoresTable(healthScores) {
    if (!healthScores || healthScores.length === 0) {
        return '';
    }

    // Helper function to safely format numbers
    const safeFixed = (value, decimals = 1) => {
        return (value !== null && value !== undefined) ? Number(value).toFixed(decimals) : '0.0';
    };

    let rows = '';
    healthScores.forEach(hs => {
        const statusClass = {
            'excellent': 'success',
            'good': 'info',
            'warning': 'warning',
            'critical': 'danger'
        }[hs.health_status] || 'secondary';

        rows += `
            <tr>
                <td><strong>${hs.project_name}</strong></td>
                <td><span class="badge badge-${statusClass}">${hs.health_status.toUpperCase()}</span></td>
                <td>${safeFixed(hs.overall_score)}</td>
                <td>${safeFixed(hs.forecast_accuracy_score)}</td>
                <td>${hs.mape !== null && hs.mape !== undefined ? safeFixed(hs.mape) + '%' : '-'}</td>
                <td>${hs.forecast_count || 0}</td>
                <td>${hs.actual_count || 0}</td>
                <td>${hs.alerts && hs.alerts.length > 0 ? `<span class="text-danger">${hs.alerts.length} alertas</span>` : '-'}</td>
            </tr>
        `;
    });

    return `
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-heartbeat"></i> Health Score dos Projetos</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Projeto</th>
                                    <th>Status</th>
                                    <th>Overall Score</th>
                                    <th>Accuracy Score</th>
                                    <th>MAPE</th>
                                    <th>Forecasts</th>
                                    <th>Actuals</th>
                                    <th>Alertas</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderPrioritizationMatrix(matrix) {
    return `
        <div class="row mb-4">
            <div class="col-12">
                <h4><i class="fas fa-th"></i> Matriz de Priorização (Valor vs Risco)</h4>
            </div>
            <div class="col-md-6">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0">Alto Valor / Baixo Risco (Quick Wins)</h6>
                    </div>
                    <div class="card-body">
                        ${renderProjectList(matrix.high_value_low_risk, 'success')}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h6 class="mb-0">Alto Valor / Alto Risco (Strategic Bets)</h6>
                    </div>
                    <div class="card-body">
                        ${renderProjectList(matrix.high_value_high_risk, 'warning')}
                    </div>
                </div>
            </div>
            <div class="col-md-6 mt-3">
                <div class="card border-secondary">
                    <div class="card-header bg-secondary text-white">
                        <h6 class="mb-0">Baixo Valor / Baixo Risco (Fill-ins)</h6>
                    </div>
                    <div class="card-body">
                        ${renderProjectList(matrix.low_value_low_risk, 'secondary')}
                    </div>
                </div>
            </div>
            <div class="col-md-6 mt-3">
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white">
                        <h6 class="mb-0">Baixo Valor / Alto Risco (Avoid)</h6>
                    </div>
                    <div class="card-body">
                        ${renderProjectList(matrix.low_value_high_risk, 'danger')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderProjectList(projects, colorClass) {
    if (!projects || projects.length === 0) {
        return '<p class="text-muted">Nenhum projeto nesta categoria</p>';
    }

    let html = '<ul class="list-group">';
    projects.forEach(p => {
        html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${p.name}
                <div>
                    <span class="badge badge-primary">Valor: ${p.business_value}</span>
                    <span class="badge badge-${colorClass}">Risco: ${p.risk_level}</span>
                </div>
            </li>
        `;
    });
    html += '</ul>';
    return html;
}

/**
 * Load and display WSJF/Cost of Delay analysis
 */
function loadWSJFAnalysis(projects) {
    if (!projects || projects.length === 0) {
        $('#wsjf-prioritization').hide();
        return;
    }

    // Calculate WSJF for each project
    const projectsWithWSJF = projects.map(p => {
        // WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size (team_size as proxy)
        const businessValue = p.business_value || 50;
        const timeCriticality = 50; // Default, could be enhanced
        const riskReduction = getRiskScore(p.risk_level);
        const jobSize = p.team_size || 1;

        const wsjf = (businessValue + timeCriticality + riskReduction) / jobSize;

        return {
            ...p,
            wsjf_score: wsjf,
            business_value: businessValue,
            time_criticality: timeCriticality,
            risk_reduction: riskReduction,
            job_size: jobSize
        };
    });

    // Sort by WSJF (highest first)
    projectsWithWSJF.sort((a, b) => b.wsjf_score - a.wsjf_score);

    // Render WSJF ranking table
    renderWSJFRanking(projectsWithWSJF);
    $('#wsjf-prioritization').show();
}

function getRiskScore(riskLevel) {
    // Convert risk level to score (higher risk = lower score for risk reduction)
    const riskMap = {
        'low': 80,
        'medium': 50,
        'high': 20,
        'critical': 10
    };
    return riskMap[riskLevel] || 50;
}

function renderWSJFRanking(projects) {
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead>
            <tr>
                <th>#</th>
                <th>Projeto</th>
                <th>WSJF Score</th>
                <th>Business Value</th>
                <th>Time Criticality</th>
                <th>Risk Reduction</th>
                <th>Job Size</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    `;

    projects.forEach((p, index) => {
        const wsjfClass = index < 3 ? 'table-success' : index < 6 ? 'table-warning' : '';
        html += `
            <tr class="${wsjfClass}">
                <td><strong>${index + 1}</strong></td>
                <td><strong>${p.name}</strong></td>
                <td>
                    <span class="badge" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; font-size: 1em; padding: 0.5em 1em;">
                        ${p.wsjf_score.toFixed(2)}
                    </span>
                </td>
                <td>${p.business_value}</td>
                <td>${p.time_criticality}</td>
                <td>${p.risk_reduction}</td>
                <td>${p.job_size}</td>
                <td><span class="badge badge-info">${p.status}</span></td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';

    html += `
        <div class="alert alert-info mt-3">
            <i class="fas fa-info-circle"></i> <strong>Como interpretar:</strong>
            <ul class="mb-0 mt-2">
                <li><strong class="text-success">Top 3 (verde):</strong> Projetos de maior prioridade - máximo retorno por esforço</li>
                <li><strong class="text-warning">4-6 (amarelo):</strong> Prioridade média - considere recursos disponíveis</li>
                <li>Demais: Avaliar se devem ser adiados ou reavaliados</li>
            </ul>
        </div>
    `;

    $('#wsjf-ranking').html(html);
}


