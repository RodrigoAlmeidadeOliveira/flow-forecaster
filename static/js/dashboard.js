/**
 * Executive Dashboard Module
 * Populates KPIs and metrics for executive view
 */

let dashboardChart = null;

// Refresh dashboard with current data
async function refreshDashboard() {
    updateCurrentKPIs();
    await loadHistoricalMetrics();
    updateProjectHealth();
}

// Update KPIs from current simulation
function updateCurrentKPIs() {
    // Get throughput from samples
    const tpText = $('#tp-samples-textarea').val();
    if (tpText) {
        const samples = tpText.split('\n')
            .map(line => parseFloat(line.trim()))
            .filter(n => !isNaN(n) && n > 0);

        if (samples.length > 0) {
            const avgThroughput = samples.reduce((a, b) => a + b, 0) / samples.length;
            $('#kpi-throughput').text(avgThroughput.toFixed(1));
        }
    }

    // Get backlog
    const backlog = parseInt($('#backlog').val()) || 0;
    $('#kpi-backlog').text(backlog);

    // Get deadline probability from last results
    if (window.lastSimulationResults && window.lastSimulationResults.duration_p85) {
        const p85 = window.lastSimulationResults.duration_p85;
        $('#kpi-duration').text(p85.toFixed(1));

        // Calculate deadline success probability
        const deadlineDate = $('#deadlineDate').val();
        const startDate = $('#start-date').val();

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
                        ${f.backlog || 0} itens | ${(f.projected_weeks_p85 || 0).toFixed(1)} sem
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
    const ctx = document.getElementById('dashboard-throughput-chart');
    if (!ctx) return;

    // Extract data
    const labels = forecasts.map(f => {
        const date = new Date(f.created_at);
        return date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
    }).reverse();

    const durations = forecasts.map(f => f.projected_weeks_p85 || 0).reverse();
    const backlogs = forecasts.map(f => f.backlog || 0).reverse();

    // Destroy previous chart if exists
    if (dashboardChart) {
        dashboardChart.destroy();
    }

    // Create new chart
    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Duração Projetada (P85) - semanas',
                    data: durations,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    yAxisID: 'y',
                },
                {
                    label: 'Backlog - itens',
                    data: backlogs,
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Semanas'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Itens'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            }
        }
    });
}

// Update project health indicators
function updateProjectHealth() {
    // Capacity calculation
    const backlog = parseInt($('#backlog').val()) || 0;
    const tpText = $('#tp-samples-textarea').val();

    if (tpText && backlog > 0) {
        const samples = tpText.split('\n')
            .map(line => parseFloat(line.trim()))
            .filter(n => !isNaN(n) && n > 0);

        if (samples.length > 0) {
            const avgThroughput = samples.reduce((a, b) => a + b, 0) / samples.length;
            const weeksNeeded = backlog / avgThroughput;

            // Capacity percentage (lower is better)
            const capacity = Math.min(100, Math.round((weeksNeeded / 52) * 100)); // % of year
            $('#health-capacity-bar')
                .css('width', capacity + '%')
                .text(capacity + '%')
                .removeClass('bg-success bg-warning bg-danger')
                .addClass(capacity < 30 ? 'bg-success' : capacity < 70 ? 'bg-warning' : 'bg-danger');
        }
    }

    // Risk level
    const riskCount = $('#risk-list tbody tr').length;
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
    $('#health-risk').removeClass('alert-success alert-warning alert-danger').addClass(riskClass);

    // Confidence level
    if (tpText) {
        const samples = tpText.split('\n').filter(line => line.trim()).length;
        $('#health-samples-count').text(samples);

        let confidence = 'Baixa';
        let confClass = 'alert-danger';
        if (samples >= 15) {
            confidence = 'Alta';
            confClass = 'alert-success';
        } else if (samples >= 8) {
            confidence = 'Média';
            confClass = 'alert-warning';
        }

        $('#health-confidence-level').text(confidence);
        $('#health-confidence').removeClass('alert-success alert-warning alert-danger').addClass(confClass);
    }
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
window.refreshDashboard = refreshDashboard;
