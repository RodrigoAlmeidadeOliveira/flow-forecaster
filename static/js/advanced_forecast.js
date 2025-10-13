$(document).ready(function() {
    function parseSamples(text) {
        if (!text || text.trim().length === 0) return [];
        return text.split(/[\s\n,]/)
            .map(s => s.trim())
            .filter(s => s.length > 0)
            .map(s => parseFloat(s))
            .filter(n => !isNaN(n) && n >= 0);
    }

    const walkForwardCharts = [];

    function showLoading() {
        $('#loading').show();
        $('#results-container').hide();
    }

    function hideLoading() {
        $('#loading').hide();
    }

    function displayError(message) {
        hideLoading();
        alert('Error: ' + message);
    }

    function displayRiskAssessment(risk) {
        const riskClass = risk.risk_level === 'HIGH' ? 'risk-high' :
                         risk.risk_level === 'MEDIUM' ? 'risk-medium' : 'risk-low';

        let html = `
            <div class="metric-card">
                <p><strong>Risk Level:</strong> <span class="${riskClass}">${risk.risk_level}</span></p>
                <p><strong>Volatility (CV):</strong> ${risk.volatility_cv}</p>
                <p><strong>Trend Deviation:</strong> ${risk.trend_deviation_pct}%</p>
                <p><strong>Outlier Percentage:</strong> ${risk.outlier_pct}%</p>
                ${risk.warning ? `<p class="text-warning"><strong>⚠️ ${risk.warning}</strong></p>` : ''}
                ${risk.recommend_monte_carlo ? '<p class="text-info"><strong>💡 Recommendation:</strong> Use Monte Carlo simulation for better uncertainty handling</p>' : ''}
            </div>
        `;
        $('#risk-assessment').html(html);
    }

    function displayModelPerformance(models) {
        if (!models || models.length === 0) {
            $('#model-performance').html('<div class="alert alert-warning">No model performance data available</div>');
            return;
        }

        // Check if K-Fold CV metrics are available
        const hasKFoldMetrics = models.some(m => m.mae_std !== undefined);

        let html = `
            <div class="alert alert-info mb-3">
                <strong>K-Fold Cross-Validation Protocol (5-fold)</strong><br>
                Training set: 80% | Validation set: 20% | Grid Search for hyperparameter tuning
            </div>
        `;

        if (hasKFoldMetrics) {
            // Display detailed K-Fold CV results
            html += '<div class="table-responsive">';
            html += '<table class="table table-sm table-hover">';
            html += '<thead class="thead-dark"><tr>';
            html += '<th>Model</th>';
            html += '<th>CV MAE<br><small>(mean ± std)</small></th>';
            html += '<th>CV RMSE<br><small>(mean ± std)</small></th>';
            html += '<th>CV R²<br><small>(mean ± std)</small></th>';
            html += '<th>Val MAE</th>';
            html += '<th>Val R²</th>';
            html += '<th>Best Hyperparameters</th>';
            html += '</tr></thead><tbody>';

            models.forEach(model => {
                const mae_cv = model.mae_std ? `${model.mae} ± ${model.mae_std}` : model.mae;
                const rmse_cv = model.rmse_std ? `${model.rmse} ± ${model.rmse_std}` : model.rmse;
                const r2_cv = model.r2_std !== undefined ? `${model.r2_mean} ± ${model.r2_std}` : '—';
                const val_mae = model.val_mae !== undefined ? model.val_mae : '—';
                const val_r2 = model.val_r2 !== undefined ? model.val_r2 : '—';

                let best_params = '—';
                if (model.best_params) {
                    best_params = Object.entries(model.best_params)
                        .map(([key, val]) => `${key}=${val}`)
                        .join('<br>');
                }

                html += `<tr>
                    <td><strong>${model.model}</strong></td>
                    <td>${mae_cv}</td>
                    <td>${rmse_cv}</td>
                    <td>${r2_cv}</td>
                    <td>${val_mae}</td>
                    <td>${val_r2}</td>
                    <td><small>${best_params}</small></td>
                </tr>`;
            });

            html += '</tbody></table></div>';

            // Add summary statistics
            html += '<div class="mt-3 p-3 bg-light border rounded">';
            html += '<h6 class="font-weight-bold">Resumo do Protocolo:</h6>';
            html += '<ul class="mb-0 small">';
            html += '<li><strong>CV MAE:</strong> Erro Absoluto Médio na validação cruzada (menor é melhor)</li>';
            html += '<li><strong>CV RMSE:</strong> Raiz do Erro Quadrático Médio (menor é melhor)</li>';
            html += '<li><strong>CV R²:</strong> Coeficiente de determinação (próximo de 1 é melhor)</li>';
            html += '<li><strong>Val MAE/R²:</strong> Métricas no conjunto de validação (20%)</li>';
            html += '<li><strong>± std:</strong> Desvio padrão entre os 5 folds (menor indica maior estabilidade)</li>';
            html += '</ul></div>';

        } else {
            // Display legacy format
            html += '<table class="table table-sm table-striped">';
            html += '<thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAE %</th></tr></thead><tbody>';
            models.forEach(model => {
                html += `<tr>
                    <td>${model.model}</td>
                    <td>${model.mae}</td>
                    <td>${model.rmse}</td>
                    <td>${model.mae_percent}%</td>
                </tr>`;
            });
            html += '</tbody></table>';
        }

        $('#model-performance').html(html);
    }

    function displayMCStats(mcData) {
        if (!mcData) {
            $('#mc-stats').html('<div class="alert alert-warning">Monte Carlo stats unavailable.</div>');
            return;
        }

        const stats = mcData.percentile_stats || {};
        const mean = mcData.mean != null ? mcData.mean : '—';
        const std = mcData.std != null ? mcData.std : '—';

        let html = `
            <div class="row">
                <div class="col-md-3"><div class="metric-card"><strong>Mean:</strong> ${mean} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>Std Dev:</strong> ${std} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P50:</strong> ${stats.p50 ?? '—'} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P85:</strong> ${stats.p85 ?? '—'} weeks</div></div>
            </div>
            <div class="row">
                <div class="col-md-3"><div class="metric-card"><strong>P10:</strong> ${stats.p10 ?? '—'} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P25:</strong> ${stats.p25 ?? '—'} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P75:</strong> ${stats.p75 ?? '—'} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P90:</strong> ${stats.p90 ?? '—'} weeks</div></div>
            </div>
        `;
        $('#mc-stats').html(html);
    }

    function displayMLSummary(mlData, backlog, startDate) {
        const ensemble = mlData.ensemble;

        // Calculate completion weeks based on backlog and throughput forecast
        let completionWeeks = null;
        if (backlog && ensemble && ensemble.mean) {
            // Simulate week-by-week completion
            let remaining = backlog;
            let week = 0;
            const forecastLength = ensemble.mean.length;

            while (remaining > 0 && week < forecastLength * 2) {
                // Use forecast value if available, otherwise use last forecast value
                const throughput = week < forecastLength ? ensemble.mean[week] : ensemble.mean[forecastLength - 1];
                remaining -= throughput;
                week++;
            }

            completionWeeks = {
                mean: week,
                // Approximate percentiles based on P10 and P90 forecasts
                p50: week,
                p85: Math.round(week * 1.2), // Conservative estimate
                p90: Math.round(week * 1.3)  // More conservative
            };
        }

        let html = `
            <div class="metric-card">
                <p><strong>Mean Forecast:</strong> ${ensemble.mean.map(v => v.toFixed(1)).join(', ')}</p>
                <p><strong>P10 Range:</strong> ${ensemble.p10.map(v => v.toFixed(1)).join(', ')}</p>
                <p><strong>P90 Range:</strong> ${ensemble.p90.map(v => v.toFixed(1)).join(', ')}</p>`;

        if (completionWeeks && startDate) {
            // Calculate completion dates
            const start = moment(startDate);
            if (start.isValid()) {
                const date50 = start.clone().add(completionWeeks.p50, 'weeks').format('DD/MM/YYYY');
                const date85 = start.clone().add(completionWeeks.p85, 'weeks').format('DD/MM/YYYY');
                const date90 = start.clone().add(completionWeeks.p90, 'weeks').format('DD/MM/YYYY');

                html += `
                <hr>
                <p><strong>Mean Completion:</strong> ${completionWeeks.mean.toFixed(1)} weeks</p>
                <p><strong>50% Confidence:</strong> ${completionWeeks.p50} weeks (${date50})</p>
                <p><strong>85% Confidence:</strong> ${completionWeeks.p85} weeks (${date85})</p>
                <p><strong>90% Confidence:</strong> ${completionWeeks.p90} weeks (${date90})</p>`;
            }
        }

        html += `</div>`;
        $('#ml-summary').html(html);
    }

    function displayMCSummary(mcData, startDate) {
        const stats = mcData.percentile_stats;
        let html = `
            <div class="metric-card">
                <p><strong>Mean Completion:</strong> ${mcData.mean} weeks</p>`;

        if (startDate) {
            const start = moment(startDate);
            if (start.isValid()) {
                const date50 = start.clone().add(stats.p50, 'weeks').format('DD/MM/YYYY');
                const date85 = start.clone().add(stats.p85, 'weeks').format('DD/MM/YYYY');
                const date90 = start.clone().add(stats.p90, 'weeks').format('DD/MM/YYYY');

                html += `
                <p><strong>50% Confidence:</strong> ${stats.p50} weeks (${date50})</p>
                <p><strong>85% Confidence:</strong> ${stats.p85} weeks (${date85})</p>
                <p><strong>90% Confidence:</strong> ${stats.p90} weeks (${date90})</p>`;
            } else {
                html += `
                <p><strong>50% Confidence:</strong> ${stats.p50} weeks</p>
                <p><strong>85% Confidence:</strong> ${stats.p85} weeks</p>
                <p><strong>90% Confidence:</strong> ${stats.p90} weeks</p>`;
            }
        } else {
            html += `
                <p><strong>50% Confidence:</strong> ${stats.p50} weeks</p>
                <p><strong>85% Confidence:</strong> ${stats.p85} weeks</p>
                <p><strong>90% Confidence:</strong> ${stats.p90} weeks</p>`;
        }

        html += `</div>`;
        $('#mc-summary').html(html);
    }

    function clearWalkForwardCharts() {
        while (walkForwardCharts.length) {
            const chart = walkForwardCharts.pop();
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        }
    }

    function analyzeAndRankModels(results) {
        const models = [];

        for (const [modelName, data] of Object.entries(results)) {
            if (data.error || data.mae === undefined || data.mae === null) continue;

            models.push({
                name: modelName,
                mae: data.mae,
                rmse: data.rmse,
                r2: data.r2,
                mape: data.mape,
                smape: data.smape,
                median_ae: data.median_ae
            });
        }

        if (models.length === 0) return null;

        // Ranking por múltiplos critérios
        const rankings = {
            mae: [...models].sort((a, b) => a.mae - b.mae),
            rmse: [...models].sort((a, b) => a.rmse - b.rmse),
            mape: [...models].sort((a, b) => a.mape - b.mape),
            smape: [...models].sort((a, b) => a.smape - b.smape),
            r2: [...models].sort((a, b) => b.r2 - a.r2) // R² maior é melhor
        };

        // Sistema de pontuação: 1º lugar = n pontos, 2º = n-1, etc.
        const scores = {};
        models.forEach(m => scores[m.name] = 0);

        Object.values(rankings).forEach(ranking => {
            ranking.forEach((model, index) => {
                scores[model.name] += (models.length - index);
            });
        });

        // Encontrar o melhor modelo
        const bestModelName = Object.keys(scores).reduce((a, b) => scores[a] > scores[b] ? a : b);
        const bestModel = models.find(m => m.name === bestModelName);

        // Determinar critérios vencidos
        const criteria = [];
        if (rankings.mae[0].name === bestModelName) criteria.push('MAE');
        if (rankings.rmse[0].name === bestModelName) criteria.push('RMSE');
        if (rankings.mape[0].name === bestModelName) criteria.push('MAPE');
        if (rankings.smape[0].name === bestModelName) criteria.push('sMAPE');
        if (rankings.r2[0].name === bestModelName) criteria.push('R²');

        return {
            bestModel: bestModel,
            scores: scores,
            rankings: rankings,
            criteria: criteria
        };
    }

    function generateBestModelSummary(analysis) {
        if (!analysis) return '';

        const model = analysis.bestModel;
        const criteria = analysis.criteria;

        // Determinar qualidade do modelo baseado em MAPE
        let quality = '';
        let qualityClass = '';
        let recommendation = '';

        if (model.mape < 10) {
            quality = 'EXCELENTE';
            qualityClass = 'success';
            recommendation = 'Modelo altamente confiável para uso em produção.';
        } else if (model.mape < 20) {
            quality = 'BOM';
            qualityClass = 'success';
            recommendation = 'Modelo confiável. Recomendado para uso em produção.';
        } else if (model.mape < 30) {
            quality = 'RAZOÁVEL';
            qualityClass = 'warning';
            recommendation = 'Modelo aceitável, mas use como suporte ao Monte Carlo.';
        } else if (model.mape < 50) {
            quality = 'FRACO';
            qualityClass = 'warning';
            recommendation = 'Use apenas como referência. Priorize Monte Carlo.';
        } else {
            quality = 'INADEQUADO';
            qualityClass = 'danger';
            recommendation = 'NÃO recomendado. Use apenas Monte Carlo.';
        }

        // Verificar se R² é negativo
        const r2Warning = model.r2 < 0
            ? '<div class="alert alert-warning mt-2 mb-0 small">⚠️ <strong>R² negativo:</strong> O modelo está performando pior que simplesmente usar a média histórica. Considere coletar mais dados ou usar apenas Monte Carlo.</div>'
            : '';

        const precision = Math.round(100 - model.mape);

        return `
            <div class="card mb-3 border-${qualityClass}">
                <div class="card-header bg-${qualityClass} text-white">
                    <h5 class="mb-0">🏆 Melhor Modelo: ${model.name}</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="font-weight-bold">Métricas de Performance</h6>
                            <ul class="mb-0">
                                <li><strong>MAE:</strong> ${model.mae.toFixed(3)} (erro médio de ~${model.mae.toFixed(1)} item${model.mae >= 2 ? 's' : ''}/semana)</li>
                                <li><strong>MAPE:</strong> ${model.mape.toFixed(2)}% (precisão de ~${precision}%)</li>
                                <li><strong>RMSE:</strong> ${model.rmse.toFixed(3)}</li>
                                <li><strong>R²:</strong> ${model.r2.toFixed(3)} ${model.r2 < 0 ? '(⚠️ negativo)' : ''}</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="font-weight-bold">Análise</h6>
                            <p class="mb-1"><strong>Qualidade:</strong> <span class="badge badge-${qualityClass} badge-lg">${quality}</span></p>
                            <p class="mb-1"><strong>Critérios vencidos:</strong> ${criteria.length > 0 ? criteria.join(', ') : 'Pontuação geral'}</p>
                            <p class="mb-0"><strong>Recomendação:</strong> ${recommendation}</p>
                        </div>
                    </div>
                    ${r2Warning}
                </div>
            </div>
        `;
    }

    function displayWalkForwardResults(results, forecastSteps) {
        const $container = $('#walk-forward-results');
        const $metrics = $('#walk-forward-metrics');
        const $charts = $('#walk-forward-charts');

        clearWalkForwardCharts();
        $charts.empty();

        if (!results || Object.keys(results).length === 0) {
            $metrics.empty();
            $container.hide();
            return;
        }

        // Analisar e ranquear modelos
        const analysis = analyzeAndRankModels(results);
        const bestModelSummary = generateBestModelSummary(analysis);

        let metricsHtml = bestModelSummary;

        // Add scoring explanation
        if (analysis && Object.keys(analysis.scores).length > 1) {
            metricsHtml += `
                <div class="alert alert-info mb-3">
                    <h6 class="font-weight-bold mb-2">📊 Como o melhor modelo é escolhido?</h6>
                    <p class="small mb-2">O sistema utiliza um <strong>ranking multi-critério</strong> que avalia cada modelo em 5 métricas diferentes:</p>
                    <ul class="small mb-2">
                        <li><strong>MAE (Mean Absolute Error):</strong> Erro absoluto médio - menor é melhor</li>
                        <li><strong>RMSE (Root Mean Squared Error):</strong> Penaliza erros grandes - menor é melhor</li>
                        <li><strong>MAPE (Mean Absolute Percentage Error):</strong> Erro percentual - menor é melhor</li>
                        <li><strong>sMAPE (Symmetric MAPE):</strong> Erro percentual simétrico - menor é melhor</li>
                        <li><strong>R² (Coeficiente de Determinação):</strong> Qualidade do ajuste - maior é melhor (próximo de 1)</li>
                    </ul>
                    <p class="small mb-0"><strong>Sistema de pontuação:</strong> Cada modelo recebe pontos em cada critério (1º lugar = ${Object.keys(analysis.scores).length} pontos, 2º = ${Object.keys(analysis.scores).length - 1} pontos, etc.). O modelo com maior pontuação total é eleito o melhor. A coluna "Score" mostra a pontuação total de cada modelo.</p>
                </div>
            `;
        }

        metricsHtml += '<table class="table table-sm table-bordered"><thead class="thead-light"><tr>' +
            '<th>Modelo</th><th>MAE</th><th>RMSE</th><th>R²</th><th>MAPE</th><th>sMAPE</th><th>Mediana |Erro|</th><th>Origens</th><th>Pontos</th><th>Score</th>' +
            '</tr></thead><tbody>';

        let chartIndex = 0;
        for (const [modelName, data] of Object.entries(results)) {
            if (data.error) {
                metricsHtml += `<tr><td>${modelName}</td><td colspan="9">${data.error}</td></tr>`;
                continue;
            }

            const isBest = analysis && analysis.bestModel.name === modelName;
            const rowClass = isBest ? 'table-success font-weight-bold' : '';
            const badge = isBest ? ' 🏆' : '';
            const score = analysis ? analysis.scores[modelName] : '—';

            metricsHtml += `<tr class="${rowClass}">
                <td>${modelName}${badge}</td>
                <td>${data.mae !== undefined && data.mae !== null ? data.mae.toFixed(3) : '—'}</td>
                <td>${data.rmse !== undefined && data.rmse !== null ? data.rmse.toFixed(3) : '—'}</td>
                <td>${data.r2 !== undefined && data.r2 !== null ? data.r2.toFixed(3) : '—'}</td>
                <td>${data.mape !== undefined && data.mape !== null ? data.mape.toFixed(2) + '%' : '—'}</td>
                <td>${data.smape !== undefined && data.smape !== null ? data.smape.toFixed(2) + '%' : '—'}</td>
                <td>${data.median_ae !== undefined && data.median_ae !== null ? data.median_ae.toFixed(3) : '—'}</td>
                <td>${data.n_forecasts ?? '—'}</td>
                <td>${data.n_points ?? '—'}</td>
                <td><span class="badge badge-secondary">${score}</span></td>
            </tr>`;

            if (data.predictions && data.actuals && data.predictions.length && data.actuals.length) {
                const canvasId = `walk-forward-chart-${chartIndex}`;
                $charts.append(`
                    <div class="col-lg-6 mb-3">
                        <div class="chart-container" style="height:320px;">
                            <h5>${modelName}</h5>
                            <canvas id="${canvasId}"></canvas>
                        </div>
                    </div>
                `);

                const labels = data.indices && data.indices.length === data.actuals.length
                    ? data.indices.map(idx => idx + 1)
                    : data.actuals.map((_, idx) => idx + 1);
                const chart = new Chart(document.getElementById(canvasId).getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Realizado',
                                data: data.actuals,
                                borderColor: 'rgba(54, 162, 235, 1)',
                                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                                borderWidth: 2,
                                pointRadius: 2,
                                fill: false
                            },
                            {
                                label: 'Previsto',
                                data: data.predictions,
                                borderColor: 'rgba(255, 99, 132, 1)',
                                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                                borderWidth: 2,
                                pointRadius: 2,
                                borderDash: [5, 5],
                                fill: false
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: `Comparação previsto vs realizado (passo ${forecastSteps})`
                        },
                        tooltips: {
                            mode: 'index',
                            intersect: false
                        },
                        hover: {
                            mode: 'nearest',
                            intersect: true
                        },
                        scales: {
                            xAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Ponto da validação'
                                }
                            }],
                            yAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Itens por semana'
                                }
                            }]
                        }
                    }
                });

                walkForwardCharts.push(chart);
                chartIndex += 1;
            }
        }

        metricsHtml += '</tbody></table>';
        $metrics.html(metricsHtml);
        $container.show();
    }

    $('#runML').on('click', function() {
        const tpSamples = parseSamples($('#tpSamples').val());
        const forecastSteps = parseInt($('#forecastSteps').val());
        const startDate = $('#startDateAdv').val() || undefined;

        if (tpSamples.length < 8) {
            alert('Need at least 8 throughput samples for ML forecasting');
            return;
        }

        showLoading();
        clearWalkForwardCharts();
        $('#walk-forward-results').hide();
        clearWalkForwardCharts();
        $('#walk-forward-results').hide();

        if (window.renderInputStats) {
            window.renderInputStats('#advanced-input-stats', null, { showLeadTime: false });
        }

        $.ajax({
            url: '/api/ml-forecast',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tpSamples: tpSamples,
                forecastSteps: forecastSteps,
                model: 'ensemble',
                startDate: startDate
            }),
            success: function(data) {
                hideLoading();
                $('#results-container').show();
                $('#ml-results').show();
                $('#mc-results').hide();
                $('#comparison-results').hide();

                // Display results
                displayRiskAssessment(data.risk_assessment);
                displayModelPerformance(data.model_results);
                $('#ml-chart').attr('src', data.charts.ml_forecast);
                $('#history-chart').attr('src', data.charts.historical_analysis);
                displayWalkForwardResults(data.walk_forward, forecastSteps);

                if (window.renderInputStats) {
                    window.renderInputStats('#advanced-input-stats', null, { showLeadTime: false });
                }
            },
            error: function(xhr) {
                displayError(xhr.responseJSON?.error || 'Unknown error occurred');
            }
        });
    });

    $('#runCombined').on('click', function() {
        const tpSamples = parseSamples($('#tpSamples').val());
        const forecastSteps = parseInt($('#forecastSteps').val());
        const backlog = parseInt($('#backlog').val());
        const nSimulations = parseInt($('#nSimulations').val());
        const startDate = $('#startDateAdv').val() || undefined;

        if (tpSamples.length < 8) {
            alert('Need at least 8 throughput samples for combined forecasting');
            return;
        }

        if (backlog <= 0) {
            alert('Backlog must be greater than zero');
            return;
        }

        showLoading();

        $.ajax({
            url: '/api/combined-forecast',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                tpSamples: tpSamples,
                forecastSteps: forecastSteps,
                backlog: backlog,
                nSimulations: nSimulations,
                startDate: startDate
            }),
            success: function(data) {
                hideLoading();
                $('#results-container').show();
                $('#ml-results').show();
                $('#mc-results').show();
                $('#comparison-results').show();

                // Display ML results
                displayRiskAssessment(data.ml.risk_assessment);

                // Display model performance if available
                if (data.ml.model_results) {
                    displayModelPerformance(data.ml.model_results);
                }

                $('#ml-chart').attr('src', data.charts.ml_forecast);
                $('#history-chart').attr('src', data.charts.ml_forecast);

                // Display MC results
                displayMCStats(data.monte_carlo);
                $('#mc-chart').attr('src', data.charts.monte_carlo);

                // Display comparison
                $('#comparison-chart').attr('src', data.charts.comparison);
                displayMLSummary(data.ml, backlog, startDate);
                displayMCSummary(data.monte_carlo, startDate);
                displayWalkForwardResults(data.ml.walk_forward, forecastSteps);

                if (window.renderInputStats) {
                    window.renderInputStats('#advanced-input-stats', data.monte_carlo.input_stats, {
                        showLeadTime: false
                    });
                }
            },
            error: function(xhr) {
                displayError(xhr.responseJSON?.error || 'Unknown error occurred');
            }
        });
    });

    $('.scroll-to-throughput').on('click', function(e) {
        e.preventDefault();
        const $target = $('#tpSamples');
        if ($target.length) {
            $('html, body').animate({ scrollTop: $target.offset().top - 70 }, 300);
            $target.focus();
        }
    });
});
