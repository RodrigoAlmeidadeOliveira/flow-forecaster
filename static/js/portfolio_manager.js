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

    // Initialize Bootstrap tooltips
    initializeTooltips();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

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
 * Run portfolio simulation WITH DEPENDENCIES
 * Implements multi-team forecasting with dependency analysis
 */
async function runSimulationWithDependencies() {
    if (!currentPortfolioId) return;

    // Show loading
    const btnSimulation = document.getElementById('btnRunSimulation');
    const spinner = document.getElementById('simulationSpinner');
    const resultsContainer = document.getElementById('dependencySimulationResults');

    btnSimulation.disabled = true;
    spinner.style.display = 'block';
    resultsContainer.style.display = 'none';

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/simulate-with-dependencies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                n_simulations: 10000,
                confidence_level: 'P85'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Simulation failed');
        }

        const result = await response.json();
        renderDependencySimulationResults(result);

    } catch (error) {
        console.error('Error running dependency simulation:', error);
        const resultsContainer = document.getElementById('dependencySimulationResults');
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = `
            <div class="card border-danger">
                <div class="card-body">
                    <div class="alert alert-danger mb-0">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Erro:</strong> ${error.message}
                    </div>
                </div>
            </div>
        `;
    } finally {
        btnSimulation.disabled = false;
        spinner.style.display = 'none';
    }
}

/**
 * Render dependency simulation results
 * Shows combined probabilities and dependency impact
 */
function renderDependencySimulationResults(result) {
    const baseline = result.baseline_forecast || {};
    const adjusted = result.adjusted_forecast || {};
    const impact = result.dependency_impact || {};
    const depAnalysis = result.dependency_analysis || {};
    const combinedProbs = result.combined_probabilities || {};
    const projectResults = result.project_results || {};

    const formatWeeks = (value) => Number.isFinite(value) ? value.toFixed(2) : '—';
    const formatPercent = (value) => Number.isFinite(value) ? value.toFixed(1) + '%' : '—';

    // Combined Probabilities Card
    const combinedProbsCard = `
        <div class="card mb-4 border-primary">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fas fa-calculator mr-2"></i>
                    Combined Probabilities (Multi-Team)
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <h6 class="text-muted mb-2">Dependency On-Time</h6>
                            <h3 class="text-primary mb-0">${formatPercent(combinedProbs.dependency_on_time_probability)}</h3>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <h6 class="text-muted mb-2">Team Combined</h6>
                            <h3 class="text-info mb-0">${formatPercent(combinedProbs.team_combined_probability)}</h3>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-warning rounded">
                            <h6 class="text-dark mb-2">Overall Probability ⭐</h6>
                            <h3 class="text-dark mb-0">${formatPercent(combinedProbs.overall_on_time_probability)}</h3>
                        </div>
                    </div>
                </div>
                <div class="alert alert-info mt-3 mb-0">
                    <i class="fas fa-info-circle mr-2"></i>
                    ${combinedProbs.explanation || 'Combined probability across all teams and dependencies.'}
                </div>
            </div>
        </div>
    `;

    // Baseline vs Adjusted Forecast
    const forecastComparisonCard = `
        <div class="card mb-4">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="fas fa-chart-line mr-2"></i>
                    Forecast Comparison: Baseline vs With Dependencies
                </h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Scenario</th>
                                <th>P50 (weeks)</th>
                                <th>P85 (weeks)</th>
                                <th>P95 (weeks)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Baseline (No Dependencies)</strong></td>
                                <td>${formatWeeks(baseline.p50_weeks)}</td>
                                <td>${formatWeeks(baseline.p85_weeks)}</td>
                                <td>${formatWeeks(baseline.p95_weeks)}</td>
                            </tr>
                            <tr class="table-warning">
                                <td><strong>Adjusted (With Dependencies)</strong></td>
                                <td>${formatWeeks(adjusted.p50_weeks)}</td>
                                <td>${formatWeeks(adjusted.p85_weeks)}</td>
                                <td>${formatWeeks(adjusted.p95_weeks)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="alert alert-warning mt-3">
                    <h6 class="alert-heading"><i class="fas fa-exclamation-triangle mr-2"></i>Dependency Impact</h6>
                    <ul class="mb-0">
                        <li>Additional delay (P85): <strong>+${formatWeeks(impact.delay_weeks_p85)} weeks</strong> (${formatPercent(impact.delay_percentage_p85)} increase)</li>
                        <li>Additional delay (P95): <strong>+${formatWeeks(impact.delay_weeks_p95)} weeks</strong></li>
                    </ul>
                </div>
            </div>
        </div>
    `;

    // Dependency Analysis
    const depAnalysisCard = depAnalysis.total_dependencies ? `
        <div class="card mb-4">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="fas fa-project-diagram mr-2"></i>
                    Dependency Analysis
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-3">
                        <strong>Total Dependencies:</strong> ${depAnalysis.total_dependencies}
                    </div>
                    <div class="col-md-3">
                        <strong>Risk Score:</strong>
                        <span class="badge ${depAnalysis.risk_score >= 70 ? 'bg-danger' : depAnalysis.risk_score >= 40 ? 'bg-warning' : 'bg-success'}">
                            ${depAnalysis.risk_score}/100
                        </span>
                    </div>
                    <div class="col-md-3">
                        <strong>Risk Level:</strong>
                        <span class="badge ${depAnalysis.risk_level === 'CRITICAL' ? 'bg-danger' : depAnalysis.risk_level === 'HIGH' ? 'bg-warning' : 'bg-info'}">
                            ${depAnalysis.risk_level}
                        </span>
                    </div>
                    <div class="col-md-3">
                        <strong>Expected Delay:</strong> ${depAnalysis.expected_delay_days?.toFixed(1) || 0} days
                    </div>
                </div>

                ${depAnalysis.critical_path && depAnalysis.critical_path.length > 0 ? `
                    <div class="mb-3">
                        <h6>Critical Path (Top Dependencies):</h6>
                        <ul class="list-unstyled">
                            ${depAnalysis.critical_path.slice(0, 5).map(dep => `<li><i class="fas fa-link text-danger mr-2"></i>${dep}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        </div>
    ` : '';

    // Project-Level Results
    const projectLevelCard = projectResults.adjusted && projectResults.adjusted.length > 0 ? `
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0">
                    <i class="fas fa-list mr-2"></i>
                    Project-Level Forecasts
                </h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Project</th>
                                <th>Baseline P85</th>
                                <th>Adjusted P85</th>
                                <th>Delay vs Baseline</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${projectResults.adjusted.map(pr => {
                                const baseline_pr = projectResults.baseline.find(b => b.project_id === pr.project_id);
                                return `
                                    <tr>
                                        <td><strong>${escapeHtml(pr.project_name)}</strong></td>
                                        <td>${formatWeeks(baseline_pr?.p85_weeks || 0)}</td>
                                        <td>${formatWeeks(pr.p85_weeks)}</td>
                                        <td>
                                            ${pr.delay_vs_baseline > 0 ?
                                                `<span class="text-danger">+${formatWeeks(pr.delay_vs_baseline)}</span>` :
                                                '<span class="text-success">No delay</span>'}
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    ` : '';

    // Process Behaviour Chart (PBC) Analysis
    const pbcAnalysis = result.pbc_analysis || {};
    const pbcSummary = pbcAnalysis.summary || {};
    const pbcWarnings = pbcAnalysis.warnings || [];

    const pbcCard = pbcSummary.total_projects_analyzed ? `
        <div class="card mt-4 ${pbcWarnings.length > 0 ? 'border-warning' : 'border-success'}">
            <div class="card-header ${pbcWarnings.length > 0 ? 'bg-warning' : 'bg-success'} text-white">
                <h5 class="mb-0">
                    <i class="fas fa-chart-bar mr-2"></i>
                    Process Behaviour Chart (PBC) - Data Quality Validation
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Projects Analyzed</h6>
                            <h4>${pbcSummary.total_projects_analyzed}</h4>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Poor Data Quality</h6>
                            <h4 class="${pbcWarnings.length > 0 ? 'text-warning' : 'text-success'}">
                                ${pbcSummary.projects_with_poor_data}
                            </h4>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <h6 class="text-muted">Overall Quality</h6>
                            <h4>
                                <span class="badge ${
                                    pbcSummary.overall_data_quality === 'Good' ? 'bg-success' :
                                    pbcSummary.overall_data_quality === 'Fair' ? 'bg-warning' : 'bg-danger'
                                }">
                                    ${pbcSummary.overall_data_quality}
                                </span>
                            </h4>
                        </div>
                    </div>
                </div>

                ${pbcWarnings.length > 0 ? `
                    <div class="alert alert-warning">
                        <h6 class="alert-heading">
                            <i class="fas fa-exclamation-triangle mr-2"></i>
                            Data Quality Warnings
                        </h6>
                        <ul class="mb-0">
                            ${pbcWarnings.map(w => `
                                <li>
                                    <strong>${escapeHtml(w.project_name)}</strong>:
                                    Predictability Score ${w.score.toFixed(0)}/100
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle mr-2"></i>
                        All projects have good throughput data quality. Forecasts are reliable.
                    </div>
                `}

                ${pbcAnalysis.by_project && Object.keys(pbcAnalysis.by_project).length > 0 ? `
                    <div class="mt-3">
                        <h6>Details by Project:</h6>
                        <div class="accordion" id="pbcAccordion">
                            ${Object.entries(pbcAnalysis.by_project).map(([projectId, pbc], index) => {
                                if (!pbc) return '';
                                const project = projectResults.adjusted?.find(p => p.project_id == projectId);
                                const projectName = project ? project.project_name : `Project ${projectId}`;

                                return `
                                    <div class="accordion-item">
                                        <h2 class="accordion-header" id="heading${projectId}">
                                            <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button"
                                                    data-bs-toggle="collapse" data-bs-target="#collapse${projectId}">
                                                ${escapeHtml(projectName)}
                                                <span class="badge ${pbc.is_predictable ? 'bg-success' : 'bg-warning'} ms-2">
                                                    ${pbc.predictability_score.toFixed(0)}/100
                                                </span>
                                            </button>
                                        </h2>
                                        <div id="collapse${projectId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}"
                                             data-bs-parent="#pbcAccordion">
                                            <div class="accordion-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <p><strong>Average:</strong> ${pbc.average.toFixed(2)}</p>
                                                        <p><strong>UNPL:</strong> ${pbc.unpl.toFixed(2)}</p>
                                                        <p><strong>LNL:</strong> ${pbc.lnl.toFixed(2)}</p>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <p><strong>Predictable:</strong> ${pbc.is_predictable ? 'Yes ✓' : 'No ✗'}</p>
                                                        <p><strong>Quality:</strong> ${pbc.interpretation.quality}</p>
                                                        <p><strong>Can Forecast:</strong> ${pbc.interpretation.can_forecast ? 'Yes ✓' : 'No ✗'}</p>
                                                    </div>
                                                </div>
                                                ${pbc.signals && pbc.signals.length > 0 ? `
                                                    <div class="mt-2">
                                                        <strong>Signals Detected:</strong>
                                                        <ul class="small">
                                                            ${pbc.signals.map(s => `<li>${s}</li>`).join('')}
                                                        </ul>
                                                    </div>
                                                ` : ''}
                                                <div class="mt-2">
                                                    <em class="small text-muted">${pbc.recommendation}</em>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="mt-3 small text-muted">
                    <i class="fas fa-info-circle mr-1"></i>
                    <strong>About PBC:</strong> Process Behaviour Charts validate if throughput data is predictable.
                    Scores below 60 indicate unreliable data that may produce inaccurate forecasts.
                </div>
            </div>
        </div>
    ` : '';

    // Recommendations
    const recommendationsCard = result.recommendations && result.recommendations.length > 0 ? `
        <div class="card mt-4 border-info">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="fas fa-lightbulb mr-2"></i>
                    Recommendations
                </h5>
            </div>
            <div class="card-body">
                <ul class="mb-0">
                    ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        </div>
    ` : '';

    // Render everything
    const resultsContainer = document.getElementById('dependencySimulationResults');
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        ${combinedProbsCard}
        ${forecastComparisonCard}
        ${depAnalysisCard}
        ${pbcCard}
        ${projectLevelCard}
        ${recommendationsCard}
    `;
}

/**
 * Render simulation results
 */
function renderSimulationResults(result) {
    const parallel = result.parallel || {};
    const sequential = result.sequential || {};
    const comparison = result.comparison || {};
    const projectResults = (parallel.project_results || []);

    const formatWeeks = (value) => Number.isFinite(value) ? value.toFixed(2) : '—';
    const formatRiskBadge = (score) => {
        if (!Number.isFinite(score)) return '<span class="badge bg-secondary">—</span>';
        const badgeClass = score >= 70 ? 'bg-danger' : score >= 40 ? 'bg-warning' : 'bg-success';
        return `<span class="badge ${badgeClass}">${score.toFixed(1)}</span>`;
    };

    const renderScenarioRow = (label, subtitle, scenario, tone) => {
        const forecast = scenario.completion_forecast || {};
        const totalCod = scenario.cost_of_delay ? scenario.cost_of_delay.total_cod : null;
        const riskScore = scenario.risk ? scenario.risk.score : null;
        return `
            <tr class="${tone === 'highlight' ? 'table-success' : ''}">
                <td class="text-left">
                    <div class="scenario-label ${tone === 'positive' ? 'text-success' : tone === 'primary' ? 'text-primary' : ''}">${label}</div>
                    <small class="text-muted">${subtitle}</small>
                </td>
                <td>${formatWeeks(forecast.p50_weeks)}</td>
                <td>${formatWeeks(forecast.p85_weeks)}</td>
                <td>${formatWeeks(forecast.p95_weeks)}</td>
                <td>${totalCod ? `R$ ${formatNumber(totalCod)}` : '—'}</td>
                <td>${formatRiskBadge(riskScore)}</td>
            </tr>
        `;
    };

    const comparisonTable = `
        <div class="card simulation-comparison mb-4">
            <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center flex-wrap">
                <div>
                    <h5 class="mb-1"><i class="fas fa-exchange-alt mr-2 text-primary"></i>Comparação de Execuções</h5>
                    <small class="text-muted">Percentis de conclusão e impacto financeiro</small>
                </div>
                <div class="text-right">
                    <span class="badge badge-pill badge-primary">
                        Recomendação: ${comparison.recommendation === 'parallel' ? 'Execução Paralela' : 'Execução Sequencial'}
                    </span>
                    ${comparison.time_diff_p85 ? `<p class="small text-muted mb-0">Diferença P85: ${Math.abs(comparison.time_diff_p85).toFixed(1)} semanas</p>` : ''}
                </div>
            </div>
            <div class="card-body pt-0">
                <div class="table-responsive">
                    <table class="table table-sm table-striped align-middle simulation-compare-table">
                        <thead class="table-light">
                            <tr>
                                <th class="text-left">Cenário</th>
                                <th>P50</th>
                                <th>P85</th>
                                <th>P95</th>
                                <th>Cost of Delay</th>
                                <th>Risco</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${renderScenarioRow('Execução Paralela', 'Projetos simultâneos', parallel, comparison.recommendation === 'parallel' ? 'highlight' : 'positive')}
                            ${renderScenarioRow('Execução Sequencial', 'Projetos um após o outro', sequential, comparison.recommendation === 'sequential' ? 'highlight' : 'primary')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    const projectTable = `
        <div class="card">
            <div class="card-header bg-white border-0">
                <strong>Previsão por Projeto (Execução Paralela)</strong>
            </div>
            <div class="card-body pt-0">
                <div class="table-responsive">
                    <table class="table table-hover table-sm align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>Projeto</th>
                                <th>P50 (sem)</th>
                                <th>P85 (sem)</th>
                                <th>P95 (sem)</th>
                                <th>Cost of Delay</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${projectResults.length ? projectResults.map(pr => `
                                <tr>
                                    <td><strong>${escapeHtml(pr.project_name)}</strong></td>
                                    <td>${formatWeeks(pr.p50_weeks)}</td>
                                    <td>${formatWeeks(pr.p85_weeks)}</td>
                                    <td>${formatWeeks(pr.p95_weeks)}</td>
                                    <td>${pr.cod_total ? `R$ ${formatNumber(pr.cod_total)}` : '—'}</td>
                                </tr>
                            `).join('') : `<tr><td colspan="5" class="text-muted text-center">Nenhum projeto encontrado.</td></tr>`}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    document.getElementById('simulationContent').innerHTML = comparisonTable + projectTable;
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
 * Display detailed CoD analysis error with issues, hints and actions
 */
function displayCoDAnalysisError(errorData) {
    let html = `
        <div class="alert alert-danger">
            <h5 class="alert-heading">
                <i class="fas fa-exclamation-triangle"></i> ${errorData.error}
            </h5>
    `;

    // Display issues if available
    if (errorData.issues && errorData.issues.length > 0) {
        errorData.issues.forEach(issue => {
            html += `
                <div class="mt-3 ps-3 border-start border-3 border-danger">
                    <strong>${issue.message}</strong>

                    ${issue.projects && issue.projects.length > 0 ? `
                        <div class="mt-2">
                            <small class="text-muted d-block mb-1">Projetos afetados:</small>
                            <ul class="mb-2">
                                ${issue.projects.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    ${issue.hint ? `
                        <div class="alert alert-info mb-2 p-2">
                            <i class="fas fa-lightbulb"></i> <strong>Dica:</strong> ${issue.hint}
                        </div>
                    ` : ''}

                    ${issue.action ? `
                        <div class="alert alert-warning mb-2 p-2">
                            <i class="fas fa-hand-point-right"></i> <strong>Ação:</strong> ${issue.action}
                        </div>
                    ` : ''}
                </div>
            `;
        });
    } else if (errorData.hint) {
        // Simple error with hint
        html += `
            <hr>
            <p class="mb-1"><strong>Dica:</strong> ${errorData.hint}</p>
            ${errorData.action ? `<p class="mb-0"><strong>Ação:</strong> ${errorData.action}</p>` : ''}
        `;
    }

    html += `</div>`;
    document.getElementById('simulationContent').innerHTML = html;
}

/**
 * Display warnings at the top of CoD analysis results
 */
function displayCoDAnalysisWarnings(warnings) {
    const warningsContainer = document.getElementById('simulationContent');

    let html = '';
    warnings.forEach(warning => {
        const severityClass = warning.severity === 'warning' ? 'warning' : 'info';

        html += `
            <div class="alert alert-${severityClass} alert-dismissible fade show" role="alert">
                <h6 class="alert-heading">
                    <i class="fas fa-exclamation-circle"></i> ${warning.message}
                </h6>

                ${warning.projects && warning.projects.length > 0 ? `
                    <small class="d-block mb-2">
                        Projetos: ${warning.projects.join(', ')}
                    </small>
                ` : ''}

                ${warning.hint ? `
                    <small class="d-block mb-1">
                        <i class="fas fa-lightbulb"></i> ${warning.hint}
                    </small>
                ` : ''}

                ${warning.impact ? `
                    <small class="d-block text-muted">
                        Impacto: ${warning.impact}
                    </small>
                ` : ''}

                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    });

    // Prepend warnings to existing content
    warningsContainer.innerHTML = html + warningsContainer.innerHTML;
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
            const errorData = await response.json();
            displayCoDAnalysisError(errorData);
            return;
        }

        const result = await response.json();

        // Check for warnings
        if (result.warnings && result.warnings.length > 0) {
            displayCoDAnalysisWarnings(result.warnings);
        }

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
    const optimizationRaw = result.optimization || {};
    const strategyComparison = result.strategy_comparison || {};
    const strategies = strategyComparison.strategies || {};
    const bestStrategy = strategyComparison.best_strategy || null;
    const riskAssessment = result.risk_assessment || { high_cod_projects: [], critical_deadline_projects: [] };
    const totals = result.totals || {};

    const savingsBlock = optimizationRaw.savings || {};
    const optimizedBlock = optimizationRaw.optimized || {};
    const originalBlock = optimizationRaw.original || {};
    const projectRankingsRaw = optimizationRaw.project_rankings || {};

    const safeTotals = {
        parallel: totals.parallel || {},
        sequential_unoptimized: totals.sequential_unoptimized || {},
        sequential_optimized: totals.sequential_optimized || {}
    };

    const optimizedSequence = Array.isArray(optimizedBlock.sequence)
        ? optimizedBlock.sequence
        : (Array.isArray(optimizationRaw.optimized_sequence) ? optimizationRaw.optimized_sequence : []);

    const projectRankings = {};
    Object.entries(projectRankingsRaw).forEach(([key, value]) => {
        const numericKey = Number(key);
        projectRankings[numericKey] = value;
    });

    const safeOptimization = {
        cod_savings: Number.isFinite(savingsBlock.cod_savings)
            ? savingsBlock.cod_savings
            : Number.isFinite(optimizationRaw.cod_savings) ? optimizationRaw.cod_savings : 0,
        cod_savings_pct: Number.isFinite(savingsBlock.cod_savings_pct)
            ? savingsBlock.cod_savings_pct
            : Number.isFinite(optimizationRaw.cod_savings_pct) ? optimizationRaw.cod_savings_pct : 0,
        optimized_sequence: optimizedSequence,
        project_rankings: projectRankings,
        original_total_cod: originalBlock.total_cod || safeTotals.sequential_unoptimized.total_cod || 0,
        optimized_total_cod: optimizedBlock.total_cod || safeTotals.sequential_optimized.total_cod || 0
    };

    const hasPositiveSavings = safeOptimization.cod_savings > 1;
    const hasNegativeSavings = safeOptimization.cod_savings < -1;
    const savingsAlertClass = hasPositiveSavings ? 'alert-success' : hasNegativeSavings ? 'alert-danger' : 'alert-warning';
    const savingsMessage = hasPositiveSavings
        ? `Economia com WSJF: <strong>R$ ${formatNumber(safeOptimization.cod_savings)}</strong> (${safeOptimization.cod_savings_pct.toFixed(1)}% de redução no CoD total)`
        : hasNegativeSavings
            ? `WSJF não reduziu o Cost of Delay. Diferença: <strong>+R$ ${formatNumber(Math.abs(safeOptimization.cod_savings))}</strong>`
            : 'WSJF não gerou economia relevante com os dados atuais.';

    const formatWeeks = (value) => Number.isFinite(value) ? `${value.toFixed(1)} semanas` : '—';

    const html = `
        <div class="row mb-4">
            <div class="col-md-12">
                <h5><i class="fas fa-dollar-sign"></i> Análise de Cost of Delay</h5>
                <div class="alert ${savingsAlertClass}">
                    ${savingsMessage}
                </div>
            </div>
        </div>

        <!-- CoD Totals Comparison -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Paralelo</h6>
                        <h3 class="text-success">R$ ${formatNumber(safeTotals.parallel.total_cod || 0)}</h3>
                        <p class="small mb-0">${formatWeeks(safeTotals.parallel.duration_p85)}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h6 class="text-muted">Sequencial (não otimizado)</h6>
                        <h3 class="text-danger">R$ ${formatNumber(safeTotals.sequential_unoptimized.total_cod || 0)}</h3>
                        <p class="small mb-0">${formatWeeks(safeTotals.sequential_unoptimized.duration_p85)}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center border-success">
                    <div class="card-body">
                        <h6 class="text-muted">Sequencial (WSJF otimizado)</h6>
                        <h3 class="text-success">R$ ${formatNumber(safeTotals.sequential_optimized.total_cod || 0)}</h3>
                        <p class="small mb-0">${formatWeeks(safeTotals.sequential_optimized.duration_p85)}</p>
                        ${hasPositiveSavings
                            ? '<span class="badge bg-success mt-2">Recomendado</span>'
                            : hasNegativeSavings
                                ? '<span class="badge bg-danger mt-2">Não recomendado</span>'
                                : '<span class="badge bg-secondary mt-2">Sem ganho</span>'}
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
                            ${safeOptimization.optimized_sequence.map((projectId, index) => {
                                const ranking = safeOptimization.project_rankings[projectId];
                                if (!ranking) return '';
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
                        if (!strategy) return '';
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
                        ${riskAssessment.high_cod_projects.length > 0 ? `
                            <ul class="list-unstyled">
                                ${riskAssessment.high_cod_projects.map(pid => {
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
                        ${riskAssessment.critical_deadline_projects.length > 0 ? `
                            <ul class="list-unstyled">
                                ${riskAssessment.critical_deadline_projects.map(pid => {
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

/**
 * Export portfolio to Excel
 */
function exportToExcel() {
    if (!currentPortfolioId) {
        alert('Por favor, selecione um portfolio primeiro');
        return;
    }

    // Open export endpoint in new tab
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

    // Open export endpoint in new tab
    window.open(`/api/portfolios/${currentPortfolioId}/export/pdf`, '_blank');
}

// ============================================================================
// DEPENDENCY VISUALIZATION
// ============================================================================

let dependencyVisualizer = null;

/**
 * Initialize dependency visualization
 */
async function initializeDependencyVisualization(portfolioId) {
    try {
        // Fetch portfolio projects
        const response = await fetch(`/api/portfolios/${portfolioId}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');

        const portfolioProjects = await response.json();

        // Extract projects and dependencies
        const projects = portfolioProjects.map(pp => ({
            id: pp.project_id,
            name: pp.project_name,
            priority: pp.portfolio_priority || 3,
            status: pp.status || 'active',
            backlog: pp.backlog
        }));

        const dependencies = [];
        portfolioProjects.forEach(pp => {
            if (pp.depends_on && pp.depends_on.length > 0) {
                pp.depends_on.forEach(targetId => {
                    const targetProject = portfolioProjects.find(p => p.project_id === targetId);
                    dependencies.push({
                        source_id: pp.project_id,
                        target_id: targetId,
                        source_name: pp.project_name,
                        target_name: targetProject?.project_name || `Project ${targetId}`,
                        name: `${pp.project_name} → ${targetProject?.project_name || targetId}`,
                        criticality: 'HIGH'
                    });
                });
            }
        });

        // Initialize visualizer
        if (!dependencyVisualizer) {
            dependencyVisualizer = new DependencyVisualizer('dependencyNetwork');
        }

        dependencyVisualizer.initialize(projects, dependencies, portfolioId);

        // Setup callbacks
        dependencyVisualizer.onDependencyAdded = async (sourceId, targetId) => {
            await addDependency(portfolioId, sourceId, targetId);
        };

        dependencyVisualizer.onDependencyRemoved = async (sourceId, targetId) => {
            await removeDependency(portfolioId, sourceId, targetId);
        };

        dependencyVisualizer.onProjectClicked = (projectId) => {
            console.log('Project clicked:', projectId);
            // Could open project details modal here
        };

        // Fit to view
        setTimeout(() => {
            dependencyVisualizer.fit();
        }, 100);

    } catch (error) {
        console.error('Error initializing dependency visualization:', error);
        showError('Erro ao inicializar visualização de dependências');
    }
}

/**
 * Add a dependency between projects
 */
async function addDependency(portfolioId, sourceId, targetId) {
    try {
        const response = await fetch(`/api/portfolios/${portfolioId}/projects/${sourceId}/dependencies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_project_id: targetId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add dependency');
        }

        showSuccess('Dependência adicionada com sucesso!');

        // Reload portfolio projects
        await loadPortfolioProjects(portfolioId);

    } catch (error) {
        console.error('Error adding dependency:', error);
        showError(error.message);

        // Refresh visualization to remove the invalid edge
        await refreshDependencyVisualization();
    }
}

/**
 * Remove a dependency between projects
 */
async function removeDependency(portfolioId, sourceId, targetId) {
    try {
        const response = await fetch(`/api/portfolios/${portfolioId}/projects/${sourceId}/dependencies/${targetId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to remove dependency');
        }

        showSuccess('Dependência removida com sucesso!');

        // Reload portfolio projects
        await loadPortfolioProjects(portfolioId);

    } catch (error) {
        console.error('Error removing dependency:', error);
        showError(error.message);
    }
}

/**
 * Refresh dependency visualization
 */
async function refreshDependencyVisualization() {
    if (currentPortfolioId) {
        await initializeDependencyVisualization(currentPortfolioId);
    }
}

/**
 * Fit dependency network to view
 */
function fitDependencyNetwork() {
    if (dependencyVisualizer) {
        dependencyVisualizer.fit();
    }
}

// Update the selectPortfolio function to initialize dependency viz
const originalSelectPortfolio = selectPortfolio;
selectPortfolio = async function(portfolioId) {
    await originalSelectPortfolio(portfolioId);

    // Initialize dependency visualization
    await initializeDependencyVisualization(portfolioId);
};
