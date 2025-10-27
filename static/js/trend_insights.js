'use strict';

(function ($) {
    function parseThroughputSamples() {
        const raw = $('#tpSamples').val() || '';
        if (!raw.trim()) return [];
        return raw
            .split(/[\s,;|\n]+/)
            .map(token => token.trim())
            .filter(token => token.length > 0)
            .map(token => Number(token.replace(',', '.')))
            .filter(value => Number.isFinite(value) && value >= 0);
    }

    function formatNumber(value, decimals = 2) {
        if (!Number.isFinite(value)) return '—';
        return value.toLocaleString('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    function formatPercent(value, decimals = 1) {
        if (!Number.isFinite(value)) return '—';
        return `${formatNumber(value, decimals)}%`;
    }

    function setStatusClass($element, status) {
        $element.removeClass('text-success text-danger text-warning text-secondary text-info');
        if (status === 'improving') {
            $element.addClass('text-success');
        } else if (status === 'declining') {
            $element.addClass('text-danger');
        } else if (status === 'stable') {
            $element.addClass('text-secondary');
        } else {
            $element.addClass('text-info');
        }
    }

    function describeDirection(direction) {
        switch ((direction || '').toLowerCase()) {
            case 'improving':
                return 'Melhorando';
            case 'declining':
                return 'Piorando';
            case 'stable':
                return 'Estável';
            default:
                return 'Indefinido';
        }
    }

    function summarizeTrend(trend, summary) {
        const $statusValue = $('#trend-status-value');
        $statusValue.text(describeDirection(trend.trend_direction));
        setStatusClass($statusValue, trend.trend_direction);

        const healthBadges = [];
        if (summary && typeof summary.is_healthy === 'boolean') {
            healthBadges.push(summary.is_healthy ? 'Processo saudável' : 'Processo precisa de atenção');
        }
        if (summary && summary.requires_attention) {
            healthBadges.push('Alertas críticos detectados');
        }
        if (trend.mann_kendall_tau !== null && trend.mann_kendall_tau !== undefined) {
            const tau = formatNumber(trend.mann_kendall_tau, 3);
            healthBadges.push(`Tau de Mann-Kendall: ${tau}`);
        }
        $('#trend-status-detail').text(healthBadges.join(' · ') || '—');

        const change = trend.change_pct;
        $('#trend-change-value').text(formatPercent(change));
        const changeDetail = `Recentes: ${formatNumber(trend.recent_avg)} · Históricos: ${formatNumber(trend.historical_avg)}`;
        $('#trend-change-detail').text(changeDetail);

        const confidencePct = trend.confidence_level ? formatPercent(trend.confidence_level * 100, 1) : '—';
        $('#trend-confidence-value').text(confidencePct);
        $('#trend-confidence-detail').text(trend.is_significant ? 'Tendência estatisticamente significativa' : 'Sem significância estatística');

        const volatility = trend.volatility;
        $('#trend-volatility-value').text(formatNumber(volatility));
        $('#trend-volatility-detail').text('Desvio padrão das últimas observações');
    }

    function renderSeasonality(seasonality) {
        const $container = $('#trend-seasonality-content');
        if (!seasonality) {
            $container.html('<p class="text-muted mb-0">Dados insuficientes para identificar sazonalidade. Forneça ao menos 8 amostras.</p>');
            return;
        }

        if (!seasonality.has_seasonality) {
            $container.html('<p class="mb-0 text-success"><i class="fas fa-check-circle"></i> Nenhum padrão sazonal forte detectado.</p>');
            return;
        }

        const items = [];
        if (seasonality.period) {
            items.push(`<li>Período dominante: ${seasonality.period} observações</li>`);
        }
        if (Array.isArray(seasonality.dominant_periods) && seasonality.dominant_periods.length) {
            items.push(`<li>Outros períodos relevantes: ${seasonality.dominant_periods.join(', ')}</li>`);
        }
        items.push(`<li>Força da sazonalidade: ${formatPercent(seasonality.seasonal_strength * 100 || 0, 1)}</li>`);
        items.push(`<li>Confiança combinada: ${formatPercent(seasonality.seasonality_confidence * 100 || 0, 1)}</li>`);

        if (seasonality.patterns && seasonality.patterns.end_period_drop) {
            items.push('<li class="text-danger font-weight-bold">Queda recorrente no fim do ciclo detectada</li>');
        }

        $container.html(`
            <p class="mb-2 text-success"><i class="fas fa-wave-square"></i> Padrões sazonais detectados.</p>
            <ul class="mb-0 pl-3">${items.join('')}</ul>
        `);
    }

    function renderAnomalies(anomalies, trend) {
        const $container = $('#trend-anomalies-content');
        if (!anomalies) {
            $container.html('<p class="text-muted mb-0">Nenhuma análise de anomalias disponível.</p>');
            return;
        }

        const parts = [];
        const method = anomalies.method_used ? String(anomalies.method_used).toUpperCase() : '—';
        parts.push(`<li><strong>Total de outliers:</strong> ${anomalies.anomalies_count}</li>`);
        parts.push(`<li><strong>Método:</strong> ${method}</li>`);
        parts.push(`<li><strong>Faixa esperada:</strong> ${formatNumber(anomalies.lower_bound)} — ${formatNumber(anomalies.upper_bound)}</li>`);
        if (anomalies.recent_anomaly) {
            const severity = anomalies.latest_anomaly_score !== null && anomalies.latest_anomaly_score !== undefined
                ? ` (score ${formatNumber(anomalies.latest_anomaly_score, 2)})`
                : '';
            parts.push(`<li class="text-danger font-weight-bold"><i class="fas fa-exclamation-circle"></i> Última observação marcada como anômala${severity}</li>`);
        }
        if (trend && Number.isFinite(trend.trend_strength)) {
            parts.push(`<li><strong>Força da tendência:</strong> ${formatPercent(trend.trend_strength * 100 || 0, 1)}</li>`);
        }

        $container.html(`<ul class="mb-0 pl-3">${parts.join('')}</ul>`);
    }

    function renderProjections(projections) {
        const $tbody = $('#trend-projections-table tbody');
        $tbody.empty();

        if (!Array.isArray(projections) || !projections.length) {
            $tbody.append('<tr><td colspan="5" class="text-center text-muted">Nenhuma projeção calculada.</td></tr>');
            $('#trend-projection-horizon').text('—');
            return;
        }

        const horizon = projections[0].projected_values ? projections[0].projected_values.length : 0;
        $('#trend-projection-horizon').text(horizon ? `Horizonte de ${horizon} períodos` : '—');

        projections.forEach((projection) => {
            const afterFour = projection.projected_values && projection.projected_values.length >= 4
                ? formatNumber(projection.projected_values[3])
                : '—';
            const note = projection.notes || '—';
            const target = projection.time_to_target
                ? `${projection.time_to_target} períodos`
                : 'Não atinge a meta';
            $tbody.append(`
                <tr>
                    <td>${projection.scenario_name}</td>
                    <td>${formatPercent(projection.improvement_rate, 0)}</td>
                    <td>${afterFour}</td>
                    <td>${target}</td>
                    <td>${note}</td>
                </tr>
            `);
        });
    }

    function renderAlerts(alerts) {
        const $list = $('#trend-alerts-list');
        $list.empty();

        if (!Array.isArray(alerts) || !alerts.length) {
            $list.append('<div class="list-group-item text-success"><i class="fas fa-smile-beam"></i> Nenhum alerta gerado. Tendência sob controle.</div>');
            return;
        }

        const severityClass = {
            critical: 'list-group-item-danger',
            high: 'list-group-item-warning',
            medium: 'list-group-item-info',
            low: 'list-group-item-success',
            improvement: 'list-group-item-success'
        };

        alerts.forEach((alert) => {
            const cssClass = severityClass[alert.severity] || 'list-group-item-info';
            const deviation = Number.isFinite(alert.deviation_pct) ? formatPercent(alert.deviation_pct, 1) : '—';
            $list.append(`
                <div class="list-group-item ${cssClass}">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <strong>${alert.message}</strong>
                        <span class="badge badge-light text-uppercase">${alert.alert_type}</span>
                    </div>
                    <p class="mb-1 text-muted">
                        Valor atual: ${formatNumber(alert.current_value)} · Esperado: ${formatNumber(alert.expected_value)} · Desvio: ${deviation}
                    </p>
                    <small class="text-dark">${alert.recommendation || 'Sem recomendação específica.'}</small>
                </div>
            `);
        });
    }

    function showError(message) {
        $('#trend-analysis-error').text(message).removeClass('d-none');
    }

    function clearError() {
        $('#trend-analysis-error').addClass('d-none').text('');
    }

    function toggleLoading(isLoading) {
        $('#trend-analysis-loading').toggleClass('d-none', !isLoading);
        $('#trend-analysis-results').toggleClass('d-none', isLoading);
    }

    function runTrendAnalysis() {
        clearError();
        const samples = parseThroughputSamples();

        if (samples.length < 3) {
            showError('Informe pelo menos 3 amostras de throughput para detectar tendências.');
            $('#trend-analysis-results').addClass('d-none');
            $('#trend-analysis-loading').addClass('d-none');
            return;
        }

        toggleLoading(true);

        fetch('/api/trend-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tpSamples: samples,
                metricName: 'throughput'
            })
        })
            .then(async (response) => {
                if (!response.ok) {
                    const payload = await response.json().catch(() => ({}));
                    const message = payload.error || 'Falha ao calcular análise de tendências.';
                    throw new Error(message);
                }
                return response.json();
            })
            .then((result) => {
                toggleLoading(false);
                if (result.error) {
                    showError(result.error);
                    $('#trend-analysis-results').addClass('d-none');
                    return;
                }
                $('#trend-analysis-results').removeClass('d-none');
                summarizeTrend(result.trend || {}, result.summary || {});
                renderSeasonality(result.seasonality || null);
                renderAnomalies(result.anomalies || null, result.trend || {});
                renderProjections(result.projections || []);
                renderAlerts(result.alerts || []);
            })
            .catch((error) => {
                toggleLoading(false);
                $('#trend-analysis-results').addClass('d-none');
                showError(error.message || 'Erro inesperado ao calcular análise de tendências.');
            });
    }

    $(document).on('click', '#runTrendAnalysisBtn', runTrendAnalysis);
})(jQuery);
