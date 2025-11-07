/**
 * Portfolio Dashboard JavaScript
 * Integrated dashboard with metrics, alerts, and visualizations
 */

let currentPortfolioId = null;
let resourceChart = null;
let budgetChart = null;

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
 * Load dashboard data for selected portfolio
 */
async function loadDashboard() {
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
        renderDashboard(data);

        document.getElementById('dashboardContent').style.display = 'block';
        document.getElementById('emptyState').style.display = 'none';

    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Erro ao carregar dashboard: ' + error.message);
    }
}

/**
 * Render complete dashboard
 */
function renderDashboard(data) {
    // Summary metrics
    document.getElementById('totalProjects').textContent = data.summary.total_projects;
    document.getElementById('activeProjects').textContent = data.summary.active_projects;
    document.getElementById('avgCompletion').textContent = data.summary.avg_completion_pct.toFixed(1);
    document.getElementById('projectedDuration').textContent = data.timeline.projected_duration_weeks.toFixed(1);

    // Health score
    renderHealthScore(data.health);

    // Alerts
    renderAlerts(data.alerts);

    // Capacity
    renderCapacity(data.health, data.resource_timeline);

    // Budget
    renderBudget(data.health);

    // Projects list
    renderProjects(data.projects);

    // Timeline
    renderTimeline(data.timeline_events);
}

/**
 * Render health score
 */
function renderHealthScore(health) {
    const score = health.overall_score;
    const scoreEl = document.getElementById('healthScore');

    scoreEl.textContent = score.toFixed(0);

    // Set color based on score
    scoreEl.className = 'health-score';
    if (score >= 80) {
        scoreEl.classList.add('health-excellent');
    } else if (score >= 60) {
        scoreEl.classList.add('health-good');
    } else if (score >= 40) {
        scoreEl.classList.add('health-warning');
    } else {
        scoreEl.classList.add('health-critical');
    }

    document.getElementById('onTrackCount').textContent = health.on_track_count;
    document.getElementById('atRiskCount').textContent = health.at_risk_count;
    document.getElementById('criticalCount').textContent = health.critical_count;
}

/**
 * Render alerts
 */
function renderAlerts(alerts) {
    const container = document.getElementById('alertsList');

    if (alerts.length === 0) {
        container.innerHTML = '<p class="text-muted">✅ Nenhum alerta. Portfolio saudável!</p>';
        return;
    }

    container.innerHTML = alerts.map(alert => {
        const severityClass = `alert-${alert.severity}`;
        const icon = alert.severity === 'critical' ? 'exclamation-circle' :
                    alert.severity === 'warning' ? 'exclamation-triangle' :
                    'info-circle';

        return `
            <div class="alert-card ${severityClass}">
                <div class="d-flex align-items-start">
                    <i class="fas fa-${icon} fa-lg me-3 mt-1"></i>
                    <div class="flex-grow-1">
                        <strong>${alert.title}</strong>
                        <p class="mb-0 small">${alert.message}</p>
                        ${alert.project_name ? `<small class="text-muted">Projeto: ${alert.project_name}</small>` : ''}
                    </div>
                    ${alert.action_required ? '<span class="badge bg-danger">Ação Requerida</span>' : ''}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render capacity allocation
 */
function renderCapacity(health, resourceTimeline) {
    const utilization = health.capacity_utilization;

    document.getElementById('capacityUtilization').textContent = utilization.toFixed(1);
    document.getElementById('capacityAllocated').textContent = health.capacity_allocated.toFixed(1);
    document.getElementById('capacityTotal').textContent = health.capacity_available.toFixed(1);

    const bar = document.getElementById('capacityBar');
    bar.style.width = Math.min(utilization, 100) + '%';

    // Color based on utilization
    bar.className = 'progress-bar';
    if (utilization > 100) {
        bar.classList.add('bg-danger');
    } else if (utilization > 90) {
        bar.classList.add('bg-warning');
    } else {
        bar.classList.add('bg-success');
    }

    // Render resource chart
    if (resourceTimeline && resourceTimeline.length > 0) {
        renderResourceChart(resourceTimeline);
    }
}

/**
 * Render resource allocation chart
 */
function renderResourceChart(timeline) {
    const ctx = document.getElementById('resourceChart');

    // Destroy existing chart
    if (resourceChart) {
        resourceChart.destroy();
    }

    resourceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.map(t => t.period),
            datasets: [
                {
                    label: 'Capacidade Alocada',
                    data: timeline.map(t => t.allocated_capacity),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Capacidade Total',
                    data: timeline.map(t => t.total_capacity),
                    borderColor: '#28a745',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
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
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + ' FTE';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'FTE'
                    }
                }
            }
        }
    });
}

/**
 * Render budget allocation
 */
function renderBudget(health) {
    const section = document.getElementById('budgetSection');

    if (!health.budget_utilization) {
        section.innerHTML = '<p class="text-muted">Orçamento não configurado para este portfolio</p>';
        return;
    }

    const utilization = health.budget_utilization;
    const allocated = health.budget_allocated;
    const available = health.budget_available;

    section.innerHTML = `
        <strong>Utilização: ${utilization.toFixed(1)}%</strong>
        <div class="progress mt-2" style="height: 25px;">
            <div class="progress-bar ${utilization > 100 ? 'bg-danger' : utilization > 90 ? 'bg-warning' : 'bg-success'}"
                 style="width: ${Math.min(utilization, 100)}%"></div>
        </div>
        <small class="text-muted">
            R$ ${formatNumber(allocated)} de R$ ${formatNumber(available)} disponíveis
        </small>
    `;

    // Render budget chart
    renderBudgetChart(allocated, available);
}

/**
 * Render budget chart
 */
function renderBudgetChart(allocated, available) {
    const ctx = document.getElementById('budgetChart');

    if (budgetChart) {
        budgetChart.destroy();
    }

    const remaining = Math.max(0, available - allocated);

    budgetChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Alocado', 'Disponível'],
            datasets: [{
                data: [allocated, remaining],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(40, 167, 69, 0.8)'
                ],
                borderWidth: 2
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
                            const value = context.parsed;
                            const pct = (value / available * 100).toFixed(1);
                            return context.label + ': R$ ' + formatNumber(value) + ' (' + pct + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Render projects list
 */
function renderProjects(projects) {
    const container = document.getElementById('projectsList');

    if (projects.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhum projeto no portfolio</p>';
        return;
    }

    // Sort by WSJF or priority
    projects.sort((a, b) => {
        if (a.wsjf_score && b.wsjf_score) {
            return b.wsjf_score - a.wsjf_score;
        }
        return a.priority - b.priority;
    });

    container.innerHTML = projects.map(p => {
        const statusBadge = p.on_track ?
            '<span class="badge bg-success">No Prazo</span>' :
            '<span class="badge bg-warning">Atrasado</span>';

        const riskBadge = {
            'low': '<span class="badge bg-success">Baixo</span>',
            'medium': '<span class="badge bg-warning">Médio</span>',
            'high': '<span class="badge bg-danger">Alto</span>',
            'critical': '<span class="badge bg-danger">Crítico</span>'
        }[p.risk_level] || '';

        return `
            <div class="project-row" onclick="goToProject(${p.project_id})">
                <div class="row align-items-center">
                    <div class="col-md-4">
                        <strong>${p.project_name}</strong>
                        <div class="small text-muted">
                            Status: ${p.status} | Prioridade: ${p.priority}
                        </div>
                    </div>
                    <div class="col-md-2">
                        ${statusBadge} ${riskBadge}
                    </div>
                    <div class="col-md-3">
                        <div class="small text-muted">Conclusão</div>
                        <div class="progress progress-bar-custom">
                            <div class="progress-bar bg-primary" style="width: ${p.completion_pct}%"></div>
                        </div>
                        <small>${p.completion_pct.toFixed(1)}%</small>
                    </div>
                    <div class="col-md-2 text-end">
                        <div class="small text-muted">Duração P85</div>
                        <strong>${p.estimated_duration_p85.toFixed(1)} sem</strong>
                    </div>
                    <div class="col-md-1 text-end">
                        ${p.wsjf_score ? `<span class="badge bg-primary">WSJF: ${p.wsjf_score.toFixed(1)}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render timeline events
 */
function renderTimeline(events) {
    const container = document.getElementById('timelineEvents');

    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhum evento na timeline</p>';
        return;
    }

    // Limit to first 10 events
    const displayEvents = events.slice(0, 10);

    container.innerHTML = displayEvents.map(e => {
        const typeIcons = {
            'project_start': 'play-circle',
            'project_end': 'check-circle',
            'deadline': 'calendar-alt',
            'milestone': 'flag'
        };

        const icon = typeIcons[e.event_type] || 'circle';
        const cssClass = e.is_critical ? 'timeline-event critical' : 'timeline-event';

        return `
            <div class="${cssClass}">
                <i class="fas fa-${icon} me-2"></i>
                <strong>${e.date}</strong> - ${e.description}
                ${e.is_critical ? '<span class="badge bg-danger ms-2">Crítico</span>' : ''}
            </div>
        `;
    }).join('');

    if (events.length > 10) {
        container.innerHTML += `<p class="text-muted mt-2">... e mais ${events.length - 10} eventos</p>`;
    }
}

/**
 * Navigate to project detail
 */
function goToProject(projectId) {
    // For now, just log
    console.log('Navigate to project:', projectId);
    // Could redirect to project page: window.location.href = `/projects/${projectId}`;
}

/**
 * Format number with thousand separators
 */
function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(num);
}
