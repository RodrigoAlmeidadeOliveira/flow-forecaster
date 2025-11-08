/**
 * Portfolio Dashboard Module
 * Manages portfolio-level visualization and analysis
 */

let selectedPortfolioId = 'all';
let selectedProjectFilters = [];
let portfolioRequestToken = 0;
let efficientFrontierRequestToken = 0;
let efficientFrontierChart = null;

function formatPercent(value, decimals = 1) {
    const num = Number(value);
    if (!Number.isFinite(num)) {
        return '-';
    }
    return `${(num * 100).toFixed(decimals)}%`;
}

// Initialize filters and listeners when document is ready
$(document).ready(function() {
    setupPortfolioDashboardFilters();

    $('#tab-dashboard-link').on('shown.bs.tab', function() {
        loadPortfolioDashboard();
    });
});

function setupPortfolioDashboardFilters() {
    loadPortfolioOptions();

    $('#portfolio-dashboard-select').on('change', function() {
        selectedPortfolioId = $(this).val() || 'all';
        selectedProjectFilters = [];
        if (selectedPortfolioId === 'all') {
            resetProjectFilterState(false);
        } else {
            resetProjectFilterState(true);
        }
        loadPortfolioDashboard();
    });

    $('#portfolio-project-select').on('change', function() {
        const values = $(this).val() || [];
        selectedProjectFilters = values
            .map(value => parseInt(value, 10))
            .filter(value => Number.isInteger(value));

        $('#project-filter-clear').prop('disabled', selectedProjectFilters.length === 0);
        loadPortfolioDashboard();
    });

    $('#project-filter-clear').on('click', function() {
        if (!selectedProjectFilters.length) {
            return;
        }
        selectedProjectFilters = [];
        $('#portfolio-project-select').val([]);
        $('#project-filter-clear').prop('disabled', true);
        loadPortfolioDashboard();
    });

    // Initial load so the view is ready even before the tab is opened
    loadPortfolioDashboard();
}

async function loadPortfolioOptions() {
    try {
        const response = await fetch('/api/portfolios');
        if (!response.ok) {
            throw new Error('Falha ao carregar portfólios');
        }

        const portfolios = await response.json();
        const selector = $('#portfolio-dashboard-select');

        if (!selector.length) {
            return;
        }

        selector.empty();
        selector.append('<option value="all">Todos os projetos</option>');

        portfolios.forEach(portfolio => {
            selector.append(
                $('<option></option>')
                    .val(portfolio.id)
                    .text(`${portfolio.name} (${portfolio.projects_count} projetos)`)
            );
        });
    } catch (error) {
        console.error('Error loading portfolios:', error);
    }
}

function resetProjectFilterState(enableSelection) {
    const projectSelect = $('#portfolio-project-select');
    const hint = $('#project-filter-hint');

    projectSelect.empty();
    if (enableSelection) {
        projectSelect.prop('disabled', true);
        hint.text('Carregando projetos...');
    } else {
        projectSelect.prop('disabled', true);
        hint.text('Selecione um portfolio para habilitar o filtro por projetos.');
    }
    $('#project-filter-clear').prop('disabled', true);
}

function updateProjectFilterOptions(projects) {
    const projectSelect = $('#portfolio-project-select');
    const hint = $('#project-filter-hint');

    if (selectedPortfolioId === 'all' || !projects || !projects.length) {
        resetProjectFilterState(selectedPortfolioId !== 'all');
        return;
    }

    const sortedProjects = [...projects].sort((a, b) => {
        const nameA = (a.name || a.project_name || '').toLowerCase();
        const nameB = (b.name || b.project_name || '').toLowerCase();
        return nameA.localeCompare(nameB);
    });

    projectSelect.prop('disabled', false);
    projectSelect.empty();
    sortedProjects.forEach(project => {
        const value = project.id || project.project_id;
        const label = project.name || project.project_name || `Projeto ${value}`;
        projectSelect.append(
            $('<option></option>')
                .val(value)
                .text(label)
        );
    });

    if (selectedProjectFilters.length) {
        projectSelect.val(selectedProjectFilters.map(id => id.toString()));
    }

    hint.text('Selecione um ou mais projetos para refinar a visão.');
    $('#project-filter-clear').prop('disabled', selectedProjectFilters.length === 0);
}

function showPortfolioLoading() {
    $('#portfolio-content').html(`
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="sr-only">Carregando...</span>
            </div>
            <p class="mt-3 text-muted">Carregando dados do portfolio...</p>
        </div>
    `);
    $('#wsjf-ranking').empty();
    $('#wsjf-prioritization').hide();
}

async function loadPortfolioDashboard() {
    const currentToken = ++portfolioRequestToken;
    showPortfolioLoading();

    try {
        let url = '/api/portfolio/dashboard';
        const params = new URLSearchParams();

        if (selectedPortfolioId !== 'all') {
            params.append('portfolio_id', selectedPortfolioId);
        }
        if (selectedProjectFilters.length > 0) {
            params.append('project_ids', selectedProjectFilters.join(','));
        }
        if ([...params.keys()].length > 0) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Erro ao carregar dados de portfolio');
        }
        const data = await response.json();

        if (currentToken !== portfolioRequestToken) {
            // A newer request has been made; discard this response
            return;
        }

        if (!data.has_data) {
            updateProjectFilterOptions([]);
            renderEmptyState(data.message || 'Nenhum dado disponível.');
            hideEfficientFrontierSection(data.message || 'Nenhum dado disponível.');
            return;
        }

        if (selectedPortfolioId !== 'all') {
            updateProjectFilterOptions(data.projects || []);
        } else {
            resetProjectFilterState(false);
        }

        renderPortfolioDashboard(data);

        if (selectedPortfolioId !== 'all') {
            loadEfficientFrontier(selectedPortfolioId, selectedProjectFilters);
        } else {
            hideEfficientFrontierSection('Selecione um portfolio específico para visualizar a fronteira eficiente.');
        }
    } catch (error) {
        if (currentToken !== portfolioRequestToken) {
            return;
        }
        console.error('Error loading portfolio:', error);
        renderError('Erro ao carregar portfolio: ' + error.message);
        hideEfficientFrontierSection('Não foi possível calcular a fronteira eficiente.');
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

// ---------------------------------------------------------------------------
// Efficient Frontier (Markowitz)
// ---------------------------------------------------------------------------

function hideEfficientFrontierSection(message) {
    const section = $('#efficient-frontier-section');
    const info = $('#efficient-frontier-info');
    const alertBox = $('#efficient-frontier-message');

    if (efficientFrontierChart) {
        efficientFrontierChart.destroy();
        efficientFrontierChart = null;
    }

    $('#efficient-frontier-summary').html('');
    alertBox.hide();

    if (message) {
        info.text(message);
    }

    section.hide();
}

function showEfficientFrontierMessage(message, variant = 'info') {
    const section = $('#efficient-frontier-section');
    const alertBox = $('#efficient-frontier-message');

    section.show();
    $('#efficient-frontier-summary').html('');

    if (efficientFrontierChart) {
        efficientFrontierChart.destroy();
        efficientFrontierChart = null;
    }

    alertBox
        .show()
        .removeClass('alert-info alert-warning alert-danger alert-success')
        .addClass(`alert-${variant}`)
        .text(message);
}

function showEfficientFrontierLoading() {
    $('#efficient-frontier-info').text('Calculando fronteira eficiente com simulações de Monte Carlo...');
    showEfficientFrontierMessage('Processando dados do portfolio...', 'info');
}

async function loadEfficientFrontier(portfolioId, projectFilterIds = []) {
    if (!portfolioId || portfolioId === 'all') {
        hideEfficientFrontierSection('Selecione um portfolio específico para visualizar a fronteira eficiente.');
        return;
    }

    const currentToken = ++efficientFrontierRequestToken;
    showEfficientFrontierLoading();

    try {
        let url = `/api/portfolios/${portfolioId}/efficient-frontier`;
        const params = new URLSearchParams();

        if (projectFilterIds && projectFilterIds.length > 0) {
            params.append('project_ids', projectFilterIds.join(','));
        }

        if ([...params.keys()].length > 0) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Erro ao consultar a fronteira eficiente');
        }

        const data = await response.json();
        if (currentToken !== efficientFrontierRequestToken) {
            return;
        }

        if (data.error) {
            showEfficientFrontierMessage(data.error, 'warning');
            return;
        }

        renderEfficientFrontier(data);
    } catch (error) {
        if (currentToken !== efficientFrontierRequestToken) {
            return;
        }
        console.error('Erro ao calcular fronteira eficiente:', error);
        showEfficientFrontierMessage('Erro ao calcular a fronteira eficiente: ' + error.message, 'danger');
    }
}

function renderEfficientFrontier(data) {
    $('#efficient-frontier-section').show();
    $('#efficient-frontier-message').hide();

    const infoText = `Simulações Monte Carlo: ${data?.monte_carlo?.sample_size || 0} • Taxa livre de risco: ${formatPercent(data?.risk_free_rate || 0, 2)}`;
    $('#efficient-frontier-info').text(infoText);

    const monteCarloPoints = (data?.monte_carlo?.points || []).map(point => ({
        x: (point.risk || 0) * 100,
        y: (point.expected_return || 0) * 100,
        sharpe: point.sharpe
    }));

    const frontierPoints = (data?.efficient_frontier || []).map(point => ({
        x: (point.risk || 0) * 100,
        y: (point.expected_return || 0) * 100
    }));

    const chartEl = document.getElementById('efficientFrontierChart');
    if (!chartEl) {
        return;
    }

    const datasets = [
        {
            label: 'Portfólios Monte Carlo',
            data: monteCarloPoints,
            backgroundColor: 'rgba(102, 126, 234, 0.25)',
            borderColor: 'rgba(102, 126, 234, 0.25)',
            pointRadius: 3,
            pointHoverRadius: 4
        },
        {
            type: 'line',
            label: 'Fronteira Eficiente',
            data: frontierPoints,
            borderColor: '#f5576c',
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.25
        }
    ];

    if (data?.best_portfolio) {
        datasets.push({
            label: 'Melhor Portfólio (Sharpe)',
            data: [{
                x: (data.best_portfolio.risk || 0) * 100,
                y: (data.best_portfolio.expected_return || 0) * 100
            }],
            backgroundColor: '#28a745',
            borderColor: '#1e7e34',
            pointRadius: 6,
            pointHoverRadius: 7
        });
    }

    if (data?.current_portfolio) {
        datasets.push({
            label: 'Portfolio Atual',
            data: [{
                x: (data.current_portfolio.risk || 0) * 100,
                y: (data.current_portfolio.expected_return || 0) * 100
            }],
            backgroundColor: '#ffc107',
            borderColor: '#e0a800',
            pointRadius: 6,
            pointHoverRadius: 7
        });
    }

    if (efficientFrontierChart) {
        efficientFrontierChart.destroy();
    }

    efficientFrontierChart = new Chart(chartEl.getContext('2d'), {
        type: 'scatter',
        data: { datasets },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: context => {
                            const label = context.dataset.label || '';
                            const x = context.parsed.x?.toFixed(2) || '0.00';
                            const y = context.parsed.y?.toFixed(2) || '0.00';
                            return `${label}: retorno ${y}% • risco ${x}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Risco (desvio padrão %)'
                    },
                    ticks: { callback: value => `${value}%` }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Retorno esperado %'
                    },
                    ticks: { callback: value => `${value}%` }
                }
            }
        }
    });

    const summaryContainer = $('#efficient-frontier-summary');
    let summaryHtml = '';
    summaryHtml += renderPortfolioSummaryCard('Melhor Portfólio (Sharpe)', data.best_portfolio, 'success');
    summaryHtml += renderPortfolioSummaryCard('Portfolio Atual', data.current_portfolio, 'warning');
    summaryContainer.html(summaryHtml);
}

function renderPortfolioSummaryCard(title, summary, variant = 'info') {
    if (!summary) {
        return `
            <div class="alert alert-${variant} mb-3">
                ${title}: dados indisponíveis.
            </div>
        `;
    }

    const sharpe = Number(summary.sharpe || 0).toFixed(2);
    const weightsHtml = buildWeightsList(summary.weights || []);

    return `
        <div class="border rounded p-3 mb-3 bg-light">
            <h6 class="text-muted text-uppercase mb-2">${title}</h6>
            <p class="mb-1"><strong>Retorno:</strong> ${formatPercent(summary.expected_return)} • <strong>Risco:</strong> ${formatPercent(summary.risk)}</p>
            <p class="mb-2"><strong>Sharpe:</strong> ${sharpe}</p>
            <div class="small">
                ${weightsHtml}
            </div>
        </div>
    `;
}

function buildWeightsList(weights) {
    if (!weights.length) {
        return '<span class="text-muted">Distribuição uniforme.</span>';
    }

    const significantWeights = weights
        .filter(item => item.weight >= 0.01)
        .slice(0, 5);

    return significantWeights.map(weight => `
        <div class="d-flex justify-content-between mb-1">
            <span>${weight.project_name}</span>
            <strong>${formatPercent(weight.weight, 1)}</strong>
        </div>
    `).join('') || '<span class="text-muted">Pesos muito distribuídos.</span>';
}
