/**
 * Cost of Delay (CoD) Analysis Interface
 * Handles prediction, calculation, and visualization of Cost of Delay metrics
 */

$(document).ready(function() {
    let featureImportanceChart = null;
    let lastPredictionResult = null;
    let datasetState = null;

    // ===============================================
    // Helper Functions
    // ===============================================

    function formatCurrency(value) {
        if (value === null || value === undefined) return '—';
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    function formatNumber(value, decimals = 2) {
        if (value === null || value === undefined) return '—';
        return value.toFixed(decimals);
    }

    function showError(message) {
        alert('Erro: ' + message);
    }

    function showSuccess(message) {
        // You can implement a toast notification here
        console.log('Success:', message);
    }

    function formatDateTime(isoString) {
        if (!isoString) return '—';
        const date = new Date(isoString);
        if (Number.isNaN(date.getTime())) {
            return isoString;
        }
        return date.toLocaleString('pt-BR');
    }

    function renderDatasetStatus(state) {
        const statusEl = $('#codDatasetStatus');
        const trainingMessageEl = $('#codTrainingMessage');
        const trainButton = $('#trainCodModel');

        let statusHtml = '';
        let messageHtml = '';

        trainButton.removeClass('btn-warning btn-success');

        if (!state || !state.has_dataset) {
            statusHtml = '<strong>Nenhum dataset carregado.</strong><br>Importe um CSV com os dados históricos para treinar o modelo personalizado.';
            trainButton.prop('disabled', true);
            trainingMessageEl.html('');
            statusEl.html(statusHtml);
            return;
        }

        const dataset = state.dataset || {};
        const datasetName = dataset.name || dataset.original_filename || 'Dataset';

        statusHtml += `<div><strong>${datasetName}</strong></div>`;
        if (dataset.row_count !== undefined) {
            statusHtml += `<div>Linhas válidas: ${dataset.row_count}</div>`;
        }
        if (dataset.created_at) {
            statusHtml += `<div>Último upload: ${formatDateTime(dataset.created_at)}</div>`;
        }
        if (dataset.column_names && dataset.column_names.length) {
            statusHtml += `<div><small>Colunas: ${dataset.column_names.join(', ')}</small></div>`;
        }

        if (state.has_model && state.model) {
            statusHtml += '<hr class="my-2">';
            statusHtml += `<div><strong>Treinado em:</strong> ${formatDateTime(state.model.trained_at)}</div>`;
            if (state.model.sample_count) {
                statusHtml += `<div>Amostras utilizadas: ${state.model.sample_count}</div>`;
            }

            if (state.model.metrics) {
                statusHtml += '<ul class="mb-0">';
                for (const [modelName, metrics] of Object.entries(state.model.metrics)) {
                    statusHtml += `<li><strong>${modelName}</strong>: MAE ${formatCurrency(metrics.mae)} | R² ${formatNumber(metrics.r2, 3)}</li>`;
                }
                statusHtml += '</ul>';
            }
        }

        trainButton.prop('disabled', false);

        if (state.retrain_required) {
            messageHtml = '<div class="alert alert-warning mb-0 mt-2">Re-treine o modelo para incorporar o novo dataset.</div>';
            trainButton.addClass('btn-warning');
        } else if (state.has_model) {
            messageHtml = '<div class="alert alert-success mb-0 mt-2">Modelo personalizado treinado e pronto para uso.</div>';
            trainButton.addClass('btn-success');
        } else {
            messageHtml = '<div class="alert alert-info mb-0 mt-2">Finalize o treinamento para habilitar o modelo personalizado.</div>';
            trainButton.addClass('btn-warning');
        }

        statusEl.html(statusHtml);
        trainingMessageEl.html(messageHtml);
    }

    function loadCodDatasetStatus() {
        $('#codDatasetStatus').html('<span class="text-muted">Carregando informações...</span>');
        $.ajax({
            url: '/api/cod/dataset',
            method: 'GET',
            success: function(response) {
                datasetState = response;
                renderDatasetStatus(response);
            },
            error: function(xhr) {
                $('#codDatasetStatus').html(
                    '<div class="text-danger">Não foi possível carregar as informações: ' +
                    (xhr.responseJSON?.error || 'Erro desconhecido') + '</div>'
                );
            }
        });
    }

    // ===============================================
    // Model Info
    // ===============================================

    $('#showModelInfo').on('click', function() {
        const panel = $('#model-info-panel');

        if (panel.is(':visible')) {
            panel.slideUp();
            $(this).text('Show Model Details');
            return;
        }

        panel.slideDown();
        $(this).text('Hide Model Details');
        loadCodModelInfo();
    });

    function loadCodModelInfo() {
        $('#model-info-content').html(
            '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div></div>'
        );

        $.ajax({
            url: '/api/cod/model_info',
            method: 'GET',
            success: function(response) {
                displayModelInfo(response);
            },
            error: function(xhr) {
                $('#model-info-content').html(
                    '<div class="alert alert-warning">Model information not available. ' +
                    (xhr.responseJSON?.error || 'Unknown error') + '</div>'
                );
            }
        });
    }

    function displayModelInfo(data) {
        if (!data.trained) {
            let html = `<div class="alert alert-warning">${data.error || 'Modelo não treinado ainda.'}</div>`;

            if (data.dataset) {
                html += '<div class="mt-3">';
                html += `<div><strong>Dataset carregado:</strong> ${data.dataset.name || data.dataset.original_filename}</div>`;
                html += `<div>Linhas válidas: ${data.dataset.row_count}</div>`;
                if (data.dataset.created_at) {
                    html += `<div>Último upload: ${formatDateTime(data.dataset.created_at)}</div>`;
                }
                html += '</div>';
            }

            $('#model-info-content').html(html);
            return;
        }

        let html = '<div class="row">';

        // Display models
        html += '<div class="col-md-6">';
        html += '<h5>Trained Models</h5>';
        html += '<table class="table table-sm table-bordered">';
        html += '<thead><tr><th>Model</th><th>MAE (R$/week)</th><th>R²</th><th>MAPE</th></tr></thead>';
        html += '<tbody>';

        for (const [modelName, metrics] of Object.entries(data.models)) {
            html += `<tr>
                <td><strong>${modelName}</strong></td>
                <td>${formatCurrency(metrics.mae)}</td>
                <td>${formatNumber(metrics.r2, 3)}</td>
                <td>${formatNumber(metrics.mape, 1)}%</td>
            </tr>`;
        }

        html += '</tbody></table>';
        html += '<small class="text-muted"><strong>MAE:</strong> Mean Absolute Error | <strong>R²:</strong> Coefficient of Determination | <strong>MAPE:</strong> Mean Absolute Percentage Error</small>';
        html += '</div>';

        // Display features
        html += '<div class="col-md-6">';
        html += '<h5>Model Features</h5>';
        html += '<ul class="list-group">';

        data.features.forEach(feature => {
            html += `<li class="list-group-item py-1"><small>${feature}</small></li>`;
        });

        html += '</ul>';
        html += '</div>';

        html += '<div class="col-12 mt-3">';
        html += `<div><strong>Fonte do modelo:</strong> ${data.source === 'custom' ? 'Personalizado (seus dados)' : 'Padrão (dados sintéticos)'}</div>`;
        if (data.trained_at) {
            html += `<div><strong>Treinado em:</strong> ${formatDateTime(data.trained_at)}</div>`;
        }
        if (data.sample_count) {
            html += `<div><strong>Amostras utilizadas:</strong> ${data.sample_count}</div>`;
        }
        if (data.dataset) {
            html += `<div><strong>Dataset:</strong> ${data.dataset.name || data.dataset.original_filename} (${data.dataset.row_count} linhas)</div>`;
        }
        html += '</div>';

        html += '</div>';

        $('#model-info-content').html(html);
    }

    // ===============================================
    // Dataset Management
    // ===============================================

    $('#codDatasetForm').on('submit', function(event) {
        event.preventDefault();

        const fileInput = $('#codDatasetFile')[0];
        if (!fileInput || fileInput.files.length === 0) {
            showError('Selecione um arquivo CSV para importar.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('name', $('#codDatasetName').val());

        const uploadButton = $('#uploadCodDataset');
        uploadButton.prop('disabled', true).text('Enviando...');
        $('#trainCodModel').prop('disabled', true);
        $('#codTrainingMessage').html('<span class="text-muted">Enviando dataset...</span>');

        $.ajax({
            url: '/api/cod/dataset',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                showSuccess(response.message || 'Dataset importado com sucesso.');
                $('#codDatasetFile').val('');
                loadCodDatasetStatus();
            },
            error: function(xhr) {
                showError(xhr.responseJSON?.error || 'Falha ao importar o dataset.');
                loadCodDatasetStatus();
            },
            complete: function() {
                uploadButton.prop('disabled', false).text('⬆️ Importar CSV');
            }
        });
    });

    $('#trainCodModel').on('click', function() {
        const button = $(this);
        if (button.prop('disabled')) {
            return;
        }

        button.prop('disabled', true).text('Treinando...');
        $('#codTrainingMessage').html('<span class="text-muted">Treinando modelo, aguarde...</span>');

        $.ajax({
            url: '/api/cod/train',
            method: 'POST',
            success: function(response) {
                showSuccess(response.message || 'Modelo treinado com sucesso.');
                $('#codTrainingMessage').html('<div class="alert alert-success mt-2 mb-0">' + (response.message || 'Modelo treinado com sucesso.') + '</div>');
                loadCodDatasetStatus();

                if ($('#model-info-panel').is(':visible')) {
                    loadCodModelInfo();
                }
            },
            error: function(xhr) {
                const errorMessage = xhr.responseJSON?.error || 'Falha ao treinar o modelo.';
                showError(errorMessage);
                $('#codTrainingMessage').html('<div class="alert alert-danger mt-2 mb-0">' + errorMessage + '</div>');
                if (xhr.responseJSON?.retrain_required) {
                    loadCodDatasetStatus();
                }
            },
            complete: function() {
                button.prop('disabled', false).text('🛠️ Treinar modelo com meus dados');
            }
        });
    });

    // ===============================================
    // CoD Prediction
    // ===============================================

    $('#predictCoD').on('click', function() {
        predictCoD();
    });

    function predictCoD() {
        // Get form values
        const budget = parseFloat($('#codBudget').val());
        const duration = parseInt($('#codDuration').val());
        const teamSize = parseInt($('#codTeamSize').val());
        const stakeholders = parseInt($('#codStakeholders').val());
        const businessValue = parseFloat($('#codBusinessValue').val());
        const complexity = parseInt($('#codComplexity').val());
        const projectType = $('#codProjectType').val();
        const riskLevel = parseInt($('#codRiskLevel').val());

        // Validation
        if (!budget || !duration || !teamSize || !stakeholders ||
            !businessValue || !complexity) {
            showError('Por favor, preencha todos os campos obrigatórios.');
            return;
        }

        if (businessValue < 0 || businessValue > 100) {
            showError('Business Value deve estar entre 0 e 100.');
            return;
        }

        if (complexity < 1 || complexity > 5) {
            showError('Complexity deve estar entre 1 e 5.');
            return;
        }

        // Prepare request data
        const requestData = {
            budget_millions: budget,
            duration_weeks: duration,
            team_size: teamSize,
            num_stakeholders: stakeholders,
            business_value: businessValue,
            complexity: complexity,
            project_type: projectType,
            risk_level: riskLevel
        };

        // Show loading state
        $('#predictCoD').prop('disabled', true).html('🔮 Predicting...');

        // Call API
        $.ajax({
            url: '/api/cod/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                displayCoDPrediction(response);
                lastPredictionResult = response;
            },
            error: function(xhr) {
                showError('Falha na previsão: ' + (xhr.responseJSON?.error || 'Erro desconhecido'));
                if (xhr.responseJSON?.retrain_required) {
                    loadCodDatasetStatus();
                }
            },
            complete: function() {
                $('#predictCoD').prop('disabled', false).html('🔮 Predict Cost of Delay');
            }
        });
    }

    function displayCoDPrediction(result) {
        // Display results
        $('#cod-weekly-value').text(formatCurrency(result.cod_weekly));
        $('#cod-daily-value').text(formatCurrency(result.cod_daily));
        $('#cod-monthly-value').text(formatCurrency(result.cod_monthly));

        // Confidence interval
        const ci = result.confidence_interval_95;
        $('#cod-confidence-interval').html(
            `<strong>${formatCurrency(ci[0])}</strong> to <strong>${formatCurrency(ci[1])}</strong>`
        );

        // Auto-fill weekly CoD in calculator
        $('#codWeeklyInput').val(result.cod_weekly.toFixed(2));

        // Show results
        $('#cod-prediction-results').slideDown();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#cod-prediction-results').offset().top - 100
        }, 500);

        showSuccess('CoD prediction completed successfully!');
    }

    // ===============================================
    // Total CoD Calculator
    // ===============================================

    $('#calculateTotalCoD').on('click', function() {
        calculateTotalCoD();
    });

    function calculateTotalCoD() {
        const codWeekly = parseFloat($('#codWeeklyInput').val());
        const delayWeeks = parseFloat($('#delayWeeks').val());

        // Validation
        if (!codWeekly || codWeekly <= 0) {
            showError('Por favor, forneça um Weekly CoD válido. Execute a previsão primeiro.');
            return;
        }

        if (!delayWeeks || delayWeeks < 0) {
            showError('Por favor, forneça uma duração de atraso válida.');
            return;
        }

        // Prepare request
        const requestData = {
            cod_weekly: codWeekly,
            delay_weeks: delayWeeks
        };

        // Show loading
        $('#calculateTotalCoD').prop('disabled', true).html('💵 Calculating...');

        // Call API
        $.ajax({
            url: '/api/cod/calculate_total',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                displayTotalCoD(response);
            },
            error: function(xhr) {
                showError('Falha no cálculo: ' + (xhr.responseJSON?.error || 'Erro desconhecido'));
            },
            complete: function() {
                $('#calculateTotalCoD').prop('disabled', false).html('💵 Calculate Total Cost');
            }
        });
    }

    function displayTotalCoD(result) {
        // Display results
        $('#total-cod-value').text(formatCurrency(result.total_cod));
        $('#total-cod-weekly').text(formatCurrency(result.cod_weekly));
        $('#total-cod-weeks').text(formatNumber(result.delay_weeks, 1));

        // Show results
        $('#total-cod-results').slideDown();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#total-cod-results').offset().top - 100
        }, 500);

        showSuccess('Total CoD calculated successfully!');
    }

    // ===============================================
    // Feature Importance
    // ===============================================

    $('#showFeatureImportance').on('click', function() {
        if ($('#feature-importance-results').is(':visible')) {
            $('#feature-importance-results').slideUp();
            $(this).text('📈 Show Feature Importance');
            return;
        }

        // Show loading
        $(this).prop('disabled', true).html('📈 Loading...');

        // Call API
        $.ajax({
            url: '/api/cod/feature_importance',
            method: 'GET',
            success: function(response) {
                displayFeatureImportance(response.features);
                $('#feature-importance-results').slideDown();
                $('#showFeatureImportance').text('📈 Hide Feature Importance');
            },
            error: function(xhr) {
                showError('Falha ao obter feature importance: ' + (xhr.responseJSON?.error || 'Erro desconhecido'));
                if (xhr.responseJSON?.retrain_required) {
                    loadCodDatasetStatus();
                }
            },
            complete: function() {
                $('#showFeatureImportance').prop('disabled', false);
            }
        });
    });

    function displayFeatureImportance(features) {
        // Sort features by importance
        features.sort((a, b) => b.importance - a.importance);

        // Take top 10
        const topFeatures = features.slice(0, 10);

        // Create table
        let tableHtml = '';
        topFeatures.forEach((feature, index) => {
            const importance = (feature.importance * 100).toFixed(2);
            const barWidth = (feature.importance * 100).toFixed(0);

            let impactClass = 'text-success';
            let impactLabel = 'Low';
            if (feature.importance > 0.15) {
                impactClass = 'text-danger';
                impactLabel = 'High';
            } else if (feature.importance > 0.08) {
                impactClass = 'text-warning';
                impactLabel = 'Medium';
            }

            tableHtml += `
                <tr>
                    <td><strong>${feature.feature}</strong></td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-primary" role="progressbar"
                                 style="width: ${barWidth}%"
                                 aria-valuenow="${barWidth}" aria-valuemin="0" aria-valuemax="100">
                                ${importance}%
                            </div>
                        </div>
                    </td>
                    <td><span class="${impactClass}">${impactLabel}</span></td>
                </tr>
            `;
        });

        $('#feature-importance-table').html(tableHtml);

        // Create chart
        drawFeatureImportanceChart(topFeatures);
    }

    function drawFeatureImportanceChart(features) {
        const ctx = document.getElementById('feature-importance-chart').getContext('2d');

        // Destroy previous chart
        if (featureImportanceChart) {
            featureImportanceChart.destroy();
        }

        // Prepare data
        const labels = features.map(f => f.feature);
        const data = features.map(f => (f.importance * 100).toFixed(2));

        // Create chart
        featureImportanceChart = new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Importance (%)',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Top 10 Most Important Features for CoD Prediction'
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Importance (%)'
                        },
                        ticks: {
                            beginAtZero: true,
                            max: Math.max(...data) * 1.1
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Feature'
                        }
                    }]
                },
                legend: {
                    display: false
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return 'Importance: ' + tooltipItem.xLabel + '%';
                        }
                    }
                }
            }
        });

        // Set chart container height
        $('#feature-importance-chart').parent().css('height', '400px');
    }

    // ===============================================
    // Initialize
    // ===============================================

    loadCodDatasetStatus();
    console.log('Cost of Delay interface initialized');
});
