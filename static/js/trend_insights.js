'use strict';

(function ($) {
    const METRIC_CONFIG = {
        throughput: {
            container: '#throughput-metric-section',
            statusValue: '#trend-status-value',
            statusDetail: '#trend-status-detail',
            changeValue: '#trend-change-value',
            changeDetail: '#trend-change-detail',
            confidenceValue: '#trend-confidence-value',
            confidenceDetail: '#trend-confidence-detail',
            volatilityValue: '#trend-volatility-value',
            volatilityDetail: '#trend-volatility-detail',
            seasonalityContent: '#trend-seasonality-content',
            anomaliesContent: '#trend-anomalies-content',
            projectionsTableBody: '#trend-projections-table tbody',
            projectionHorizon: '#trend-projection-horizon',
            alertsList: '#trend-alerts-list',
            noAlertsMessage: '<div class="list-group-item text-success"><i class="fas fa-smile-beam"></i> Nenhum alerta gerado. Tendência sob controle.</div>',
            projectionsEmptyRow: '<tr><td colspan="5" class="text-center text-muted">Nenhuma projeção calculada.</td></tr>',
            seasonalityDefaultMessage: 'Execute a análise para detectar padrões sazonais.',
            seasonalityInsufficientMessage: 'Dados insuficientes para identificar sazonalidade. Forneça ao menos 8 amostras.',
            anomaliesDefaultMessage: 'Nenhuma análise de anomalias disponível.',
            volatilityDetailDefault: 'Desvio padrão das últimas observações'
        },
        lead_time: {
            container: '#lead-time-metric-section',
            statusValue: '#lt-trend-status-value',
            statusDetail: '#lt-trend-status-detail',
            changeValue: '#lt-trend-change-value',
            changeDetail: '#lt-trend-change-detail',
            confidenceValue: '#lt-trend-confidence-value',
            confidenceDetail: '#lt-trend-confidence-detail',
            volatilityValue: '#lt-trend-volatility-value',
            volatilityDetail: '#lt-trend-volatility-detail',
            seasonalityContent: '#lt-trend-seasonality-content',
            anomaliesContent: '#lt-trend-anomalies-content',
            projectionsTableBody: '#lt-trend-projections-table tbody',
            projectionHorizon: '#lt-trend-projection-horizon',
            alertsList: '#lt-trend-alerts-list',
            noAlertsMessage: '<div class="list-group-item text-success"><i class="fas fa-smile-beam"></i> Nenhum alerta gerado. Tendência sob controle.</div>',
            projectionsEmptyRow: '<tr><td colspan="5" class="text-center text-muted">Nenhuma projeção calculada.</td></tr>',
            seasonalityDefaultMessage: 'Informe tempos de lead para identificar padrões sazonais.',
            seasonalityInsufficientMessage: 'Dados insuficientes para identificar sazonalidade. Forneça ao menos 8 amostras.',
            anomaliesDefaultMessage: 'Nenhuma análise de anomalias disponível.',
            volatilityDetailDefault: 'Desvio padrão das últimas observações'
        }
    };

    function parseSamplesFrom(selector) {
        const raw = ($(selector).val() || '').trim();
        if (!raw) return [];
        return raw
            .split(/[\s,;|\n]+/)
            .map(token => token.trim())
            .filter(token => token.length > 0)
            .map(token => Number(token.replace(',', '.')))
            .filter(value => Number.isFinite(value));
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

    function summarizeTrend(trend, summary, config, higherIsBetter) {
        const polarity = typeof higherIsBetter === 'boolean' ? higherIsBetter : true;
        const $statusValue = $(config.statusValue);
        const direction = describeDirection(trend.trend_direction);
        $statusValue.text(direction);
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
        healthBadges.push(polarity ? 'Objetivo: aumentar a métrica' : 'Objetivo: reduzir a métrica');
        $(config.statusDetail).text(healthBadges.join(' · ') || '—');

        if (Number.isFinite(trend.change_pct)) {
            $(config.changeValue).text(formatPercent(trend.change_pct));
        } else {
            $(config.changeValue).text('—');
        }
        const changeDetail = (Number.isFinite(trend.recent_avg) && Number.isFinite(trend.historical_avg))
            ? `Recentes: ${formatNumber(trend.recent_avg)} · Históricos: ${formatNumber(trend.historical_avg)}`
            : '—';
        $(config.changeDetail).text(changeDetail);

        const confidencePct = Number.isFinite(trend.confidence_level)
            ? formatPercent(trend.confidence_level * 100, 1)
            : '—';
        $(config.confidenceValue).text(confidencePct);
        $(config.confidenceDetail).text(trend.is_significant ? 'Tendência estatisticamente significativa' : 'Sem significância estatística');

        $(config.volatilityValue).text(Number.isFinite(trend.volatility) ? formatNumber(trend.volatility) : '—');
        $(config.volatilityDetail).text(config.volatilityDetailDefault || 'Desvio padrão das últimas observações');
    }

    function renderSeasonality(seasonality, config) {
        const $container = $(config.seasonalityContent);
        if (!seasonality) {
            $container.html(`<p class="text-muted mb-0">${config.seasonalityDefaultMessage || 'Execute a análise para detectar padrões sazonais.'}</p>`);
            return;
        }

        if (!seasonality.has_seasonality) {
            const insufficientData = !seasonality.period && (!seasonality.dominant_periods || !seasonality.dominant_periods.length);
            if (insufficientData) {
                $container.html(`<p class="text-muted mb-0">${config.seasonalityInsufficientMessage || config.seasonalityDefaultMessage || 'Dados insuficientes para identificar sazonalidade.'}</p>`);
            } else {
                $container.html('<p class="mb-0 text-success"><i class="fas fa-check-circle"></i> Nenhum padrão sazonal forte detectado.</p>');
            }
            return;
        }

        const items = [];
        if (seasonality.period) {
            items.push(`<li>Período dominante: ${seasonality.period} observações</li>`);
        }
        if (Array.isArray(seasonality.dominant_periods) && seasonality.dominant_periods.length) {
            items.push(`<li>Outros períodos relevantes: ${seasonality.dominant_periods.join(', ')}</li>`);
        }
        items.push(`<li>Força da sazonalidade: ${formatPercent((seasonality.seasonal_strength || 0) * 100, 1)}</li>`);
        items.push(`<li>Confiança combinada: ${formatPercent((seasonality.seasonality_confidence || 0) * 100, 1)}</li>`);

        $container.html(`
            <p class="mb-2 text-success"><i class="fas fa-wave-square"></i> Padrões sazonais detectados.</p>
            <ul class="mb-0 pl-3">${items.join('')}</ul>
        `);
    }

    function renderAnomalies(anomalies, trend, config) {
        const $container = $(config.anomaliesContent);
        if (!anomalies) {
            $container.html(`<p class="text-muted mb-0">${config.anomaliesDefaultMessage || 'Nenhuma análise de anomalias disponível.'}</p>`);
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
            parts.push(`<li><strong>Força da tendência:</strong> ${formatPercent((trend.trend_strength || 0) * 100, 1)}</li>`);
        }

        $container.html(`<ul class="mb-0 pl-3">${parts.join('')}</ul>`);
    }

    function renderProjections(projections, config) {
        const $tbody = $(config.projectionsTableBody);
        $tbody.empty();

        if (!Array.isArray(projections) || !projections.length) {
            $tbody.append(config.projectionsEmptyRow || '<tr><td colspan="5" class="text-center text-muted">Nenhuma projeção calculada.</td></tr>');
            $(config.projectionHorizon).text('—');
            return;
        }

        const horizon = projections[0].projected_values ? projections[0].projected_values.length : 0;
        $(config.projectionHorizon).text(horizon ? `Horizonte de ${horizon} períodos` : '—');

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

    function renderAlerts(alerts, config) {
        const $list = $(config.alertsList);
        $list.empty();

        if (!Array.isArray(alerts) || !alerts.length) {
            $list.html(config.noAlertsMessage || '<div class="list-group-item text-success"><i class="fas fa-smile-beam"></i> Nenhum alerta gerado. Tendência sob controle.</div>');
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

    function resetMetricSection(config) {
        $(config.statusValue).text('—');
        $(config.statusDetail).text('—');
        $(config.changeValue).text('—');
        $(config.changeDetail).text('—');
        $(config.confidenceValue).text('—');
        $(config.confidenceDetail).text('Aguardando análise');
        $(config.volatilityValue).text('—');
        $(config.volatilityDetail).text(config.volatilityDetailDefault || 'Desvio padrão das últimas observações');
        renderSeasonality(null, config);
        renderAnomalies(null, null, config);
        renderProjections([], config);
        renderAlerts([], config);
        $(config.projectionHorizon).text('—');
        $(config.container).addClass('d-none');
    }

    function showMetric(metricData) {
        const key = (metricData.metric_key || metricData.metric_name || '').toLowerCase();
        const config = METRIC_CONFIG[key];
        if (!config) return;

        const trend = metricData.trend || {};
        const summary = metricData.summary || {};
        const polarity = typeof metricData.higher_is_better === 'boolean'
            ? metricData.higher_is_better
            : trend.higher_is_better;

        resetMetricSection(config);
        summarizeTrend(trend, summary, config, polarity);
        renderSeasonality(metricData.seasonality || null, config);
        renderAnomalies(metricData.anomalies || null, trend, config);
        renderProjections(metricData.projections || [], config);
        renderAlerts(metricData.alerts || [], config);
        $(config.container).removeClass('d-none');
    }

    function hideAllMetricSections() {
        Object.values(METRIC_CONFIG).forEach(resetMetricSection);
    }

    function showFeedback(message, type = 'danger') {
        const $alert = $('#trend-analysis-error');
        $alert.removeClass('d-none alert-danger alert-warning alert-info');
        $alert.addClass(`alert-${type}`);
        $alert.text(message);
    }

    function clearFeedback() {
        const $alert = $('#trend-analysis-error');
        $alert.addClass('d-none').removeClass('alert-warning alert-info');
        if (!$alert.hasClass('alert-danger')) {
            $alert.addClass('alert-danger');
        }
        $alert.text('');
    }

    function toggleLoading(isLoading) {
        if (isLoading) {
            $('#trend-analysis-results').addClass('d-none');
        }
        $('#trend-analysis-loading').toggleClass('d-none', !isLoading);
    }

    function runTrendAnalysis() {
        clearFeedback();
        const throughputSamples = parseSamplesFrom('#tpSamples');
        const leadTimeSamples = parseSamplesFrom('#ltSamples');

        if (throughputSamples.length < 3 && leadTimeSamples.length < 3) {
            showFeedback('Informe pelo menos 3 amostras de throughput ou de tempo de lead para detectar tendências.');
            $('#trend-analysis-results').addClass('d-none');
            return;
        }

        hideAllMetricSections();
        toggleLoading(true);

        const payload = { metricName: 'throughput' };
        if (throughputSamples.length) {
            payload.tpSamples = throughputSamples;
        }
        if (leadTimeSamples.length) {
            payload.ltSamples = leadTimeSamples;
        }

        fetch('/api/trend-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(async (response) => {
                if (!response.ok) {
                    const payloadError = await response.json().catch(() => ({}));
                    const message = payloadError.error || 'Falha ao calcular análise de tendências.';
                    throw new Error(message);
                }
                return response.json();
            })
            .then((result) => {
                toggleLoading(false);
                if (result.error) {
                    showFeedback(result.error);
                    $('#trend-analysis-results').addClass('d-none');
                    return;
                }

                const metricsArray = Array.isArray(result.metrics) ? result.metrics : [];
                const metricMap = {};
                metricsArray.forEach((metric) => {
                    const key = (metric.metric_key || metric.metric_name || '').toLowerCase();
                    metricMap[key] = metric;
                });

                let displayed = false;

                if (metricMap.throughput) {
                    showMetric(metricMap.throughput);
                    displayed = true;
                } else if (result.metric_name && result.metric_name.toLowerCase() === 'throughput' && result.trend) {
                    showMetric({
                        metric_key: 'throughput',
                        metric_name: result.metric_name,
                        trend: result.trend,
                        seasonality: result.seasonality,
                        anomalies: result.anomalies,
                        projections: result.projections,
                        alerts: result.alerts,
                        summary: result.summary,
                        higher_is_better: result.higher_is_better
                    });
                    displayed = true;
                } else {
                    resetMetricSection(METRIC_CONFIG.throughput);
                }

                if (metricMap['lead_time']) {
                    showMetric(metricMap['lead_time']);
                    displayed = true;
                } else {
                    resetMetricSection(METRIC_CONFIG.lead_time);
                }

                if (displayed) {
                    $('#trend-analysis-results').removeClass('d-none');
                } else {
                    $('#trend-analysis-results').addClass('d-none');
                    showFeedback('Não foi possível calcular tendências com os dados fornecidos.');
                }

                if (Array.isArray(result.warnings) && result.warnings.length) {
                    showFeedback(result.warnings.join(' '), 'warning');
                }
            })
            .catch((error) => {
                toggleLoading(false);
                $('#trend-analysis-results').addClass('d-none');
                showFeedback(error.message || 'Erro inesperado ao calcular análise de tendências.');
            });
    }

    $(document).on('click', '#runTrendAnalysisBtn', runTrendAnalysis);
})(jQuery);
