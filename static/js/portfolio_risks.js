/**
 * Portfolio Risk Management JavaScript
 * Handles risk CRUD, heatmap visualization, and analysis
 */

let currentPortfolioId = null;
let currentRisks = [];
let portfolioProjects = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolios();
    initializeTooltips();
    setupRiskCalculator();
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
 * Setup automatic risk score calculation
 */
function setupRiskCalculator() {
    const probInput = document.getElementById('riskProbability');
    const impactInput = document.getElementById('riskImpact');
    const scoreInput = document.getElementById('riskScore');

    function updateScore() {
        const prob = parseInt(probInput.value) || 0;
        const impact = parseInt(impactInput.value) || 0;
        const score = prob * impact;
        scoreInput.value = score;

        // Update score color
        scoreInput.className = 'form-control';
        if (score >= 20) {
            scoreInput.classList.add('risk-critical');
        } else if (score >= 15) {
            scoreInput.classList.add('risk-high');
        } else if (score >= 10) {
            scoreInput.classList.add('risk-medium');
        } else if (score >= 5) {
            scoreInput.classList.add('risk-low');
        } else {
            scoreInput.classList.add('risk-very-low');
        }
    }

    probInput.addEventListener('input', updateScore);
    impactInput.addEventListener('input', updateScore);
    updateScore();
}

/**
 * Load all portfolios
 */
async function loadPortfolios() {
    try {
        const response = await fetch('/api/portfolios');
        if (!response.ok) throw new Error('Failed to load portfolios');

        const portfolios = await response.json();
        const select = document.getElementById('portfolioSelect');

        portfolios.forEach(portfolio => {
            const option = document.createElement('option');
            option.value = portfolio.id;
            option.textContent = portfolio.name;
            select.appendChild(option);
        });

        select.addEventListener('change', (e) => {
            if (e.target.value) {
                selectPortfolio(parseInt(e.target.value));
            }
        });

    } catch (error) {
        console.error('Error loading portfolios:', error);
        alert('Error loading portfolios: ' + error.message);
    }
}

/**
 * Select a portfolio and load its risks
 */
async function selectPortfolio(portfolioId) {
    currentPortfolioId = portfolioId;

    // Show portfolio detail, hide empty state
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('portfolioDetail').style.display = 'block';

    // Load risks and analysis
    await Promise.all([
        loadRisks(),
        loadRiskAnalysis(),
        loadPortfolioProjects()
    ]);
}

/**
 * Load all risks for current portfolio
 */
async function loadRisks() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/risks`);
        if (!response.ok) throw new Error('Failed to load risks');

        currentRisks = await response.json();
        renderRisksList(currentRisks);
        document.getElementById('riskCount').textContent = currentRisks.length;

    } catch (error) {
        console.error('Error loading risks:', error);
        alert('Error loading risks: ' + error.message);
    }
}

/**
 * Load portfolio projects for the dropdown
 */
async function loadPortfolioProjects() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');

        portfolioProjects = await response.json();

        // Populate project dropdown in modal
        const select = document.getElementById('riskProject');
        select.innerHTML = '<option value="">No specific project</option>';

        portfolioProjects.forEach(pp => {
            const option = document.createElement('option');
            option.value = pp.project.id;
            option.textContent = pp.project.name;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

/**
 * Load and display risk analysis
 */
async function loadRiskAnalysis() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/risks/analysis`);
        if (!response.ok) throw new Error('Failed to load analysis');

        const analysis = await response.json();

        // Render components
        renderRiskSummary(analysis.metrics);
        renderRiskHeatmap(analysis.heatmap);
        renderAlerts(analysis.alerts);

        // Show cards
        document.getElementById('riskSummaryCard').style.display = 'block';
        if (analysis.alerts && analysis.alerts.length > 0) {
            document.getElementById('alertsCard').style.display = 'block';
        }

    } catch (error) {
        console.error('Error loading risk analysis:', error);
    }
}

/**
 * Render risk summary metrics
 */
function renderRiskSummary(metrics) {
    const html = `
        <div class="mb-3">
            <strong>Total Risks:</strong> ${metrics.total_risks}
        </div>

        <div class="mb-3">
            <small class="text-muted d-block mb-1">By Level:</small>
            <div class="risk-badge risk-critical me-1">${metrics.by_level.critical}</div>
            <div class="risk-badge risk-high me-1">${metrics.by_level.high}</div>
            <div class="risk-badge risk-medium me-1">${metrics.by_level.medium}</div>
            <div class="risk-badge risk-low me-1">${metrics.by_level.low}</div>
            <div class="risk-badge risk-very-low">${metrics.by_level.very_low}</div>
        </div>

        <div class="mb-3">
            <small class="text-muted d-block mb-1">By Status:</small>
            <div><span class="badge bg-warning text-dark">Active: ${metrics.by_status.active}</span></div>
            <div><span class="badge bg-info text-dark">Mitigated: ${metrics.by_status.mitigated}</span></div>
            <div><span class="badge bg-secondary">Accepted: ${metrics.by_status.accepted}</span></div>
            <div><span class="badge bg-danger">Occurred: ${metrics.by_status.occurred}</span></div>
            <div><span class="badge bg-success">Closed: ${metrics.by_status.closed}</span></div>
        </div>

        ${metrics.costs.expected_monetary_value > 0 ? `
        <div class="mb-2">
            <small class="text-muted">Expected Risk Cost (EMV):</small><br>
            <strong class="text-danger">R$ ${formatNumber(metrics.costs.expected_monetary_value)}</strong>
        </div>
        ` : ''}

        ${metrics.scores.average > 0 ? `
        <div class="mb-2">
            <small class="text-muted">Average Risk Score:</small><br>
            <strong>${metrics.scores.average.toFixed(1)}</strong> / 25
        </div>
        ` : ''}
    `;

    document.getElementById('riskSummary').innerHTML = html;
}

/**
 * Render risk heatmap (5x5 probability x impact matrix)
 */
function renderRiskHeatmap(heatmap) {
    const matrix = heatmap.matrix;

    let html = '<table class="table-borderless mx-auto">';

    // Header row with impact labels
    html += '<tr><td></td>';
    for (let impact = 5; impact >= 1; impact--) {
        html += `<td class="matrix-label">I=${impact}</td>`;
    }
    html += '</tr>';

    // Matrix rows (probability from 5 to 1)
    for (let prob = 5; prob >= 1; prob--) {
        html += '<tr>';
        html += `<td class="matrix-label">P=${prob}</td>`;

        for (let impact = 5; impact >= 1; impact--) {
            const count = matrix[prob - 1][impact - 1] || 0;
            const score = prob * impact;
            const riskClass = getRiskClass(score);
            const cellKey = `${prob},${impact}`;

            html += `
                <td>
                    <div class="risk-matrix-cell ${riskClass}" onclick="showCellRisks(${prob}, ${impact})">
                        <div class="count">${count}</div>
                        <div class="label">Score: ${score}</div>
                    </div>
                </td>
            `;
        }

        html += '</tr>';
    }

    html += '</table>';

    document.getElementById('riskHeatmap').innerHTML = html;
}

/**
 * Get CSS class for risk level based on score
 */
function getRiskClass(score) {
    if (score >= 20) return 'risk-critical';
    if (score >= 15) return 'risk-high';
    if (score >= 10) return 'risk-medium';
    if (score >= 5) return 'risk-low';
    return 'risk-very-low';
}

/**
 * Show risks for a specific heatmap cell
 */
function showCellRisks(probability, impact) {
    const cellRisks = currentRisks.filter(r =>
        r.probability === probability && r.impact === impact
    );

    if (cellRisks.length === 0) {
        alert(`No risks with Probability=${probability} and Impact=${impact}`);
        return;
    }

    const riskNames = cellRisks.map(r => `• ${r.risk_title}`).join('\n');
    alert(`Risks (P=${probability}, I=${impact}):\n\n${riskNames}`);
}

/**
 * Render alerts
 */
function renderAlerts(alerts) {
    if (!alerts || alerts.length === 0) {
        document.getElementById('alertsCard').style.display = 'none';
        return;
    }

    let html = '';
    alerts.forEach(alert => {
        const alertClass = alert.severity === 'critical' ? 'danger' :
                          alert.severity === 'high' ? 'warning' : 'info';

        html += `
            <div class="alert alert-${alertClass} mb-2 p-2">
                <div class="d-flex align-items-start">
                    <i class="fas fa-${alert.icon || 'info-circle'} me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <strong>${alert.title}</strong>
                        <div class="small">${alert.message}</div>
                        ${alert.action ? `<div class="small text-muted mt-1">→ ${alert.action}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    });

    document.getElementById('alertsList').innerHTML = html;
}

/**
 * Render risks list table
 */
function renderRisksList(risks) {
    const tbody = document.getElementById('risksList');

    if (risks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">
                    No risks tracked yet. Click "Add Risk" to get started.
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    risks.forEach(risk => {
        const riskClass = getRiskClass(risk.risk_score);

        html += `
            <tr>
                <td>
                    <strong>${risk.risk_title}</strong>
                    ${risk.risk_description ? `<br><small class="text-muted">${truncate(risk.risk_description, 60)}</small>` : ''}
                </td>
                <td><span class="badge bg-secondary">${risk.risk_category}</span></td>
                <td>${risk.project_name || '<span class="text-muted">—</span>'}</td>
                <td>${risk.probability}</td>
                <td>${risk.impact}</td>
                <td><strong>${risk.risk_score}</strong></td>
                <td><span class="risk-badge ${riskClass}">${risk.risk_level}</span></td>
                <td><span class="badge bg-info text-dark">${risk.status}</span></td>
                <td>${risk.owner || '<span class="text-muted">—</span>'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editRisk(${risk.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRisk(${risk.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

/**
 * Show add risk modal
 */
function showAddRiskModal() {
    document.getElementById('riskModalTitle').textContent = 'Add Risk';
    document.getElementById('riskId').value = '';
    document.getElementById('riskTitle').value = '';
    document.getElementById('riskDescription').value = '';
    document.getElementById('riskCategory').value = 'general';
    document.getElementById('riskProbability').value = '3';
    document.getElementById('riskImpact').value = '3';
    document.getElementById('riskStatus').value = 'identified';
    document.getElementById('riskOwner').value = '';
    document.getElementById('riskCost').value = '';
    document.getElementById('mitigationCost').value = '';
    document.getElementById('riskProject').value = '';
    document.getElementById('mitigationPlan').value = '';
    document.getElementById('contingencyPlan').value = '';

    // Trigger score calculation
    document.getElementById('riskProbability').dispatchEvent(new Event('input'));

    const modal = new bootstrap.Modal(document.getElementById('riskModal'));
    modal.show();
}

/**
 * Edit existing risk
 */
async function editRisk(riskId) {
    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/risks/${riskId}`);
        if (!response.ok) throw new Error('Failed to load risk');

        const risk = await response.json();

        document.getElementById('riskModalTitle').textContent = 'Edit Risk';
        document.getElementById('riskId').value = risk.id;
        document.getElementById('riskTitle').value = risk.risk_title;
        document.getElementById('riskDescription').value = risk.risk_description || '';
        document.getElementById('riskCategory').value = risk.risk_category;
        document.getElementById('riskProbability').value = risk.probability;
        document.getElementById('riskImpact').value = risk.impact;
        document.getElementById('riskStatus').value = risk.status;
        document.getElementById('riskOwner').value = risk.owner || '';
        document.getElementById('riskCost').value = risk.estimated_cost_if_occurs || '';
        document.getElementById('mitigationCost').value = risk.mitigation_cost || '';
        document.getElementById('riskProject').value = risk.project_id || '';
        document.getElementById('mitigationPlan').value = risk.mitigation_plan || '';
        document.getElementById('contingencyPlan').value = risk.contingency_plan || '';

        // Trigger score calculation
        document.getElementById('riskProbability').dispatchEvent(new Event('input'));

        const modal = new bootstrap.Modal(document.getElementById('riskModal'));
        modal.show();

    } catch (error) {
        console.error('Error loading risk:', error);
        alert('Error loading risk: ' + error.message);
    }
}

/**
 * Save risk (create or update)
 */
async function saveRisk() {
    const riskId = document.getElementById('riskId').value;
    const riskTitle = document.getElementById('riskTitle').value.trim();

    if (!riskTitle) {
        alert('Risk title is required');
        return;
    }

    const data = {
        risk_title: riskTitle,
        risk_description: document.getElementById('riskDescription').value.trim(),
        risk_category: document.getElementById('riskCategory').value,
        probability: parseInt(document.getElementById('riskProbability').value),
        impact: parseInt(document.getElementById('riskImpact').value),
        status: document.getElementById('riskStatus').value,
        owner: document.getElementById('riskOwner').value.trim(),
        estimated_cost_if_occurs: parseFloat(document.getElementById('riskCost').value) || null,
        mitigation_cost: parseFloat(document.getElementById('mitigationCost').value) || null,
        project_id: parseInt(document.getElementById('riskProject').value) || null,
        mitigation_plan: document.getElementById('mitigationPlan').value.trim(),
        contingency_plan: document.getElementById('contingencyPlan').value.trim()
    };

    try {
        let response;
        if (riskId) {
            // Update existing risk
            response = await fetch(`/api/portfolios/${currentPortfolioId}/risks/${riskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            // Create new risk
            response = await fetch(`/api/portfolios/${currentPortfolioId}/risks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save risk');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('riskModal'));
        modal.hide();

        // Reload data
        await selectPortfolio(currentPortfolioId);

        alert(riskId ? 'Risk updated successfully!' : 'Risk created successfully!');

    } catch (error) {
        console.error('Error saving risk:', error);
        alert('Error saving risk: ' + error.message);
    }
}

/**
 * Delete risk
 */
async function deleteRisk(riskId) {
    if (!confirm('Are you sure you want to delete this risk?')) {
        return;
    }

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/risks/${riskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete risk');

        // Reload data
        await selectPortfolio(currentPortfolioId);

        alert('Risk deleted successfully!');

    } catch (error) {
        console.error('Error deleting risk:', error);
        alert('Error deleting risk: ' + error.message);
    }
}

/**
 * Suggest risks based on portfolio data
 */
async function suggestRisks() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/risks/suggest`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Failed to suggest risks');

        const result = await response.json();

        if (result.suggested_risks.length === 0) {
            alert('No risk suggestions at this time. Portfolio health looks good!');
            return;
        }

        // Show suggestions
        let message = 'AI-Suggested Risks:\n\n';
        result.suggested_risks.forEach((risk, index) => {
            message += `${index + 1}. ${risk.risk_title}\n`;
            message += `   Category: ${risk.risk_category}\n`;
            message += `   P=${risk.probability} × I=${risk.impact} = ${risk.probability * risk.impact}\n`;
            if (risk.affected_projects) {
                message += `   Projects: ${risk.affected_projects.slice(0, 3).join(', ')}\n`;
            }
            message += '\n';
        });

        message += '\nWould you like to add these risks to track?';

        if (confirm(message)) {
            // Add suggested risks
            for (const risk of result.suggested_risks) {
                await fetch(`/api/portfolios/${currentPortfolioId}/risks`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        risk_title: risk.risk_title,
                        risk_description: risk.risk_description,
                        risk_category: risk.risk_category,
                        probability: risk.probability,
                        impact: risk.impact,
                        status: 'identified'
                    })
                });
            }

            // Reload data
            await selectPortfolio(currentPortfolioId);
            alert('Suggested risks added successfully!');
        }

    } catch (error) {
        console.error('Error suggesting risks:', error);
        alert('Error suggesting risks: ' + error.message);
    }
}

/**
 * Utility: Format number with thousands separator
 */
function formatNumber(num) {
    return num.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

/**
 * Utility: Truncate string
 */
function truncate(str, maxLength) {
    if (!str) return '';
    return str.length > maxLength ? str.substring(0, maxLength) + '...' : str;
}
