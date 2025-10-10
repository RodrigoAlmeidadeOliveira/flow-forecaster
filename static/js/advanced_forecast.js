$(document).ready(function() {
    function parseSamples(text) {
        if (!text || text.trim().length === 0) return [];
        return text.split(/[\s\n,]/)
            .map(s => s.trim())
            .filter(s => s.length > 0)
            .map(s => parseFloat(s))
            .filter(n => !isNaN(n) && n >= 0);
    }

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
        let html = '<table class="table table-sm table-striped"><thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAE %</th></tr></thead><tbody>';
        models.forEach(model => {
            html += `<tr>
                <td>${model.model}</td>
                <td>${model.mae}</td>
                <td>${model.rmse}</td>
                <td>${model.mae_percent}%</td>
            </tr>`;
        });
        html += '</tbody></table>';
        $('#model-performance').html(html);
    }

    function displayMCStats(stats) {
        let html = `
            <div class="row">
                <div class="col-md-3"><div class="metric-card"><strong>Mean:</strong> ${stats.mean} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>Std Dev:</strong> ${stats.std} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P50:</strong> ${stats.p50} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P85:</strong> ${stats.p85} weeks</div></div>
            </div>
            <div class="row">
                <div class="col-md-3"><div class="metric-card"><strong>P10:</strong> ${stats.p10} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P25:</strong> ${stats.p25} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P75:</strong> ${stats.p75} weeks</div></div>
                <div class="col-md-3"><div class="metric-card"><strong>P90:</strong> ${stats.p90} weeks</div></div>
            </div>
        `;
        $('#mc-stats').html(html);
    }

    function displayMLSummary(mlData) {
        const ensemble = mlData.ensemble;
        let html = `
            <div class="metric-card">
                <p><strong>Mean Forecast:</strong> ${ensemble.mean.map(v => v.toFixed(1)).join(', ')}</p>
                <p><strong>P10 Range:</strong> ${ensemble.p10.map(v => v.toFixed(1)).join(', ')}</p>
                <p><strong>P90 Range:</strong> ${ensemble.p90.map(v => v.toFixed(1)).join(', ')}</p>
            </div>
        `;
        $('#ml-summary').html(html);
    }

    function displayMCSummary(mcData) {
        const stats = mcData.percentile_stats;
        let html = `
            <div class="metric-card">
                <p><strong>Mean Completion:</strong> ${mcData.mean} weeks</p>
                <p><strong>50% Confidence:</strong> ${stats.p50} weeks</p>
                <p><strong>85% Confidence:</strong> ${stats.p85} weeks</p>
                <p><strong>90% Confidence:</strong> ${stats.p90} weeks</p>
            </div>
        `;
        $('#mc-summary').html(html);
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
                $('#ml-chart').attr('src', data.charts.ml_forecast);
                $('#history-chart').attr('src', data.charts.ml_forecast);

                // Display MC results
                displayMCStats(data.monte_carlo.percentile_stats);
                $('#mc-chart').attr('src', data.charts.monte_carlo);

                // Display comparison
                $('#comparison-chart').attr('src', data.charts.comparison);
                displayMLSummary(data.ml);
                displayMCSummary(data.monte_carlo);
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
