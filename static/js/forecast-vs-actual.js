/**
 * Forecast vs Actual Dashboard
 * Manages the interface for comparing forecasts with actual results
 */

let comparisonChartInstance = null;
let fvaInitialized = false;

// Initialize when tab is shown
$(document).ready(function() {
    // Load when tab is activated
    $('#tab-forecast-vs-actual').on('shown.bs.tab', function() {
        if (!fvaInitialized) {
            fvaInitialized = true;
            initForecastVsActual();
        }
        loadDashboard();
    });
});

function initForecastVsActual() {
    loadForecasts();

    // Event handlers
    $('#fva-btn-save-actual').click(saveActual);

    // Reload forecasts when modal is shown
    $('#registerActualModal').on('show.bs.modal', function() {
        loadForecasts();
    });

    $('#registerActualModal').on('hidden.bs.modal', function() {
        $('#fva-registerActualForm')[0].reset();
    });
}

/**
 * Load dashboard data and populate UI
 */
async function loadDashboard() {
    try {
        $('#fva-loading-state').show();
        $('#fva-empty-state').hide();
        $('#fva-dashboard-content').hide();

        const response = await fetch('/api/forecast-vs-actual/dashboard');
        const data = await response.json();

        $('#fva-loading-state').hide();

        if (!data.has_data) {
            $('#fva-empty-state').show();
            return;
        }

        // Populate metrics
        populateMetrics(data);

        // Populate issues and recommendations
        await loadDetailedAnalysis();

        // Render chart
        renderComparisonChart(data.recent_comparisons);

        // Populate table
        populateComparisonsTable(data.recent_comparisons);

        $('#fva-dashboard-content').show();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        $('#fva-loading-state').hide();
        showError('Erro ao carregar dashboard: ' + error.message);
    }
}

/**
 * Populate metrics cards
 */
function populateMetrics(data) {
    const metrics = data.overall_metrics;
    const ratings = data.quality_ratings;

    // MAPE
    $('#fva-metric-mape').text(metrics.mape.toFixed(1) + '%');
    $('#fva-badge-mape').text(ratings.mape).removeClass().addClass('badge badge-' + getBadgeClass(ratings.mape));

    // Accuracy Rate
    $('#fva-metric-accuracy').text(metrics.accuracy_rate.toFixed(1) + '%');
    $('#fva-badge-accuracy').text(ratings.accuracy_rate).removeClass().addClass('badge badge-' + getBadgeClass(ratings.accuracy_rate));

    // R²
    $('#fva-metric-r-squared').text(metrics.r_squared.toFixed(3));
    $('#fva-badge-r-squared').text(ratings.r_squared).removeClass().addClass('badge badge-' + getBadgeClass(ratings.r_squared));

    // Overall
    $('#fva-metric-overall').text(ratings.overall);
    $('#fva-badge-overall').text(ratings.overall).removeClass().addClass('badge badge-' + getBadgeClass(ratings.overall));

    // Additional stats
    $('#fva-total-comparisons').text(data.summary.total_comparisons);

    // Bias
    const biasText = metrics.bias_direction === 'overforecasting' ? 'Superestimativa' :
                     metrics.bias_direction === 'underforecasting' ? 'Subestimativa' :
                     'Balanceado';
    $('#fva-bias-direction').text(biasText);
    $('#fva-bias-count').text(`${metrics.overforecast_count} over / ${metrics.underforecast_count} under`);

    // Mean error
    $('#fva-mean-error').text(metrics.mae.toFixed(1) + ' sem');
}

/**
 * Load detailed analysis with issues and recommendations
 */
async function loadDetailedAnalysis() {
    try {
        const response = await fetch('/api/accuracy-analysis');
        const data = await response.json();

        // Populate issues
        const issuesContainer = $('#fva-issues-container');
        if (data.issues && data.issues.length > 0) {
            issuesContainer.empty();
            data.issues.forEach(issue => {
                const badgeClass = issue.severity === 'high' ? 'danger' :
                                  issue.severity === 'medium' ? 'warning' : 'info';
                const iconClass = issue.severity === 'high' ? 'fa-exclamation-circle' :
                                 issue.severity === 'medium' ? 'fa-exclamation-triangle' :
                                 'fa-info-circle';

                issuesContainer.append(`
                    <div class="alert alert-${badgeClass} mb-2">
                        <strong><i class="fas ${iconClass}"></i> ${capitalizeFirst(issue.severity)}</strong><br>
                        ${issue.message}
                    </div>
                `);
            });
        } else {
            issuesContainer.html('<p class="text-muted">Nenhum alerta detectado. ✓</p>');
        }

        // Populate recommendations
        const recsContainer = $('#fva-recommendations-container');
        if (data.recommendations && data.recommendations.length > 0) {
            recsContainer.empty();
            const recsList = $('<ul class="mb-0"></ul>');
            data.recommendations.forEach(rec => {
                recsList.append(`<li class="mb-2">${rec}</li>`);
            });
            recsContainer.append(recsList);
        } else {
            recsContainer.html('<p class="text-muted">Nenhuma recomendação no momento.</p>');
        }

    } catch (error) {
        console.error('Error loading detailed analysis:', error);
    }
}

/**
 * Render comparison chart
 */
function renderComparisonChart(comparisons) {
    const ctx = document.getElementById('fva-comparisonChart').getContext('2d');

    // Destroy previous chart if exists
    if (comparisonChartInstance) {
        comparisonChartInstance.destroy();
    }

    // Prepare data
    const labels = comparisons.map((c, idx) => `#${idx + 1}`);
    const forecastedData = comparisons.map(c => c.forecasted_weeks);
    const actualData = comparisons.map(c => c.actual_weeks);

    comparisonChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Previsto (P85)',
                    data: forecastedData,
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Real',
                    data: actualData,
                    backgroundColor: 'rgba(40, 167, 69, 0.6)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const idx = context.dataIndex;
                            const comparison = comparisons[idx];
                            if (context.datasetIndex === 1 && comparison.error_pct !== null) {
                                return `Erro: ${comparison.error_pct.toFixed(1)}%`;
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Semanas'
                    }
                }
            }
        }
    });
}

/**
 * Populate comparisons table
 */
function populateComparisonsTable(comparisons) {
    const tbody = $('#fva-comparisons-table-body');
    tbody.empty();

    if (!comparisons || comparisons.length === 0) {
        tbody.append('<tr><td colspan="7" class="text-center text-muted">Nenhuma comparação disponível</td></tr>');
        return;
    }

    comparisons.forEach(c => {
        const errorClass = c.error_pct > 0 ? 'text-danger' : 'text-success';
        const errorSign = c.error_pct > 0 ? '+' : '';
        const date = new Date(c.created_at).toLocaleDateString('pt-BR');

        tbody.append(`
            <tr>
                <td><strong>${c.forecast_name}</strong></td>
                <td>${c.project_name || '-'}</td>
                <td>${date}</td>
                <td>${c.forecasted_weeks.toFixed(1)}</td>
                <td>${c.actual_weeks.toFixed(1)}</td>
                <td class="${errorClass}">
                    <strong>${errorSign}${c.error_pct.toFixed(1)}%</strong>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewForecastDetails(${c.forecast_id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `);
    });
}

/**
 * Load forecasts for the dropdown
 */
async function loadForecasts() {
    try {
        const response = await fetch('/api/forecasts');
        const forecasts = await response.json();

        const select = $('#fva-select-forecast');
        select.empty();

        if (forecasts.length === 0) {
            select.append('<option value="">Nenhuma previsão disponível</option>');
            return;
        }

        select.append('<option value="">Selecione uma previsão...</option>');

        forecasts.forEach(f => {
            // Only show forecasts that don't have actuals yet
            const label = `${f.name} - ${f.project_name || 'Sem projeto'} (${f.created_at ? new Date(f.created_at).toLocaleDateString('pt-BR') : ''})`;
            select.append(`<option value="${f.id}" data-start-date="${f.start_date}">${label}</option>`);
        });

    } catch (error) {
        console.error('Error loading forecasts:', error);
        showError('Erro ao carregar previsões: ' + error.message);
    }
}

/**
 * Save actual result
 */
async function saveActual() {
    try {
        const forecastId = $('#fva-select-forecast').val();
        if (!forecastId) {
            alert('Selecione uma previsão');
            return;
        }

        const actualCompletionDate = $('#fva-actual-completion-date').val();
        if (!actualCompletionDate) {
            alert('Informe a data de conclusão real');
            return;
        }

        const data = {
            forecast_id: parseInt(forecastId),
            actual_completion_date: actualCompletionDate,
            actual_weeks_taken: parseFloat($('#fva-actual-weeks-taken').val()) || null,
            actual_items_completed: parseInt($('#fva-actual-items-completed').val()) || null,
            actual_scope_delivered_pct: parseFloat($('#fva-actual-scope-pct').val()) || null,
            notes: $('#fva-actual-notes').val() || null,
            recorded_by: $('#fva-recorded-by').val() || null
        };

        // Show loading
        $('#fva-save-spinner').show();
        $('#fva-btn-save-actual').prop('disabled', true);

        const response = await fetch('/api/actuals', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao salvar');
        }

        // Success
        alert('Resultado real registrado com sucesso!');

        // Close modal
        $('#registerActualModal').modal('hide');

        // Reload dashboard
        setTimeout(() => {
            loadDashboard();
            loadForecasts();
        }, 500);

    } catch (error) {
        console.error('Error saving actual:', error);
        alert('Erro ao salvar: ' + error.message);
    } finally {
        $('#fva-save-spinner').hide();
        $('#fva-btn-save-actual').prop('disabled', false);
    }
}

/**
 * View forecast details (placeholder for future implementation)
 */
function viewForecastDetails(forecastId) {
    // TODO: Implement modal or navigation to forecast details
    console.log('View forecast:', forecastId);
    showInfo(`Visualizando previsão #${forecastId}`);
}

/**
 * Helper Functions
 */

function getBadgeClass(rating) {
    switch(rating.toLowerCase()) {
        case 'excelente': return 'success';
        case 'bom': return 'info';
        case 'aceitável': return 'warning';
        case 'ruim': return 'danger';
        default: return 'secondary';
    }
}

function getRatingClass(rating) {
    switch(rating.toLowerCase()) {
        case 'excelente': return 'excellent';
        case 'bom': return 'good';
        case 'aceitável': return 'acceptable';
        case 'ruim': return 'poor';
        default: return 'acceptable';
    }
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
