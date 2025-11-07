/**
 * Portfolio Manager JavaScript
 * Handles portfolio CRUD, project assignment, and simulations
 */

let currentPortfolioId = null;
let portfolios = [];
let projects = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolios();
});

/**
 * Load all portfolios for current user
 */
async function loadPortfolios() {
    try {
        const response = await fetch('/api/portfolios');
        if (!response.ok) throw new Error('Failed to load portfolios');

        portfolios = await response.json();
        renderPortfolioList();

    } catch (error) {
        console.error('Error loading portfolios:', error);
        showError('Erro ao carregar portfólios');
    }
}

/**
 * Render portfolio list in sidebar
 */
function renderPortfolioList() {
    const container = document.getElementById('portfoliosList');

    if (portfolios.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <p>Nenhum portfólio ainda</p>
                <button class="btn btn-primary btn-sm" onclick="showCreatePortfolioModal()">
                    <i class="fas fa-plus"></i> Criar Primeiro Portfólio
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = portfolios.map(p => `
        <div class="portfolio-card card mb-2" onclick="selectPortfolio(${p.id})">
            <div class="card-body p-3">
                <h6 class="mb-1">${escapeHtml(p.name)}</h6>
                <p class="text-muted small mb-2">${escapeHtml(p.description || '')}</p>
                <div>
                    <span class="badge bg-info">${p.projects_count} projetos</span>
                    <span class="badge bg-secondary">${p.status}</span>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Select and display portfolio details
 */
async function selectPortfolio(portfolioId) {
    currentPortfolioId = portfolioId;

    try {
        const response = await fetch(`/api/portfolios/${portfolioId}`);
        if (!response.ok) throw new Error('Failed to load portfolio');

        const portfolio = await response.json();
        renderPortfolioDetail(portfolio);

        // Load portfolio projects
        await loadPortfolioProjects(portfolioId);

    } catch (error) {
        console.error('Error loading portfolio:', error);
        showError('Erro ao carregar portfólio');
    }
}

/**
 * Render portfolio detail panel
 */
function renderPortfolioDetail(portfolio) {
    document.getElementById('portfolioDetail').style.display = 'block';
    document.getElementById('portfolioTitle').textContent = portfolio.name;

    const infoHtml = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Status:</strong> <span class="badge bg-info">${portfolio.status}</span></p>
                <p><strong>Tipo:</strong> ${portfolio.portfolio_type}</p>
                ${portfolio.owner ? `<p><strong>Responsável:</strong> ${escapeHtml(portfolio.owner)}</p>` : ''}
            </div>
            <div class="col-md-6">
                ${portfolio.total_budget ? `<p><strong>Orçamento:</strong> R$ ${formatNumber(portfolio.total_budget)}</p>` : ''}
                ${portfolio.total_capacity ? `<p><strong>Capacidade:</strong> ${portfolio.total_capacity} FTE</p>` : ''}
                ${portfolio.start_date ? `<p><strong>Início:</strong> ${portfolio.start_date}</p>` : ''}
            </div>
        </div>
        ${portfolio.description ? `<p class="text-muted mt-2">${escapeHtml(portfolio.description)}</p>` : ''}
    `;

    document.getElementById('portfolioInfo').innerHTML = infoHtml;
}

/**
 * Load projects in portfolio
 */
async function loadPortfolioProjects(portfolioId) {
    try {
        const response = await fetch(`/api/portfolios/${portfolioId}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');

        const portfolioProjects = await response.json();
        renderPortfolioProjects(portfolioProjects);

    } catch (error) {
        console.error('Error loading portfolio projects:', error);
        showError('Erro ao carregar projetos do portfólio');
    }
}

/**
 * Render projects in portfolio
 */
function renderPortfolioProjects(portfolioProjects) {
    const container = document.getElementById('portfolioProjects');

    if (portfolioProjects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Nenhum projeto adicionado ainda</p>
                <button class="btn btn-primary btn-sm" onclick="showAddProjectModal()">
                    <i class="fas fa-plus"></i> Adicionar Projeto
                </button>
            </div>
        `;
        return;
    }

    // Sort by WSJF score (descending) or priority
    portfolioProjects.sort((a, b) => {
        if (a.wsjf_score && b.wsjf_score) {
            return b.wsjf_score - a.wsjf_score;
        }
        return a.portfolio_priority - b.portfolio_priority;
    });

    container.innerHTML = portfolioProjects.map(pp => `
        <div class="project-item">
            <div class="row align-items-center">
                <div class="col-md-6">
                    <h6 class="mb-1">
                        ${escapeHtml(pp.project.name)}
                        ${pp.wsjf_score ? `<span class="wsjf-score ms-2">WSJF: ${pp.wsjf_score.toFixed(1)}</span>` : ''}
                    </h6>
                    <small class="text-muted">${escapeHtml(pp.project.description || '')}</small>
                </div>
                <div class="col-md-4">
                    <small>
                        <strong>Prioridade:</strong> ${pp.portfolio_priority}<br>
                        ${pp.cod_weekly ? `<strong>CoD:</strong> <span class="cod-badge badge">R$ ${formatNumber(pp.cod_weekly)}/sem</span>` : ''}
                    </small>
                </div>
                <div class="col-md-2 text-end">
                    <button class="btn btn-sm btn-outline-danger" onclick="removeProjectFromPortfolio(${pp.project_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Show create portfolio modal
 */
function showCreatePortfolioModal() {
    document.getElementById('portfolioModalTitle').textContent = 'Criar Portfólio';
    document.getElementById('portfolioForm').reset();
    document.getElementById('portfolioId').value = '';

    const modal = new bootstrap.Modal(document.getElementById('portfolioModal'));
    modal.show();
}

/**
 * Edit current portfolio
 */
async function editPortfolio() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}`);
        if (!response.ok) throw new Error('Failed to load portfolio');

        const portfolio = await response.json();

        document.getElementById('portfolioModalTitle').textContent = 'Editar Portfólio';
        document.getElementById('portfolioId').value = portfolio.id;
        document.getElementById('portfolioName').value = portfolio.name;
        document.getElementById('portfolioDescription').value = portfolio.description || '';
        document.getElementById('portfoliobudget').value = portfolio.total_budget || '';
        document.getElementById('portfolioCapacity').value = portfolio.total_capacity || '';
        document.getElementById('portfolioStartDate').value = portfolio.start_date || '';
        document.getElementById('portfolioEndDate').value = portfolio.target_end_date || '';

        const modal = new bootstrap.Modal(document.getElementById('portfolioModal'));
        modal.show();

    } catch (error) {
        console.error('Error loading portfolio for edit:', error);
        showError('Erro ao carregar portfólio');
    }
}

/**
 * Save portfolio (create or update)
 */
async function savePortfolio() {
    const portfolioId = document.getElementById('portfolioId').value;
    const isEdit = portfolioId !== '';

    const data = {
        name: document.getElementById('portfolioName').value,
        description: document.getElementById('portfolioDescription').value,
        total_budget: parseFloat(document.getElementById('portfoliobudget').value) || null,
        total_capacity: parseFloat(document.getElementById('portfolioCapacity').value) || null,
        start_date: document.getElementById('portfolioStartDate').value || null,
        target_end_date: document.getElementById('portfolioEndDate').value || null
    };

    try {
        const url = isEdit ? `/api/portfolios/${portfolioId}` : '/api/portfolios';
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Failed to save portfolio');

        const portfolio = await response.json();

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('portfolioModal'));
        modal.hide();

        // Reload portfolios
        await loadPortfolios();

        // Select the new/updated portfolio
        selectPortfolio(portfolio.id);

        showSuccess(isEdit ? 'Portfólio atualizado!' : 'Portfólio criado!');

    } catch (error) {
        console.error('Error saving portfolio:', error);
        showError('Erro ao salvar portfólio');
    }
}

/**
 * Show add project modal
 */
async function showAddProjectModal() {
    if (!currentPortfolioId) return;

    // Load available projects
    try {
        const response = await fetch('/api/projects');
        if (!response.ok) throw new Error('Failed to load projects');

        projects = await response.json();
        renderProjectsList();

        const modal = new bootstrap.Modal(document.getElementById('addProjectModal'));
        modal.show();

    } catch (error) {
        console.error('Error loading projects:', error);
        showError('Erro ao carregar projetos');
    }
}

/**
 * Render projects list for selection
 */
function renderProjectsList() {
    const container = document.getElementById('projectsList');

    if (projects.length === 0) {
        container.innerHTML = `
            <div class="text-center p-3">
                <p>Nenhum projeto disponível</p>
                <a href="/projects" class="btn btn-primary btn-sm">Criar Projeto</a>
            </div>
        `;
        return;
    }

    container.innerHTML = projects.map(p => `
        <div class="list-group-item list-group-item-action" onclick="selectProjectForAdd(${p.id})">
            <h6 class="mb-1">${escapeHtml(p.name)}</h6>
            <small class="text-muted">${escapeHtml(p.description || '')}</small>
        </div>
    `).join('');
}

/**
 * Select a project to add to portfolio
 */
function selectProjectForAdd(projectId) {
    document.getElementById('selectedProjectId').value = projectId;
    document.getElementById('projectDetailsForm').style.display = 'block';
    document.getElementById('addProjectBtn').disabled = false;

    // Highlight selected project
    document.querySelectorAll('#projectsList .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

/**
 * Add project to portfolio
 */
async function addProjectToPortfolio() {
    const projectId = document.getElementById('selectedProjectId').value;
    if (!projectId) return;

    const data = {
        project_id: parseInt(projectId),
        portfolio_priority: parseInt(document.getElementById('projectPriority').value),
        cod_weekly: parseFloat(document.getElementById('projectCoD').value) || null,
        business_value_score: parseInt(document.getElementById('projectBusinessValue').value),
        time_criticality_score: parseInt(document.getElementById('projectTimeCriticality').value),
        risk_reduction_score: parseInt(document.getElementById('projectRiskReduction').value)
    };

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add project');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addProjectModal'));
        modal.hide();

        // Reload portfolio projects
        await loadPortfolioProjects(currentPortfolioId);
        await loadPortfolios();  // Update project count

        showSuccess('Projeto adicionado ao portfólio!');

    } catch (error) {
        console.error('Error adding project:', error);
        showError(error.message || 'Erro ao adicionar projeto');
    }
}

/**
 * Remove project from portfolio
 */
async function removeProjectFromPortfolio(projectId) {
    if (!confirm('Remover este projeto do portfólio?')) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/projects/${projectId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to remove project');

        await loadPortfolioProjects(currentPortfolioId);
        await loadPortfolios();  // Update project count

        showSuccess('Projeto removido do portfólio');

    } catch (error) {
        console.error('Error removing project:', error);
        showError('Erro ao remover projeto');
    }
}

/**
 * Run portfolio simulation
 */
async function runSimulation() {
    if (!currentPortfolioId) return;

    // Show loading
    document.getElementById('simulationResults').style.display = 'block';
    document.getElementById('simulationContent').innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status"></div>
            <p class="lead">Executando simulação de Monte Carlo...</p>
            <p class="text-muted">Isso pode levar alguns segundos</p>
        </div>
    `;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                n_simulations: 10000,
                confidence_level: 'P85',
                execution_mode: 'compare'  // Compare parallel vs sequential
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Simulation failed');
        }

        const result = await response.json();
        renderSimulationResults(result);

    } catch (error) {
        console.error('Error running simulation:', error);
        document.getElementById('simulationContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Erro:</strong> ${error.message}
            </div>
        `;
    }
}

/**
 * Render simulation results
 */
function renderSimulationResults(result) {
    const parallel = result.parallel;
    const sequential = result.sequential;
    const comparison = result.comparison;

    const html = `
        <div class="row mb-4">
            <div class="col-md-12">
                <h5><i class="fas fa-chart-line"></i> Comparação: Execução Paralela vs Sequencial</h5>
                <div class="alert alert-info">
                    <strong>Recomendação:</strong> Execução ${comparison.recommendation === 'parallel' ? 'Paralela' : 'Sequencial'}
                    ${comparison.time_diff_p85 ? ` (economia de ${Math.abs(comparison.time_diff_p85).toFixed(1)} semanas)` : ''}
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-success text-white">
                        <strong>Execução Paralela</strong>
                        <small class="float-end">(Projetos simultâneos)</small>
                    </div>
                    <div class="card-body">
                        ${renderCompletionMetrics(parallel.completion_forecast)}
                        ${parallel.cost_of_delay.total_cod ? `<p><strong>Cost of Delay Total:</strong> <span class="text-danger">R$ ${formatNumber(parallel.cost_of_delay.total_cod)}</span></p>` : ''}
                        <p><strong>Risco:</strong> <span class="badge ${parallel.risk.score > 50 ? 'bg-danger' : 'bg-success'}">${parallel.risk.score.toFixed(1)}</span></p>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-primary text-white">
                        <strong>Execução Sequencial</strong>
                        <small class="float-end">(Projetos um após o outro)</small>
                    </div>
                    <div class="card-body">
                        ${renderCompletionMetrics(sequential.completion_forecast)}
                        ${sequential.cost_of_delay.total_cod ? `<p><strong>Cost of Delay Total:</strong> <span class="text-danger">R$ ${formatNumber(sequential.cost_of_delay.total_cod)}</span></p>` : ''}
                        <p><strong>Risco:</strong> <span class="badge ${sequential.risk.score > 50 ? 'bg-danger' : 'bg-success'}">${sequential.risk.score.toFixed(1)}</span></p>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <strong>Previsão por Projeto (Execução Paralela)</strong>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Projeto</th>
                                <th>P50</th>
                                <th>P85</th>
                                <th>P95</th>
                                <th>Cost of Delay</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${parallel.project_results.map(pr => `
                                <tr>
                                    <td><strong>${escapeHtml(pr.project_name)}</strong></td>
                                    <td>${pr.p50_weeks} sem</td>
                                    <td>${pr.p85_weeks} sem</td>
                                    <td>${pr.p95_weeks} sem</td>
                                    <td>${pr.cod_total ? `R$ ${formatNumber(pr.cod_total)}` : '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    document.getElementById('simulationContent').innerHTML = html;
}

/**
 * Render completion metrics
 */
function renderCompletionMetrics(forecast) {
    return `
        <div class="row text-center mb-3">
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-value">${forecast.p50_weeks}</div>
                    <div class="metric-label">P50 (semanas)</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-value">${forecast.p85_weeks}</div>
                    <div class="metric-label">P85 (semanas)</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-value">${forecast.p95_weeks}</div>
                    <div class="metric-label">P95 (semanas)</div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Utility: Format number with thousand separators
 */
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(num);
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Simple alert for now - can be replaced with toast notification
    alert(message);
}

/**
 * Show error message
 */
function showError(message) {
    alert('Erro: ' + message);
}

/**
 * Run Cost of Delay analysis
 */
async function runCoDAnalysis() {
    if (!currentPortfolioId) return;

    // Show loading
    document.getElementById('simulationResults').style.display = 'block';
    document.getElementById('simulationContent').innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status"></div>
            <p class="lead">Analisando Cost of Delay...</p>
            <p class="text-muted">Otimizando sequência por WSJF</p>
        </div>
    `;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/cod-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'CoD analysis failed');
        }

        const result = await response.json();
        renderCoDAnalysisResults(result);

    } catch (error) {
        console.error('Error running CoD analysis:', error);
        document.getElementById('simulationContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Erro:</strong> ${error.message}
            </div>
        `;
    }
}

/**
 * Render Cost of Delay analysis results
 */
function renderCoDAnalysisResults(result) {
    const optimization = result.optimization;
    const strategies = result.strategy_comparison.strategies;
    const bestStrategy = result.strategy_comparison.best_strategy;

    const html = `
        <div class="row mb-4">
            <div class="col-md-12">
                <h5><i class="fas fa-dollar-sign"></i> Análise de Cost of Delay</h5>
                <div class="alert alert-success">
                    <strong>Economia com WSJF:</strong> R$ ${formatNumber(optimization.cod_savings)}
                    (${optimization.cod_savings_pct.toFixed(1)}% de redução no CoD total)
                </div>
            </div>
        </div>

        <!-- CoD Totals Comparison -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Paralelo</h6>
                        <h3 class="text-success">R$ ${formatNumber(result.totals.parallel.total_cod)}</h3>
                        <p class="small mb-0">${result.totals.parallel.duration_p85.toFixed(1)} semanas</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Sequencial (não otimizado)</h6>
                        <h3 class="text-danger">R$ ${formatNumber(result.totals.sequential_unoptimized.total_cod)}</h3>
                        <p class="small mb-0">${result.totals.sequential_unoptimized.duration_p85.toFixed(1)} semanas</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center border-success">
                    <div class="card-body">
                        <h6 class="text-muted">Sequencial (WSJF otimizado)</h6>
                        <h3 class="text-success">R$ ${formatNumber(result.totals.sequential_optimized.total_cod)}</h3>
                        <p class="small mb-0">${result.totals.sequential_optimized.duration_p85.toFixed(1)} semanas</p>
                        <span class="badge bg-success mt-2">Recomendado</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- WSJF Ranking -->
        <div class="card mb-4">
            <div class="card-header">
                <strong><i class="fas fa-trophy"></i> Ranking WSJF - Ordem de Execução Recomendada</strong>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Projeto</th>
                                <th>WSJF Score</th>
                                <th>CoD Total</th>
                                <th>Recomendação</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${optimization.optimized_sequence.map((projectId, index) => {
                                const ranking = optimization.project_rankings[projectId];
                                return `
                                    <tr>
                                        <td><strong>${index + 1}</strong></td>
                                        <td>${escapeHtml(ranking.name)}</td>
                                        <td><span class="wsjf-score">${ranking.wsjf}</span></td>
                                        <td>R$ ${formatNumber(ranking.cod)}</td>
                                        <td>
                                            ${index === 0 ? '<span class="badge bg-danger">URGENTE - Fazer Primeiro!</span>' :
                                              index === 1 ? '<span class="badge bg-warning">Alta Prioridade</span>' :
                                              '<span class="badge bg-secondary">Normal</span>'}
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Strategy Comparison -->
        <div class="card mb-4">
            <div class="card-header">
                <strong><i class="fas fa-balance-scale"></i> Comparação de Estratégias de Priorização</strong>
            </div>
            <div class="card-body">
                <p class="text-muted">Comparando diferentes métodos de priorização:</p>
                <div class="row">
                    ${Object.keys(strategies).map(strategyName => {
                        const strategy = strategies[strategyName];
                        const isBest = strategy.is_best;
                        const strategyLabel = {
                            'wsjf': 'WSJF (Recomendado)',
                            'shortest_first': 'Menor Duração Primeiro',
                            'highest_cod_first': 'Maior CoD Primeiro',
                            'business_value_first': 'Maior Valor de Negócio'
                        }[strategyName];

                        return `
                            <div class="col-md-6 mb-3">
                                <div class="card ${isBest ? 'border-success' : ''}">
                                    <div class="card-body">
                                        <h6>${strategyLabel}</h6>
                                        <p class="mb-0">
                                            <strong>CoD Total:</strong> R$ ${formatNumber(strategy.total_cod)}
                                            ${isBest ? '<span class="badge bg-success ms-2">Melhor</span>' : ''}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div class="alert alert-info mt-3">
                    <strong>Melhor Estratégia:</strong> ${
                        bestStrategy === 'wsjf' ? 'WSJF (balanceia valor, criticidade e duração)' :
                        bestStrategy === 'shortest_first' ? 'Menor Duração Primeiro' :
                        bestStrategy === 'highest_cod_first' ? 'Maior CoD Primeiro' :
                        'Maior Valor de Negócio'
                    }
                </div>
            </div>
        </div>

        <!-- Risk Assessment -->
        <div class="card">
            <div class="card-header">
                <strong><i class="fas fa-exclamation-triangle"></i> Avaliação de Riscos</strong>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Projetos com Alto CoD</h6>
                        ${result.risk_assessment.high_cod_projects.length > 0 ? `
                            <ul class="list-unstyled">
                                ${result.risk_assessment.high_cod_projects.map(pid => {
                                    const project = result.projects.find(p => p.project_id === pid);
                                    return project ? `
                                        <li>
                                            <i class="fas fa-exclamation-circle text-danger"></i>
                                            ${escapeHtml(project.project_name)}
                                            <span class="cod-badge badge">R$ ${formatNumber(project.total_cod)}/total</span>
                                        </li>
                                    ` : '';
                                }).join('')}
                            </ul>
                        ` : '<p class="text-muted">Nenhum projeto com CoD crítico</p>'}
                    </div>
                    <div class="col-md-6">
                        <h6>Projetos com Prazos Críticos</h6>
                        ${result.risk_assessment.critical_deadline_projects.length > 0 ? `
                            <ul class="list-unstyled">
                                ${result.risk_assessment.critical_deadline_projects.map(pid => {
                                    const project = result.projects.find(p => p.project_id === pid);
                                    return project ? `
                                        <li>
                                            <i class="fas fa-clock text-warning"></i>
                                            ${escapeHtml(project.project_name)}
                                            <span class="badge bg-warning">Criticidade: ${project.time_criticality}</span>
                                        </li>
                                    ` : '';
                                }).join('')}
                            </ul>
                        ` : '<p class="text-muted">Nenhum projeto com prazo crítico</p>'}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById('simulationContent').innerHTML = html;
}
