/**
 * Portfolio Dashboard Module
 * Manages portfolio-level visualization and analysis
 */

// Initialize portfolio when tab is shown
$(document).ready(function() {
    $('#tab-portfolio-link').on('shown.bs.tab', function() {
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
        <!-- Admin Button (only visible for admins) -->
        <div class="row mb-3">
            <div class="col-12 text-right">
                <button id="admin-update-portfolio-btn" class="btn btn-sm btn-warning" onclick="updatePortfolioValuesAdmin()" style="display: none;">
                    <i class="fas fa-wrench"></i> [ADMIN] Atualizar Valores de Portfólio
                </button>
            </div>
        </div>

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

    // Show admin button if user is admin (check if user_role variable exists)
    if (typeof user_role !== 'undefined' && (user_role === 'admin' || user_role === 'instructor')) {
        $('#admin-update-portfolio-btn').show();
    }
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
                                <h3>${capacity.total_capacity.toFixed(1)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Capacidade Alocada</h6>
                                <h3>${capacity.allocated_capacity.toFixed(1)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Capacidade Disponível</h6>
                                <h3>${capacity.available_capacity.toFixed(1)} FTE</h3>
                            </div>
                            <div class="col-md-3 text-center">
                                <h6>Taxa de Utilização</h6>
                                <h3>${capacity.utilization_rate.toFixed(1)}%</h3>
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
                <td>${hs.overall_score.toFixed(1)}</td>
                <td>${hs.forecast_accuracy_score.toFixed(1)}</td>
                <td>${hs.mape ? hs.mape.toFixed(1) + '%' : '-'}</td>
                <td>${hs.forecast_count}</td>
                <td>${hs.actual_count}</td>
                <td>${hs.alerts.length > 0 ? `<span class="text-danger">${hs.alerts.length} alertas</span>` : '-'}</td>
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
 * Admin function to update portfolio values
 * Distributes projects across the prioritization matrix quadrants
 */
async function updatePortfolioValuesAdmin() {
    if (!confirm('⚠️ Isso atualizará os valores de business_value e risk_level de todos os projetos.\n\nDeseja continuar?')) {
        return;
    }

    const btn = $('#admin-update-portfolio-btn');
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Atualizando...');

    try {
        const response = await fetch('/admin/update-portfolio-values', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert('✅ Valores atualizados com sucesso!\n\n' + data.updates.join('\n'));

            // Reload dashboard to show updated values
            loadPortfolioDashboard();
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error('Error updating portfolio values:', error);
        alert('❌ Erro ao atualizar valores: ' + error.message);
    } finally {
        btn.prop('disabled', false).html('<i class="fas fa-wrench"></i> [ADMIN] Atualizar Valores de Portfólio');
    }
}

// Export to global scope
window.updatePortfolioValuesAdmin = updatePortfolioValuesAdmin;
