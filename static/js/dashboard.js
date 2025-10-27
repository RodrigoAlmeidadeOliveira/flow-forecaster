/**
 * Executive Dashboard Module
 * Populates KPIs and metrics for executive view
 */

let dashboardChart = null;

function parseThroughputSamples() {
    const raw = $('#tpSamples').val() || '';
    if (!raw.trim()) return [];
    return raw
        .split(/[\s,;]+/)
        .map(value => parseFloat(value.trim()))
        .filter(value => !Number.isNaN(value) && value >= 0);
}

function getCurrentBacklog() {
    const primary = parseInt($('#numberOfTasks').val(), 10);
    if (Number.isFinite(primary) && primary >= 0) {
        return primary;
    }
    const advancedBacklog = parseInt($('#backlog').val(), 10);
    return Number.isFinite(advancedBacklog) && advancedBacklog >= 0 ? advancedBacklog : 0;
}

// Refresh dashboard with current data
async function refreshDashboard() {
    updateCurrentKPIs();
    await loadHistoricalMetrics();
    updateProjectHealth();
}

// Update KPIs from current simulation
function updateCurrentKPIs() {
    // Get throughput from samples
    const samples = parseThroughputSamples();
    if (samples.length > 0) {
        const avgThroughput = samples.reduce((a, b) => a + b, 0) / samples.length;
        $('#kpi-throughput').text(avgThroughput.toFixed(1));
    } else {
        $('#kpi-throughput').text('-');
    }

    // Get backlog
    const backlog = getCurrentBacklog();
    $('#kpi-backlog').text(Number.isFinite(backlog) ? backlog : '-');

    // Get deadline probability from last results
    if (window.lastSimulationResults && window.lastSimulationResults.duration_p85) {
        const p85 = window.lastSimulationResults.duration_p85;
        $('#kpi-duration').text(p85.toFixed(1));

        // Calculate deadline success probability
        const deadlineDate = $('#deadlineDate').val();
        const startDate = $('#startDate').val();

        if (deadlineDate && startDate) {
            const weeksAvailable = calculateWeeksDiff(startDate, deadlineDate);

            // Rough probability calculation
            const p50 = window.lastSimulationResults.duration_p50 || p85 * 0.7;
            const p95 = window.lastSimulationResults.duration_p95 || p85 * 1.3;

            let probability = 0;
            if (weeksAvailable >= p95) probability = 95;
            else if (weeksAvailable >= p85) probability = 85;
            else if (weeksAvailable >= p50) probability = 50;
            else probability = Math.max(0, Math.round((weeksAvailable / p85) * 50));

            $('#kpi-deadline-prob').text(probability + '%');
        } else {
            $('#kpi-deadline-prob').text('-');
        }
    } else {
        $('#kpi-duration').text('-');
        $('#kpi-deadline-prob').text('-');
    }
}

// Load historical metrics from saved forecasts
async function loadHistoricalMetrics() {
    try {
        $('#dashboard-loading').show();

        const response = await fetch('/api/forecasts');
        if (!response.ok) throw new Error('Erro ao carregar análises');

        const forecasts = await response.json();

        $('#dashboard-loading').hide();

        if (forecasts.length === 0) {
            $('#dashboard-historical-list').html('<p class="text-muted">Nenhuma análise salva ainda.</p>');
            return;
        }

        // Display recent forecasts
        let html = '<div class="list-group">';
        forecasts.slice(0, 5).forEach(f => {
            const date = new Date(f.created_at).toLocaleDateString('pt-BR');
            const statusClass = f.can_meet_deadline ? 'success' : 'danger';
            const statusIcon = f.can_meet_deadline ? 'check-circle' : 'exclamation-triangle';
            const backlogValue = Number(f.backlog || 0);
            const projectedWeeks = Number(f.projected_weeks_p85 || 0);

            html += `
                <div class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${escapeHtml(f.name)}</h6>
                        <small>${date}</small>
                    </div>
                    <p class="mb-1 small">
                        <span class="badge badge-${statusClass}">
                            <i class="fas fa-${statusIcon}"></i>
                            ${f.can_meet_deadline ? 'Prazo OK' : 'Risco de Atraso'}
                        </span>
                        ${backlogValue} itens | ${projectedWeeks.toFixed(1)} sem
                    </p>
                </div>
            `;
        });
        html += '</div>';

        $('#dashboard-historical-list').html(html);

        // Create throughput trend chart
        createThroughputTrendChart(forecasts);

    } catch (error) {
        console.error('Error loading historical metrics:', error);
        $('#dashboard-loading').hide();
        $('#dashboard-historical-list').html('<p class="text-danger">Erro ao carregar histórico.</p>');
    }
}

// Create throughput trend chart
function createThroughputTrendChart(forecasts) {
    const canvas = document.getElementById('dashboard-throughput-chart');
    if (!canvas) return;

    if (dashboardChart) {
        try {
            dashboardChart.destroy();
        } catch (err) {
            console.warn('Failed to destroy dashboard chart', err);
        }
        dashboardChart = null;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const validForecasts = Array.isArray(forecasts)
        ? forecasts.filter(f => f && (f.projected_weeks_p85 != null || f.backlog != null))
        : [];

    if (validForecasts.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
    }

    const labels = [];
    const durations = [];
    const backlogs = [];

    validForecasts.slice().reverse().forEach(f => {
        const date = f.created_at ? new Date(f.created_at) : null;
        labels.push(date ? date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }) : '');
        durations.push(Number(f.projected_weeks_p85) || 0);
        backlogs.push(Number(f.backlog) || 0);
    });

    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Duração Projetada (P85) - semanas',
                    data: durations,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    yAxisID: 'duration-axis',
                    fill: false,
                },
                {
                    label: 'Backlog - itens',
                    data: backlogs,
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    yAxisID: 'backlog-axis',
                    fill: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'index',
                intersect: false,
            },
            legend: {
                position: 'bottom'
            },
            scales: {
                xAxes: [{
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 8
                    },
                    gridLines: {
                        display: false
                    }
                }],
                yAxes: [
                    {
                        id: 'duration-axis',
                        position: 'left',
                        ticks: {
                            beginAtZero: true
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Semanas'
                        }
                    },
                    {
                        id: 'backlog-axis',
                        position: 'right',
                        ticks: {
                            beginAtZero: true
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Itens'
                        },
                        gridLines: {
                            drawOnChartArea: false
                        }
                    }
                ]
            }
        }
    });
}

// Update project health indicators
function updateProjectHealth() {
    // Capacity calculation
    const backlog = getCurrentBacklog();
    const samples = parseThroughputSamples();

    if (samples.length > 0 && backlog > 0) {
        const avgThroughput = samples.reduce((a, b) => a + b, 0) / samples.length;
        const weeksNeeded = backlog / avgThroughput;

        // Capacity percentage (lower is better)
        const capacity = Math.min(100, Math.round((weeksNeeded / 52) * 100)); // % of year
        $('#health-capacity-bar')
            .css('width', capacity + '%')
            .text(capacity + '%')
            .removeClass('bg-success bg-warning bg-danger bg-secondary')
            .addClass(capacity < 30 ? 'bg-success' : capacity < 70 ? 'bg-warning' : 'bg-danger');
    } else {
        $('#health-capacity-bar')
            .css('width', '0%')
            .text('0%')
            .removeClass('bg-success bg-warning bg-danger')
            .addClass('bg-secondary');
    }

    // Risk level
    const riskCount = $('#risks .risk-row')
        .not('#risk-row-template')
        .filter(function () {
            const $row = $(this);
            const likelihood = parseFloat($row.find("input[name='likelihood']").val() || '0');
            const lowImpact = parseFloat($row.find("input[name='lowImpact']").val() || '0');
            const mediumImpact = parseFloat($row.find("input[name='mediumImpact']").val() || '0');
            const highImpact = parseFloat($row.find("input[name='highImpact']").val() || '0');
            return likelihood > 0 || lowImpact > 0 || mediumImpact > 0 || highImpact > 0;
        }).length;
    $('#health-risk-count').text(riskCount);

    let riskLevel = 'Baixo';
    let riskClass = 'alert-success';
    if (riskCount > 5) {
        riskLevel = 'Alto';
        riskClass = 'alert-danger';
    } else if (riskCount > 2) {
        riskLevel = 'Médio';
        riskClass = 'alert-warning';
    }

    $('#health-risk-level').text(riskLevel);
    $('#health-risk').removeClass('alert-success alert-warning alert-danger alert-secondary').addClass(riskClass);

    // Confidence level
    const sampleCount = samples.length;
    $('#health-samples-count').text(sampleCount);

    let confidence = 'Baixa';
    let confClass = 'alert-danger';
    if (sampleCount >= 15) {
        confidence = 'Alta';
        confClass = 'alert-success';
    } else if (sampleCount >= 8) {
        confidence = 'Média';
        confClass = 'alert-warning';
    }

    $('#health-confidence-level').text(confidence);
    $('#health-confidence').removeClass('alert-success alert-warning alert-danger alert-secondary').addClass(confClass);
}

// Helper: Calculate weeks difference
function calculateWeeksDiff(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.ceil(diffDays / 7);
}

// Helper: Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Auto-refresh dashboard when tab is shown
$(document).on('shown.bs.tab', 'a[href="#executive-dashboard"]', function () {
    refreshDashboard();
});

// Export to global scope
window.updateCurrentKPIs = updateCurrentKPIs;
window.updateProjectHealth = updateProjectHealth;
window.refreshDashboard = refreshDashboard;
