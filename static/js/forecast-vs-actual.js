/**
 * Forecast vs Actual Dashboard
 * Manages the interface for comparing forecasts with actual results
 */

let comparisonChartInstance = null;

// Load dashboard on page load
$(document).ready(function() {
    loadDashboard();
    loadForecasts();

    // Event handlers
    $('#btn-save-actual').click(saveActual);
    $('#registerActualModal').on('hidden.bs.modal', function() {
        $('#registerActualForm')[0].reset();
    });
});

/**
 * Load dashboard data and populate UI
 */
async function loadDashboard() {
    try {
        $('#loading-state').show();
        $('#empty-state').hide();
        $('#dashboard-content').hide();

        const response = await fetch('/api/forecast-vs-actual/dashboard');
        const data = await response.json();

        $('#loading-state').hide();

        if (!data.has_data) {
            $('#empty-state').show();
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

        $('#dashboard-content').show();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        $('#loading-state').hide();
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
    $('#metric-mape').text(metrics.mape.toFixed(1) + '%');
    $('#badge-mape').text(ratings.mape).removeClass().addClass('quality-badge quality-' + getRatingClass(ratings.mape));

    // Accuracy Rate
    $('#metric-accuracy').text(metrics.accuracy_rate.toFixed(1) + '%');
    $('#badge-accuracy').text(ratings.accuracy_rate).removeClass().addClass('quality-badge quality-' + getRatingClass(ratings.accuracy_rate));

    // R²
    $('#metric-r-squared').text(metrics.r_squared.toFixed(3));
    $('#badge-r-squared').text(ratings.r_squared).removeClass().addClass('quality-badge quality-' + getRatingClass(ratings.r_squared));

    // Overall
    $('#metric-overall').text(ratings.overall);
    $('#badge-overall').text(ratings.overall).removeClass().addClass('quality-badge quality-' + getRatingClass(ratings.overall));

    // Additional stats
    $('#total-comparisons').text(data.summary.total_comparisons);

    // Bias
    const biasText = metrics.bias_direction === 'overforecasting' ? 'Superestimativa' :
                     metrics.bias_direction === 'underforecasting' ? 'Subestimativa' :
                     'Balanceado';
    $('#bias-direction').text(biasText);
    $('#bias-count').text(`${metrics.overforecast_count} over / ${metrics.underforecast_count} under`);

    // Mean error
    $('#mean-error').text(metrics.mae.toFixed(1) + ' sem');
}

/**
 * Load detailed analysis with issues and recommendations
 */
async function loadDetailedAnalysis() {
    try {
        const response = await fetch('/api/accuracy-analysis');
        const data = await response.json();

        // Populate issues
        const issuesContainer = $('#issues-container');
        if (data.issues && data.issues.length > 0) {
            issuesContainer.empty();
            data.issues.forEach(issue => {
                const issueClass = 'issue-' + issue.severity;
                const iconClass = issue.severity === 'high' ? 'fa-exclamation-circle' :
                                 issue.severity === 'medium' ? 'fa-exclamation-triangle' :
                                 'fa-info-circle';

                issuesContainer.append(`
                    <div class="issue-card ${issueClass}">
                        <strong><i class="fas ${iconClass}"></i> ${capitalizeFirst(issue.severity)}</strong><br>
                        ${issue.message}
                    </div>
                `);
            });
        } else {
            issuesContainer.html('<p class="text-muted">Nenhum alerta detectado. ✓</p>');
        }

        // Populate recommendations
        const recsContainer = $('#recommendations-container');
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
    const ctx = document.getElementById('comparisonChart').getContext('2d');

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
    const tbody = $('#comparisons-table-body');
    tbody.empty();

    if (!comparisons || comparisons.length === 0) {
        tbody.append('<tr><td colspan="7" class="text-center text-muted">Nenhuma comparação disponível</td></tr>');
        return;
    }

    comparisons.forEach(c => {
        const errorClass = c.error_pct > 0 ? 'error-positive' : 'error-negative';
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

        const select = $('#select-forecast');
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
        const forecastId = $('#select-forecast').val();
        if (!forecastId) {
            showError('Selecione uma previsão');
            return;
        }

        const actualCompletionDate = $('#actual-completion-date').val();
        if (!actualCompletionDate) {
            showError('Informe a data de conclusão real');
            return;
        }

        const data = {
            forecast_id: parseInt(forecastId),
            actual_completion_date: actualCompletionDate,
            actual_weeks_taken: parseFloat($('#actual-weeks-taken').val()) || null,
            actual_items_completed: parseInt($('#actual-items-completed').val()) || null,
            actual_scope_delivered_pct: parseFloat($('#actual-scope-pct').val()) || null,
            notes: $('#actual-notes').val() || null,
            recorded_by: $('#recorded-by').val() || null
        };

        // Show loading
        $('#save-spinner').show();
        $('#btn-save-actual').prop('disabled', true);

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
        showSuccess('Resultado real registrado com sucesso!');

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('registerActualModal'));
        modal.hide();

        // Reload dashboard
        setTimeout(() => {
            loadDashboard();
        }, 500);

    } catch (error) {
        console.error('Error saving actual:', error);
        showError('Erro ao salvar: ' + error.message);
    } finally {
        $('#save-spinner').hide();
        $('#btn-save-actual').prop('disabled', false);
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

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'danger');
}

function showInfo(message) {
    showToast(message, 'info');
}

function showToast(message, type) {
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11000">
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        </div>
    `;

    $('body').append(toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();

    // Remove after hiding
    toastElement.addEventListener('hidden.bs.toast', function() {
        $(this).parent().remove();
    });
}
