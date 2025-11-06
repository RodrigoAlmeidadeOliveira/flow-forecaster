/**
 * Cost of Delay (CoD) Analysis Interface
 * Handles prediction, calculation, and visualization of Cost of Delay metrics
 */

$(document).ready(function() {
    let featureImportanceChart = null;
    let lastPredictionResult = null;

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

        // Show panel with loading spinner
        panel.slideDown();
        $(this).text('Hide Model Details');

        // Fetch model info
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
    });

    function displayModelInfo(data) {
        if (!data.trained) {
            $('#model-info-content').html(
                '<div class="alert alert-warning">Model not trained yet. The model will be initialized when you make your first prediction.</div>'
            );
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

        html += '</div>';

        $('#model-info-content').html(html);
    }

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

    console.log('Cost of Delay interface initialized');
});
