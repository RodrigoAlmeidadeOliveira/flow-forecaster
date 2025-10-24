$(function () {
    function parseDateInput(text) {
        if (!text) return [];
        return text
            .split(/[\n,;]+/)
            .map(s => s.trim())
            .filter(Boolean);
    }

    function showError(message) {
        if (!message) {
            $('#demand-forecast-error').hide().text('');
            return;
        }
        $('#demand-forecast-error').text(message).show();
    }

    function setLoading(isLoading) {
        if (isLoading) {
            $('#demand-forecast-loading').show();
            $('#demand-forecast-results').hide();
        } else {
            $('#demand-forecast-loading').hide();
        }
    }

    function formatNumber(value, decimals = 2) {
        if (value === null || value === undefined || Number.isNaN(value)) {
            return '—';
        }
        return Number(value).toFixed(decimals);
    }

    const weekdayNames = [
        'Segunda-feira',
        'Terça-feira',
        'Quarta-feira',
        'Quinta-feira',
        'Sexta-feira',
        'Sábado',
        'Domingo'
    ];

    function renderWeekdayProfile(profile) {
        if (!Array.isArray(profile) || profile.length === 0) {
            return '<div class="alert alert-warning">Sem dados suficientes para o perfil semanal.</div>';
        }

        const rows = profile.map(item => {
            const label = weekdayNames[item.weekday_index] || `Dia ${item.weekday_index}`;
            return `
                <tr>
                    <th scope="row">${label}</th>
                    <td>${formatNumber(item.mean, 2)}</td>
                    <td>${formatNumber(item.std, 2)}</td>
                    <td>${formatNumber(item.max, 2)}</td>
                    <td>${formatNumber(item.total, 2)}</td>
                    <td>${item.count_days}</td>
                </tr>
            `;
        }).join('');

        return `
            <div class="table-responsive">
                <table class="table table-sm table-striped table-hover mb-0">
                    <thead class="thead-light">
                        <tr>
                            <th>Dia da semana</th>
                            <th>Média</th>
                            <th>Desvio</th>
                            <th>Pico</th>
                            <th>Total</th>
                            <th>Dias analisados</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    }

    function renderHistory(summary) {
        if (!summary) {
            return '<div class="alert alert-info">Informe as datas para visualizar o resumo histórico.</div>';
        }

        return `
            <div class="row">
                <div class="col-md-3">
                    <div class="metric-card">
                        <strong>Intervalo:</strong><br>
                        ${summary.start_date} → ${summary.end_date}
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <strong>Total de itens:</strong><br>
                        ${summary.total_events}
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <strong>Média diária:</strong><br>
                        ${formatNumber(summary.mean_per_day, 2)}
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <strong>Pico diário:</strong><br>
                        ${formatNumber(summary.max_per_day, 2)}
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <h5 class="font-weight-bold">Perfil por dia da semana</h5>
                ${renderWeekdayProfile(summary.weekday_profile)}
            </div>
        `;
    }

    function renderRisk(risk) {
        if (!risk) {
            return '<div class="alert alert-secondary">Sem avaliação de risco disponível.</div>';
        }

        const riskClass = risk.risk_level === 'HIGH'
            ? 'risk-high'
            : risk.risk_level === 'MEDIUM'
                ? 'risk-medium'
                : 'risk-low';

        return `
            <div class="metric-card">
                <p><strong>Nível:</strong> <span class="${riskClass}">${risk.risk_level}</span></p>
                <p><strong>Volatilidade (CV):</strong> ${formatNumber(risk.volatility_cv, 2)}</p>
                <p><strong>Desvio de tendência:</strong> ${formatNumber(risk.trend_deviation_pct, 1)}%</p>
                <p><strong>Outliers:</strong> ${formatNumber(risk.outlier_pct, 1)}%</p>
                ${risk.warning ? `<p class="text-warning font-weight-bold mb-0">${risk.warning}</p>` : ''}
            </div>
        `;
    }

    function renderModelPerformance(models) {
        if (!Array.isArray(models) || models.length === 0) {
            return '<div class="alert alert-warning">Sem métricas de modelos treinados.</div>';
        }

        const rows = models.map(model => `
            <tr>
                <td>${model.model}</td>
                <td>${formatNumber(model.mae, 2)}</td>
                <td>${formatNumber(model.rmse, 2)}</td>
                <td>${formatNumber(model.mae_percent, 1)}%</td>
                <td>${model.r2_mean !== undefined ? formatNumber(model.r2_mean, 3) : '—'}</td>
            </tr>
        `).join('');

        return `
            <div class="table-responsive">
                <table class="table table-sm table-striped mb-0">
                    <thead class="thead-dark">
                        <tr>
                            <th>Modelo</th>
                            <th>MAE</th>
                            <th>RMSE</th>
                            <th>MAE %</th>
                            <th>R² (CV)</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    }

    function renderForecastTable(forecast) {
        if (!forecast) {
            return '<div class="alert alert-info">Sem forecast disponível.</div>';
        }

        const ensemble = forecast.ensemble || {};
        const dates = forecast.dates || [];
        const mean = ensemble.mean || [];
        const p10 = ensemble.p10 || [];
        const p90 = ensemble.p90 || [];

        const rows = dates.map((date, index) => `
            <tr>
                <th scope="row">${date}</th>
                <td>${formatNumber(p10[index] ?? null, 2)}</td>
                <td>${formatNumber(mean[index] ?? null, 2)}</td>
                <td>${formatNumber(p90[index] ?? null, 2)}</td>
            </tr>
        `).join('');

        const summary = forecast.summary || {};

        return `
            <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                    <thead class="thead-light">
                        <tr>
                            <th>Data</th>
                            <th>P10</th>
                            <th>Média</th>
                            <th>P90</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
            <div class="alert alert-info mt-3 mb-0">
                <strong>Total previsto (média):</strong> ${formatNumber(summary.total_mean, 2)} |
                <strong>P10:</strong> ${formatNumber(summary.total_p10, 2)} |
                <strong>P90:</strong> ${formatNumber(summary.total_p90, 2)}
            </div>
        `;
    }

    $('#runDemandForecast').on('click', function () {
        showError('');

        const rawText = $('#demandDates').val();
        const dates = parseDateInput(rawText);

        if (dates.length === 0) {
            showError('Informe pelo menos uma data (uma por linha).');
            return;
        }

        const payload = {
            dates: dates,
            forecastDays: Number($('#demandForecastDays').val()) || 14,
            forecastWeeks: Number($('#demandForecastWeeks').val()) || 8,
            excludeWeekends: $('#demandExcludeWeekends').is(':checked')
        };

        setLoading(true);

        fetch('/api/demand/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Falha ao gerar o forecasting de demanda.');
                }
                return data;
            })
            .then(data => {
                $('#demand-history-summary').html(renderHistory(data.history));

                if (data.charts && data.charts.daily) {
                    $('#demand-daily-chart').attr('src', data.charts.daily);
                    $('#demand-daily-chart-container').show();
                } else {
                    $('#demand-daily-chart-container').hide();
                }

                if (data.charts && data.charts.weekly) {
                    $('#demand-weekly-chart').attr('src', data.charts.weekly);
                    $('#demand-weekly-chart-container').show();
                } else {
                    $('#demand-weekly-chart-container').hide();
                }

                const dailyForecast = data.daily_forecast || null;
                $('#demand-daily-risk').html(renderRisk(dailyForecast ? dailyForecast.risk : null));
                $('#demand-daily-table').html(renderForecastTable(dailyForecast));
                $('#demand-model-performance').html(renderModelPerformance(dailyForecast ? dailyForecast.model_results : []));

                const weeklyForecast = data.weekly_forecast || null;
                if (weeklyForecast) {
                    $('#demand-weekly-risk').html(renderRisk(weeklyForecast.risk));
                    $('#demand-weekly-table').html(renderForecastTable(weeklyForecast));
                    $('#demand-weekly-panels').show();
                    $('#demand-weekly-table-wrapper').show();
                } else {
                    $('#demand-weekly-panels').hide();
                    $('#demand-weekly-table-wrapper').hide();
                }

                setLoading(false);
                $('#demand-forecast-results').show();
            })
            .catch(error => {
                setLoading(false);
                $('#demand-forecast-results').hide();
                showError(error.message || 'Erro inesperado ao processar o forecasting.');
            });
    });
});
