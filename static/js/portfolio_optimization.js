/**
 * Portfolio Optimization JavaScript
 * Handles optimization, scenarios, and Pareto frontier visualization
 */

let currentPortfolioId = null;
let currentPortfolio = null;
let scenarios = [];
let paretoChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolios();
});

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
 * Select a portfolio
 */
async function selectPortfolio(portfolioId) {
    currentPortfolioId = portfolioId;

    try {
        const response = await fetch(`/api/portfolios/${portfolioId}`);
        if (!response.ok) throw new Error('Failed to load portfolio');

        currentPortfolio = await response.json();

        // Update constraints with portfolio defaults
        document.getElementById('maxBudget').value = currentPortfolio.total_budget || 1000000;
        document.getElementById('maxCapacity').value = currentPortfolio.total_capacity || 10;

        // Show panels
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('constraintsPanel').style.display = 'block';

        // Clear previous results
        scenarios = [];

    } catch (error) {
        console.error('Error loading portfolio:', error);
        alert('Error loading portfolio: ' + error.message);
    }
}

/**
 * Run optimization
 */
async function runOptimization() {
    if (!currentPortfolioId) return;

    const maxBudget = parseFloat(document.getElementById('maxBudget').value);
    const maxCapacity = parseFloat(document.getElementById('maxCapacity').value);
    const objective = document.getElementById('objective').value;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                max_budget: maxBudget,
                max_capacity: maxCapacity,
                objective: objective
            })
        });

        if (!response.ok) {
            const error = await response.json();

            // Handle missing PuLP dependency
            if (error.error_type === 'dependency_missing') {
                alert(
                    'Optimization Library Not Installed\n\n' +
                    error.hint + '\n\n' +
                    error.action
                );
                return;
            }

            throw new Error(error.error || 'Optimization failed');
        }

        const result = await response.json();
        displayOptimizationResults(result);

    } catch (error) {
        console.error('Error running optimization:', error);
        alert('Error running optimization: ' + error.message);
    }
}

/**
 * Display optimization results
 */
function displayOptimizationResults(result) {
    // Show results panel
    document.getElementById('resultsPanel').style.display = 'block';

    // Update metrics
    document.getElementById('projectsSelected').textContent = result.metrics.projects_included;
    document.getElementById('totalValue').textContent = result.metrics.total_value.toFixed(0);
    document.getElementById('totalCost').textContent = formatNumber(result.metrics.total_cost);
    document.getElementById('totalCapacity').textContent = result.metrics.total_capacity.toFixed(1);

    // Update utilization bars
    const budgetPct = result.utilization.budget.percentage.toFixed(1);
    const capacityPct = result.utilization.capacity.percentage.toFixed(1);

    const budgetBar = document.getElementById('budgetUtilization');
    budgetBar.style.width = Math.min(budgetPct, 100) + '%';
    budgetBar.textContent = budgetPct + '%';

    const capacityBar = document.getElementById('capacityUtilization');
    capacityBar.style.width = Math.min(capacityPct, 100) + '%';
    capacityBar.textContent = capacityPct + '%';

    // Display selected projects
    let selectedHtml = '<div class="table-responsive"><table class="table table-sm">';
    selectedHtml += '<thead><tr><th>Project</th><th>Value</th><th>Cost</th><th>Capacity</th><th>WSJF</th></tr></thead><tbody>';

    result.selected_projects.forEach(project => {
        selectedHtml += `
            <tr>
                <td><strong>${project.name}</strong></td>
                <td>${project.business_value}</td>
                <td>R$ ${formatNumber(project.budget_allocated)}</td>
                <td>${project.capacity_allocated.toFixed(1)} FTE</td>
                <td>${project.wsjf_score ? project.wsjf_score.toFixed(2) : 'N/A'}</td>
            </tr>
        `;
    });
    selectedHtml += '</tbody></table></div>';
    document.getElementById('selectedProjects').innerHTML = selectedHtml;

    // Display excluded projects
    if (result.excluded_projects.length > 0) {
        let excludedHtml = '<div class="table-responsive"><table class="table table-sm">';
        excludedHtml += '<thead><tr><th>Project</th><th>Value</th><th>Risk</th><th>Reason</th></tr></thead><tbody>';

        result.excluded_projects.forEach(project => {
            excludedHtml += `
                <tr>
                    <td>${project.name}</td>
                    <td>${project.business_value}</td>
                    <td><span class="badge bg-secondary">${project.risk_level}</span></td>
                    <td class="text-muted">Constraint limits</td>
                </tr>
            `;
        });
        excludedHtml += '</tbody></table></div>';
        document.getElementById('excludedProjects').innerHTML = excludedHtml;
    } else {
        document.getElementById('excludedProjects').innerHTML = '<p class="text-muted">All projects selected</p>';
    }

    // Display recommendations
    if (result.recommendations && result.recommendations.length > 0) {
        let recHtml = '';
        result.recommendations.forEach(rec => {
            recHtml += `<div class="recommendation-item"><i class="fas fa-lightbulb me-2"></i>${rec}</div>`;
        });
        document.getElementById('recommendations').innerHTML = recHtml;
        document.getElementById('recommendationsCard').style.display = 'block';
    } else {
        document.getElementById('recommendationsCard').style.display = 'none';
    }

    // Show optimization status
    if (result.optimization.status !== 'Optimal') {
        alert('Optimization Status: ' + result.optimization.status + '\n\nConstraints may be too restrictive.');
    }
}

/**
 * Show scenario modal
 */
function showScenarioModal() {
    if (!currentPortfolio) {
        alert('Please select a portfolio first');
        return;
    }

    // Prefill with current portfolio values
    document.getElementById('scenarioName').value = '';
    document.getElementById('scenarioDescription').value = '';
    document.getElementById('scenarioBudget').value = currentPortfolio.total_budget || 1000000;
    document.getElementById('scenarioCapacity').value = currentPortfolio.total_capacity || 10;

    const modal = new bootstrap.Modal(document.getElementById('scenarioModal'));
    modal.show();
}

/**
 * Add scenario to list
 */
function addScenario() {
    const name = document.getElementById('scenarioName').value.trim();
    const description = document.getElementById('scenarioDescription').value.trim();
    const budget = parseFloat(document.getElementById('scenarioBudget').value);
    const capacity = parseFloat(document.getElementById('scenarioCapacity').value);

    if (!name) {
        alert('Scenario name is required');
        return;
    }

    scenarios.push({
        name: name,
        description: description,
        max_budget: budget,
        max_capacity: capacity
    });

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('scenarioModal'));
    modal.hide();

    // Update scenarios list
    renderScenariosList();

    alert(`Scenario "${name}" added. Click "Compare Scenarios" to run comparison.`);
}

/**
 * Render scenarios list
 */
function renderScenariosList() {
    if (scenarios.length === 0) {
        document.getElementById('scenariosList').innerHTML = '<p class="text-muted">No scenarios added yet. Click "Add Scenario" to get started.</p>';
        return;
    }

    let html = '';
    scenarios.forEach((scenario, index) => {
        html += `
            <div class="scenario-card">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5>${scenario.name}</h5>
                        <p class="text-muted mb-2">${scenario.description || 'No description'}</p>
                        <div class="small">
                            <span class="me-3"><i class="fas fa-dollar-sign me-1"></i>R$ ${formatNumber(scenario.max_budget)}</span>
                            <span><i class="fas fa-users me-1"></i>${scenario.max_capacity} FTE</span>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeScenario(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });

    document.getElementById('scenariosList').innerHTML = html;
}

/**
 * Remove scenario
 */
function removeScenario(index) {
    scenarios.splice(index, 1);
    renderScenariosList();
}

/**
 * Compare scenarios
 */
async function compareScenarios() {
    if (!currentPortfolioId) return;

    if (scenarios.length === 0) {
        alert('Please add at least one scenario to compare');
        return;
    }

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/scenarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scenarios: scenarios
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Scenario comparison failed');
        }

        const result = await response.json();
        displayScenarioComparison(result);

    } catch (error) {
        console.error('Error comparing scenarios:', error);
        alert('Error comparing scenarios: ' + error.message);
    }
}

/**
 * Display scenario comparison
 */
function displayScenarioComparison(result) {
    let html = '<div class="card mt-4"><div class="card-header"><i class="fas fa-balance-scale"></i> Scenario Comparison</div><div class="card-body">';

    // Best scenario highlight
    if (result.best_scenario) {
        html += `<div class="alert alert-success"><i class="fas fa-trophy me-2"></i><strong>Best Scenario:</strong> ${result.best_scenario}</div>`;
    }

    // Comparison table
    html += '<div class="table-responsive"><table class="table table-hover">';
    html += '<thead><tr><th>Scenario</th><th>Projects</th><th>Total Value</th><th>Total Cost</th><th>Capacity</th></tr></thead><tbody>';

    result.scenarios.forEach(scenario => {
        const isBest = scenario.scenario_name === result.best_scenario;
        const rowClass = isBest ? 'table-success' : '';

        html += `
            <tr class="${rowClass}">
                <td>
                    <strong>${scenario.scenario_name}</strong>
                    ${isBest ? '<span class="badge bg-success ms-2">Best</span>' : ''}
                    <br><small class="text-muted">${scenario.description}</small>
                </td>
                <td>${scenario.projects_selected}</td>
                <td><strong>${scenario.total_value}</strong></td>
                <td>R$ ${formatNumber(scenario.total_cost)}</td>
                <td>${scenario.total_capacity.toFixed(1)} FTE</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';

    // Value range
    if (result.comparison && result.comparison.value_range) {
        html += `
            <div class="mt-3">
                <h6>Value Range:</h6>
                <p>Min: ${result.comparison.value_range.min} | Max: ${result.comparison.value_range.max} | Spread: ${result.comparison.value_range.spread}</p>
            </div>
        `;
    }

    html += '</div></div>';
    document.getElementById('scenarioComparison').innerHTML = html;
    document.getElementById('scenarioComparison').style.display = 'block';
}

/**
 * Generate Pareto frontier
 */
async function generatePareto() {
    if (!currentPortfolioId) return;

    try {
        const response = await fetch(`/api/portfolios/${currentPortfolioId}/pareto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                axis_x: 'cost',
                axis_y: 'value',
                points: 10
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Pareto generation failed');
        }

        const result = await response.json();
        displayParetoFrontier(result);

    } catch (error) {
        console.error('Error generating Pareto frontier:', error);
        alert('Error generating Pareto frontier: ' + error.message);
    }
}

/**
 * Display Pareto frontier chart
 */
function displayParetoFrontier(result) {
    const ctx = document.getElementById('paretoChart');

    // Destroy previous chart if exists
    if (paretoChart) {
        paretoChart.destroy();
    }

    // Prepare data
    const data = {
        datasets: [{
            label: 'Pareto Frontier (Optimal Trade-offs)',
            data: result.pareto_frontier.map(point => ({
                x: point.x,
                y: point.y,
                projects_count: point.projects_count
            })),
            backgroundColor: 'rgba(88, 166, 255, 0.6)',
            borderColor: 'rgba(88, 166, 255, 1)',
            borderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
        }]
    };

    // Create chart
    paretoChart = new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Cost vs. Value Trade-off Analysis',
                    color: '#c9d1d9',
                    font: { size: 16 }
                },
                legend: {
                    labels: { color: '#c9d1d9' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Cost: R$ ${formatNumber(point.x)}`,
                                `Value: ${point.y}`,
                                `Projects: ${point.projects_count}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Total Cost (R$)',
                        color: '#c9d1d9'
                    },
                    ticks: {
                        color: '#c9d1d9',
                        callback: function(value) {
                            return 'R$ ' + (value / 1000) + 'k';
                        }
                    },
                    grid: { color: '#30363d' }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Total Business Value',
                        color: '#c9d1d9'
                    },
                    ticks: { color: '#c9d1d9' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

/**
 * Utility: Format number with thousands separator
 */
function formatNumber(num) {
    return num.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
