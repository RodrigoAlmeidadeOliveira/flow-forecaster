(function (global) {
    if (typeof global === 'undefined' || global === null) {
        if (typeof window === 'undefined') {
            console.error('[Flow Forecaster] Global context unavailable for UI initialization.');
            return;
        }
        global = window;
    }

    const maybeJQuery = global.jQuery || global.$;
    if (!maybeJQuery || !maybeJQuery.fn || typeof maybeJQuery.fn.on !== 'function') {
        console.error('[Flow Forecaster] jQuery not detected. UI logic disabled.');
        return;
    }
    const $ = maybeJQuery;
    if (typeof $ !== 'function') {
        console.error('[Flow Forecaster] jQuery not detected. UI logic disabled.');
        return;
    }
    function isFiniteNumber(value) {
        return typeof value === 'number' && isFinite(value);
    }

    function formatNumber(value, decimals = 2) {
        if (value === null || value === undefined) return '—';
        const num = Number(value);
        if (!isFinite(num)) return '—';
        return num.toFixed(decimals);
    }

    function formatInteger(value) {
        if (value === null || value === undefined) return '—';
        const num = Number(value);
        if (!isFinite(num)) return '—';
        return Math.round(num).toString();
    }

    function formatPercent(value, decimals = 1) {
        if (value === null || value === undefined) return '—';
        const num = Number(value);
        if (!isFinite(num)) return '—';
        return `${num.toFixed(decimals)}%`;
    }

    window.__PF_isFiniteNumber = isFiniteNumber;
    window.__PF_formatNumber = formatNumber;
    window.__PF_formatInteger = formatInteger;
    window.__PF_formatPercent = formatPercent;

    function translate(key, fallback, params) {
        if (typeof window.i18n === 'function') {
            try {
                return window.i18n(key, params);
            } catch (error) {
                console.warn('[i18n] Failed to translate key:', key, error);
            }
        }
        let text = fallback != null ? fallback : key;
        if (params) {
            Object.keys(params).forEach(param => {
                const value = params[param];
                text = text.replace(new RegExp(`{{${param}}}`, 'g'), value);
            });
        }
        return text;
    }

    function parseIntegerValue(value) {
        if (value === null || value === undefined) return null;
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function computeBacklogState() {
        const $minInput = $('#backlogMin');
        const $maxInput = $('#backlogMax');
        const $complexity = $('#backlogComplexity');
        const $hiddenBacklog = $('#numberOfTasks');

        if ($minInput.length === 0 || $maxInput.length === 0 || $complexity.length === 0) {
            const fallback = parseIntegerValue($hiddenBacklog.val());
            return {
                rawMin: null,
                rawMax: null,
                normalizedMin: null,
                normalizedMax: null,
                adjustedMin: fallback,
                adjustedMax: fallback,
                average: fallback,
                swapped: false,
                lowMultiplier: 1,
                highMultiplier: 1,
                complexityKey: null,
                complexityLabel: '',
                elementsPresent: false
            };
        }

        const rawMin = parseIntegerValue($minInput.val());
        const rawMax = parseIntegerValue($maxInput.val());
        const option = $complexity.find('option:selected');

        const lowMultiplier = parseFloat(option.data('lowMultiplier')) || 1;
        const highMultiplier = parseFloat(option.data('highMultiplier')) || 1;
        const complexityKey = option.val() || null;
        const complexityLabel = option.text().trim();

        let normalizedMin = rawMin;
        let normalizedMax = rawMax;
        let swapped = false;

        if (normalizedMin !== null && normalizedMax !== null) {
            if (normalizedMin > normalizedMax) {
                swapped = true;
                const tmp = normalizedMin;
                normalizedMin = normalizedMax;
                normalizedMax = tmp;
            }
        }

        if (normalizedMin !== null) {
            normalizedMin = Math.max(0, normalizedMin);
        }
        if (normalizedMax !== null) {
            normalizedMax = Math.max(0, normalizedMax);
        }

        const adjustedMin = normalizedMin !== null ? Math.round(normalizedMin * lowMultiplier) : null;
        const adjustedMax = normalizedMax !== null ? Math.round(normalizedMax * highMultiplier) : null;

        let average = null;
        if (adjustedMin !== null && adjustedMax !== null) {
            average = Math.round((adjustedMin + adjustedMax) / 2);
        } else if (adjustedMin !== null) {
            average = adjustedMin;
        } else if (adjustedMax !== null) {
            average = adjustedMax;
        }

        return {
            rawMin,
            rawMax,
            normalizedMin,
            normalizedMax,
            adjustedMin,
            adjustedMax,
            average,
            swapped,
            lowMultiplier,
            highMultiplier,
            complexityKey,
            complexityLabel,
            elementsPresent: true
        };
    }

    function updateBacklogSummary(state) {
        if (!state.elementsPresent) {
            return;
        }

        const $minInput = $('#backlogMin');
        const $maxInput = $('#backlogMax');
        const $hiddenBacklog = $('#numberOfTasks');
        const $warning = $('#backlogRangeWarning');
        const $summary = $('#backlogAdjustedSummary');

        if (state.swapped) {
            $warning.text(translate(
                'backlog_range_swapped_warning',
                'O valor mínimo era maior que o máximo e foi invertido automaticamente.'
            ));
            if (state.normalizedMin !== null) {
                $minInput.val(state.normalizedMin);
            }
            if (state.normalizedMax !== null) {
                $maxInput.val(state.normalizedMax);
            }
        } else {
            $warning.text('');
        }

        if (state.average !== null && state.average > 0) {
            $hiddenBacklog.val(state.average);
        } else {
            $hiddenBacklog.val('');
        }

        if (state.adjustedMin !== null && state.adjustedMax !== null && state.adjustedMin >= 0 && state.adjustedMax >= 0) {
            $summary.text(translate(
                'backlog_adjusted_summary',
                'Backlog ajustado: {{adjustedMin}} – {{adjustedMax}} tarefas (média {{average}}) • Complexidade: {{label}}',
                {
                    adjustedMin: state.adjustedMin,
                    adjustedMax: state.adjustedMax,
                    average: state.average ?? '—',
                    label: state.complexityLabel || ''
                }
            ));
        } else {
            $summary.text(translate(
                'backlog_adjusted_summary_placeholder',
                'Backlog ajustado será exibido aqui.'
            ));
        }
    }

    function recalculateBacklog() {
        const state = computeBacklogState();
        updateBacklogSummary(state);
        return state;
    }
    window.recalculateBacklog = recalculateBacklog;

    function clampFocusPercent(value) {
        const num = parseFloat(value);
        if (!Number.isFinite(num)) return 100;
        return Math.min(100, Math.max(0, num));
    }

    function updateTeamFocusUI(percent) {
        const clamped = clampFocusPercent(percent);
        const focusFactor = Math.round((clamped / 100) * 1000) / 1000;
        $('#teamFocusPercent').val(clamped);
        $('#teamFocus').val(focusFactor);
        $('#teamFocusDisplay').text(`${Math.round(clamped)}%`);

        $('.team-focus-preset').each(function() {
            const preset = parseFloat($(this).data('focus'));
            if (Math.abs(preset - clamped) < 0.001) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    }

    function getTeamFocusPercent() {
        return clampFocusPercent($('#teamFocusPercent').val());
    }

    function buildThroughputStatsHtml(stats) {
        if (!stats) return '';
        const percentiles = stats.percentiles || {};
        let html = '<div class="card mb-3">';
        html += '<div class="card-header">Throughput</div>';
        html += '<div class="card-body">';
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-3"><tbody>';
        html += `<tr><th scope="row">Quantidade de Pontos</th><td>${formatInteger(stats.count)}</td></tr>`;
        html += `<tr><th scope="row">Média</th><td>${formatNumber(stats.mean)}</td></tr>`;
        html += `<tr><th scope="row">Mediana</th><td>${formatNumber(stats.median)}</td></tr>`;
        html += `<tr><th scope="row">Moda</th><td>${formatNumber(stats.mode)}</td></tr>`;
        html += `<tr><th scope="row">Desvio Padrão</th><td>${formatNumber(stats.std)}</td></tr>`;
        html += `<tr><th scope="row">Desvio Médio</th><td>${formatNumber(stats.mad)}</td></tr>`;
        html += `<tr><th scope="row">Coef. Var.</th><td>${formatPercent(stats.cv)}</td></tr>`;
        html += `<tr><th scope="row">Min</th><td>${formatNumber(stats.min)}</td></tr>`;
        html += `<tr><th scope="row">Máx</th><td>${formatNumber(stats.max)}</td></tr>`;
        html += `<tr><th scope="row">Amplitude</th><td>${formatNumber(stats.range)}</td></tr>`;
        html += '</tbody></table></div>';

        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-0"><thead><tr><th colspan="2">Percentis</th></tr></thead><tbody>';
        const percRows = [
            ['P25', percentiles.p25],
            ['P50', percentiles.p50],
            ['P75', percentiles.p75],
            ['P85', percentiles.p85],
            ['P90', percentiles.p90],
            ['P95', percentiles.p95]
        ];
        percRows.forEach(([label, value]) => {
            html += `<tr><th scope="row">${label}</th><td>${formatNumber(value)}</td></tr>`;
        });
        html += '</tbody></table></div>';
        html += '</div></div>';
        return html;
    }

    function buildLeadStatsHtml(stats) {
        if (!stats) return '';
        const percentiles = stats.percentiles || {};
        const risk = stats.risk_metrics || {};
        const weibull = stats.weibull_fit || {};

        let html = '<div class="card mb-3">';
        html += '<div class="card-header">Lead Time</div>';
        html += '<div class="card-body">';
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-3"><tbody>';
        html += `<tr><th scope="row">Quantidade de Pontos</th><td>${formatInteger(stats.count)}</td></tr>`;
        html += `<tr><th scope="row">Média</th><td>${formatNumber(stats.mean)}</td></tr>`;
        html += `<tr><th scope="row">Mediana</th><td>${formatNumber(stats.median)}</td></tr>`;
        html += `<tr><th scope="row">Moda</th><td>${formatNumber(stats.mode)}</td></tr>`;
        html += `<tr><th scope="row">Desvio Padrão</th><td>${formatNumber(stats.std)}</td></tr>`;
        html += `<tr><th scope="row">Desvio Médio</th><td>${formatNumber(stats.mad)}</td></tr>`;
        html += `<tr><th scope="row">Coef. Var.</th><td>${formatPercent(stats.cv)}</td></tr>`;
        html += `<tr><th scope="row">Min</th><td>${formatNumber(stats.min)}</td></tr>`;
        html += `<tr><th scope="row">Máx</th><td>${formatNumber(stats.max)}</td></tr>`;
        html += `<tr><th scope="row">Amplitude</th><td>${formatNumber(stats.range)}</td></tr>`;
        html += `<tr><th scope="row">P98 / P50</th><td>${formatNumber(stats.ratio_p98_p50)}</td></tr>`;
        html += `<tr><th scope="row">IIQ</th><td>${formatNumber(stats.iqr)}</td></tr>`;
        html += '</tbody></table></div>';

        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-3"><thead><tr><th colspan="2">Percentis</th></tr></thead><tbody>';
        const leadPercRows = [
            ['P100', percentiles.p100],
            ['P98', percentiles.p98],
            ['P95', percentiles.p95],
            ['P90', percentiles.p90],
            ['P85', percentiles.p85],
            ['P75', percentiles.p75],
            ['P50 (Median)', percentiles.p50],
            ['P25', percentiles.p25],
            ['P15', percentiles.p15]
        ];
        leadPercRows.forEach(([label, value]) => {
            html += `<tr><th scope="row">${label}</th><td>${formatNumber(value)}</td></tr>`;
        });
        html += '</tbody></table></div>';

        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-3"><thead><tr><th>Risco do Lead Time</th><th>Valor</th><th>Qt. acima valor</th></tr></thead><tbody>';
        html += `<tr><th scope="row">6× Média</th><td>${formatNumber(risk.six_mean_threshold)}</td><td>${formatInteger(risk.count_above_six_mean)}</td></tr>`;
        html += `<tr><th scope="row">10× Mediana</th><td>${formatNumber(risk.ten_median_threshold)}</td><td>${formatInteger(risk.count_above_ten_median)}</td></tr>`;
        html += `<tr><th scope="row">Outlier</th><td>${formatNumber(risk.outlier_threshold)}</td><td>${formatInteger(risk.count_above_outlier)}</td></tr>`;
        html += '</tbody></table></div>';

        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-bordered mb-0"><thead><tr><th colspan="2">Ajuste Weibull</th></tr></thead><tbody>';
        if (weibull && Object.keys(weibull).length) {
            html += `<tr><th scope="row">Shape (k)</th><td>${formatNumber(weibull.shape)}</td></tr>`;
            html += `<tr><th scope="row">Scale (λ)</th><td>${formatNumber(weibull.scale)}</td></tr>`;
            html += `<tr><th scope="row">Intercept</th><td>${formatNumber(weibull.intercept)}</td></tr>`;
            html += `<tr><th scope="row">R²</th><td>${formatNumber(weibull.r_squared, 3)}</td></tr>`;
            html += `<tr><th scope="row">Média prevista</th><td>${formatNumber(weibull.predicted_mean)}</td></tr>`;
            html += `<tr><th scope="row">P63 (Scale)</th><td>${formatNumber(weibull.p63)}</td></tr>`;
        } else {
            html += '<tr><td colspan="2">Insufficient data to fit Weibull distribution.</td></tr>';
        }
        html += '</tbody></table></div>';

        html += '</div></div>';
        return html;
    }

    window.renderInputStats = function(selector, stats, options) {
        const $container = $(selector);
        if (!$container.length) return;

        options = options || {};
        const $title = $container.find('.input-stats-title');
        if (options.title) {
            $title.text(options.title);
        }

        const $content = $container.find('.input-stats-content');

        if (!stats) {
            $content.empty();
            $container.hide();
            return;
        }

        let sections = '';
        const showThroughput = options.showThroughput !== false;
        const showLeadTime = options.showLeadTime !== false;

        if (showThroughput && stats.throughput) {
            sections += buildThroughputStatsHtml(stats.throughput);
        }

        if (showLeadTime && stats.lead_time) {
            sections += buildLeadStatsHtml(stats.lead_time);
        }

        if (sections) {
            $content.html(sections);
            $container.show();
        } else {
            $content.empty();
            $container.hide();
        }
    };

    $(window).on("load", function () {
    const TOOLTIP_DELAY = 500;
    const DOC_BASE_URL = "https://flow-forecaster.fly.dev/documentacao";

    function initDocumentationTooltips() {
        $('.doc-hint-icon').each(function () {
            const $icon = $(this);
            if (!$icon.attr('href')) {
                const anchor = $icon.data('docAnchor');
                const docUrl = anchor ? `${DOC_BASE_URL}#${anchor}` : DOC_BASE_URL;
                $icon.attr('href', docUrl);
            }
            if (!$icon.data('bs.tooltip')) {
                $icon.tooltip({ delay: TOOLTIP_DELAY });
            }
        });
    }

    window.initDocumentationTooltips = initDocumentationTooltips;

    $('[data-toggle="tooltip"]').tooltip({ delay: TOOLTIP_DELAY });
    initDocumentationTooltips();

    function parseSamples(selector) {
        let val = $(selector).val() || '';
        if (val.trim().length === 0) return [];
        return val.split(/[\s\n,]/)
            .map(s => s.trim().length > 0 ? Number(s.trim()) : NaN)
            .filter(n => !isNaN(n))
            .filter(n => n >= 0);
    }

    function parseActualRemainingSeries(raw) {
        const values = [];
        const labels = [];
        if (!raw) {
            return { values, labels };
        }

        raw.split(/\r?\n/).forEach(line => {
            if (!line) return;
            const trimmed = line.trim();
            if (!trimmed) return;

            let datePart = null;
            let valuePart = trimmed;

            const delimiterMatch = trimmed.match(/[;,\t]/);
            if (delimiterMatch) {
                const split = trimmed.split(delimiterMatch[0]);
                datePart = (split[0] || '').trim();
                valuePart = (split[1] || '').trim();
            } else if (trimmed.includes(' ')) {
                const lastSpace = trimmed.lastIndexOf(' ');
                const maybeValue = trimmed.slice(lastSpace + 1).trim();
                const maybeDate = trimmed.slice(0, lastSpace).trim();
                if (/^-?\d+(?:[\.,]\d+)?$/.test(maybeValue)) {
                    datePart = maybeDate;
                    valuePart = maybeValue;
                }
            }

            const numeric = parseFloat(valuePart.replace(',', '.'));
            if (!Number.isFinite(numeric)) return;

            labels.push(datePart || `Semana ${labels.length + 1}`);
            values.push(numeric);
        });

        return { values, labels };
    }

    function updateRiskSummaryUI(simulationData, result) {
        const riskRows = $('#risks').find('.risk-row').not('#risk-row-template');
        if (!riskRows.length) return;

        riskRows.each((_idx, row) => {
            const $row = $(row);
            $row.find("input[name='expectedImpact']").val('-');
            $row.find("input[name='impactRank']").val('-');
        });

        const risks = simulationData?.risks || [];
        if (!risks.length) return;

        const p85 = Number(result?.percentile_stats?.p85);
        const severityScale = Number.isFinite(p85) && p85 > 0 ? p85 : 1;
        const computed = [];

        riskRows.each((idx, row) => {
            const risk = risks[idx];
            if (!risk || !risk.likelihood) return;
            const probability = Number(risk.likelihood) / 100;
            const baseImpact = Number(risk.mediumImpact || ((risk.lowImpact + risk.highImpact) / 2)) || 0;
            const expected = probability * baseImpact;
            const severity = expected * severityScale;
            const $row = $(row);
            $row.find("input[name='expectedImpact']").val(expected > 0 ? expected.toFixed(2) : '0');
            computed.push({ index: idx, severity });
        });

        computed
            .filter(item => item.severity > 0)
            .sort((a, b) => b.severity - a.severity)
            .forEach((item, order) => {
                riskRows.eq(item.index).find("input[name='impactRank']").val(order + 1);
            });
    }

    const isFiniteNumberLocal = window.__PF_isFiniteNumber || function(value) {
        return typeof value === 'number' && isFinite(value);
    };

    const formatNumber = window.__PF_formatNumber || function(value, decimals = 2) {
        if (value === null || value === undefined) return '—';
        const num = Number(value);
        if (!isFiniteNumberLocal(num)) return '—';
        return num.toFixed(decimals);
    };

    const formatInteger = window.__PF_formatInteger || function(value) {
        if (value === null || value === undefined) return '—';
        const num = Number(value);
        if (!isFiniteNumberLocal(num)) return '—';
        return Math.round(num).toString();
    };

    const deadlineCharts = [];
    const historicalCharts = {
        throughputHistogram: null,
        throughputControl: null,
        leadHistogram: null,
        leadControl: null
    };
    let historicalChartsDirty = true;
    let historicalChartsUpdateTimer = null;

    const chartColors = {
        throughput: {
            barBg: 'rgba(46, 134, 171, 0.35)',
            barBorder: '#2E86AB',
            series: '#2E86AB',
            seriesFill: 'rgba(46, 134, 171, 0.10)'
        },
        leadTime: {
            barBg: 'rgba(106, 153, 78, 0.35)',
            barBorder: '#6A994E',
            series: '#6A994E',
            seriesFill: 'rgba(106, 153, 78, 0.10)'
        },
        percentiles: {
            p15: '#1D3557',
            p85: '#F18F01',
            p95: '#C73E1D'
        }
    };

    function destroyHistoricalChart(key) {
        if (historicalCharts[key]) {
            historicalCharts[key].destroy();
            historicalCharts[key] = null;
        }
    }

    function percentileValue(sorted, percentile) {
        if (!sorted.length) return null;
        if (percentile <= 0) return sorted[0];
        if (percentile >= 1) return sorted[sorted.length - 1];

        const index = (sorted.length - 1) * percentile;
        const lower = Math.floor(index);
        const upper = Math.ceil(index);
        const weight = index - lower;

        if (lower === upper) return sorted[lower];
        return sorted[lower] * (1 - weight) + sorted[upper] * weight;
    }

    function computePercentileStats(values) {
        if (!values || !values.length) return null;
        const sorted = values.slice().sort((a, b) => a - b);
        const sum = sorted.reduce((acc, val) => acc + val, 0);
        return {
            sorted,
            count: sorted.length,
            min: sorted[0],
            max: sorted[sorted.length - 1],
            mean: sum / sorted.length,
            p15: percentileValue(sorted, 0.15),
            p85: percentileValue(sorted, 0.85),
            p95: percentileValue(sorted, 0.95)
        };
    }

    function buildHistogramSeries(values) {
        const stats = computePercentileStats(values);
        if (!stats) return null;

        const { min, max, sorted } = stats;
        const count = sorted.length;

        if (count === 0) return null;

        if (max === min) {
            const rangePadding = Math.abs(max) * 0.1 || 1;
            const start = max - rangePadding;
            const end = max + rangePadding;
            return {
                stats,
                histogramData: [{
                    x: max,
                    y: count,
                    binStart: start,
                    binEnd: end
                }],
                lineMax: Math.max(1, count * 1.1)
            };
        }

        let binCount = Math.round(Math.sqrt(count));
        binCount = Math.max(5, Math.min(20, binCount));

        const range = max - min;
        const binSize = range / binCount;
        const bins = [];

        for (let i = 0; i < binCount; i++) {
            const start = min + (i * binSize);
            const end = (i === binCount - 1) ? max : start + binSize;
            bins.push({ start, end, count: 0 });
        }

        const lastIndex = binCount - 1;
        sorted.forEach((value) => {
            const relative = (value - min) / binSize;
            let index = Math.floor(relative);
            if (!isFinite(index) || index < 0) index = 0;
            if (index > lastIndex) index = lastIndex;
            bins[index].count += 1;
        });

        const histogramData = bins.map(({ start, end, count: binCountValue }) => ({
            x: (start + end) / 2,
            y: binCountValue,
            binStart: start,
            binEnd: end
        }));

        const maxCount = bins.reduce((maxValue, bin) => Math.max(maxValue, bin.count), 0);

        return {
            stats,
            histogramData,
            lineMax: Math.max(1, maxCount * 1.1)
        };
    }

    function toggleChartVisibility(hasData, emptySelector, containerSelector) {
        if (hasData) {
            $(emptySelector).hide();
            $(containerSelector).show();
        } else {
            $(emptySelector).show();
            $(containerSelector).hide();
        }
    }

    function createVerticalLineDataset(label, value, color, maxY, dashPattern) {
        if (!isFiniteNumberLocal(value)) return null;
        return {
            type: 'line',
            label,
            data: [
                { x: value, y: 0 },
                { x: value, y: maxY }
            ],
            borderColor: color,
            borderWidth: 2,
            borderDash: dashPattern || [],
            fill: false,
            pointRadius: 0,
            pointHitRadius: 0,
            pointHoverRadius: 0,
            tension: 0
        };
    }

    function createHorizontalLineDataset(label, value, color, length, dashPattern) {
        if (!isFiniteNumberLocal(value)) return null;
        return {
            label,
            data: new Array(length).fill(value),
            borderColor: color,
            borderWidth: 2,
            borderDash: dashPattern || [],
            fill: false,
            pointRadius: 0,
            pointHitRadius: 0,
            pointHoverRadius: 0,
            lineTension: 0,
            spanGaps: true
        };
    }

    function buildHistogramAnnotation(bins, percentileValue, label, color, dash = [6, 4]) {
        if (!isFiniteNumberLocal(percentileValue) || !bins.length) return null;

        let index = bins.findIndex(bin => percentileValue <= bin.binEnd + 1e-9);
        if (index === -1) index = bins.length - 1;

        const bin = bins[index];
        let relative = 0.5;
        if (isFiniteNumberLocal(bin.binEnd) && isFiniteNumberLocal(bin.binStart) && bin.binEnd !== bin.binStart) {
            relative = (percentileValue - bin.binStart) / (bin.binEnd - bin.binStart);
            relative = Math.min(1, Math.max(0, relative));
        }

        const value = index + relative;

        return {
            type: 'line',
            mode: 'vertical',
            scaleID: 'x-axis-0',
            value,
            borderColor: color,
            borderDash: dash,
            borderWidth: 2,
            label: {
                enabled: true,
                content: `${label}: ${formatNumber(percentileValue)}`,
                position: 'top',
                yAdjust: 12,
                backgroundColor: color,
                fontColor: '#fff',
                fontSize: 10,
                padding: 4
            }
        };
    }

    function buildHorizontalAnnotation(value, label, color, dash = [6, 4]) {
        if (!isFiniteNumberLocal(value)) return null;

        return {
            type: 'line',
            mode: 'horizontal',
            scaleID: 'y-axis-0',
            value,
            borderColor: color,
            borderDash: dash,
            borderWidth: 2,
            label: {
                enabled: true,
                content: `${label}: ${formatNumber(value)}`,
                position: 'right',
                xAdjust: -6,
                backgroundColor: color,
                fontColor: '#fff',
                fontSize: 10,
                padding: 4
            }
        };
    }

    function renderHistogramChart(config) {
        const values = Array.isArray(config.values) ? config.values : [];
        const hasData = values.length >= 3;

        toggleChartVisibility(hasData, config.emptySelector, config.containerSelector);
        destroyHistoricalChart(config.chartKey);

        if (!hasData || !config.allowRender) {
            return;
        }

        const histogram = buildHistogramSeries(values);
        if (!histogram) return;

        const ctxElement = document.getElementById(config.canvasId);
        if (!ctxElement) return;

        const labels = histogram.histogramData.map((bin) => {
            const start = formatNumber(bin.binStart);
            const end = formatNumber(bin.binEnd);
            return start === end ? `${start}` : `${start} – ${end}`;
        });
        const counts = histogram.histogramData.map(bin => bin.y);

        const annotations = [
            buildHistogramAnnotation(histogram.histogramData, histogram.stats.p15, 'P15', chartColors.percentiles.p15, [12, 6]),
            buildHistogramAnnotation(histogram.histogramData, histogram.stats.p85, 'P85', chartColors.percentiles.p85, [8, 6]),
            buildHistogramAnnotation(histogram.histogramData, histogram.stats.p95, 'P95', chartColors.percentiles.p95, [6, 4]),
            buildHistogramAnnotation(histogram.histogramData, histogram.stats.mean, 'Média', '#6c757d', [4, 2])
        ].filter(Boolean);

        historicalCharts[config.chartKey] = new Chart(ctxElement.getContext('2d'), {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Frequência',
                    data: counts,
                    backgroundColor: config.colors.barBg,
                    borderColor: config.colors.barBorder,
                    borderWidth: 1,
                    barPercentage: 0.95,
                    categoryPercentage: 0.95
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 12,
                        right: 12,
                        bottom: 12,
                        left: 12
                    }
                },
                legend: { display: false },
                tooltips: {
                    backgroundColor: 'rgba(0,0,0,0.75)',
                    titleFontSize: 13,
                    bodyFontSize: 12,
                    mode: 'nearest',
                    intersect: true,
                    callbacks: {
                        title: function(items) {
                            const item = items[0];
                            const bin = histogram.histogramData[item.index];
                            if (bin) {
                                const start = formatNumber(bin.binStart);
                                const end = formatNumber(bin.binEnd);
                                return start === end ? `${start}` : `${start} – ${end}`;
                            }
                            return labels[item.index] || '';
                        },
                        label: function(tooltipItem) {
                            return `Frequência: ${formatInteger(tooltipItem.yLabel)}`;
                        }
                    }
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: config.xLabel || 'Valor'
                        },
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            fontSize: 11
                        },
                        gridLines: {
                            drawOnChartArea: false
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            beginAtZero: true,
                            precision: 0,
                            fontSize: 11
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Frequência'
                        }
                    }]
                },
                annotation: {
                    drawTime: 'afterDatasetsDraw',
                    annotations
                }
            }
        });
    }

    function renderControlChart(config) {
        const values = Array.isArray(config.values) ? config.values : [];
        const hasData = values.length >= 1;

        toggleChartVisibility(hasData, config.emptySelector, config.containerSelector);
        destroyHistoricalChart(config.chartKey);

        if (!hasData || !config.allowRender) {
            return;
        }

        const stats = computePercentileStats(values);
        if (!stats) return;

        const ctxElement = document.getElementById(config.canvasId);
        if (!ctxElement) return;

        const labels = values.map((_value, index) => index + 1);
        const annotations = [
            buildHorizontalAnnotation(stats.p15, 'P15', chartColors.percentiles.p15, [12, 6]),
            buildHorizontalAnnotation(stats.p85, 'P85', chartColors.percentiles.p85, [8, 6]),
            buildHorizontalAnnotation(stats.p95, 'P95', chartColors.percentiles.p95, [6, 4]),
            buildHorizontalAnnotation(stats.mean, 'Média', '#6c757d', [4, 2])
        ].filter(Boolean);

        historicalCharts[config.chartKey] = new Chart(ctxElement.getContext('2d'), {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: config.seriesLabel,
                    data: values,
                    borderColor: config.colors.series,
                    backgroundColor: config.colors.seriesFill,
                    fill: false,
                    lineTension: 0.2,
                    pointRadius: 4,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: config.colors.series,
                    pointHoverRadius: 6,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 12,
                        right: 12,
                        bottom: 12,
                        left: 12
                    }
                },
                tooltips: {
                    backgroundColor: 'rgba(0,0,0,0.75)',
                    titleFontSize: 13,
                    bodyFontSize: 12,
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const datasetLabel = data.datasets[tooltipItem.datasetIndex].label || '';
                            return `${datasetLabel}: ${formatNumber(tooltipItem.yLabel)}`;
                        }
                    }
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                legend: { display: false },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: config.xLabel || 'Observação'
                        },
                        ticks: {
                            beginAtZero: true,
                            precision: 0,
                            fontSize: 11
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: config.yLabel || 'Valor'
                        },
                        ticks: {
                            beginAtZero: true,
                            fontSize: 11
                        }
                    }]
                },
                annotation: {
                    drawTime: 'afterDatasetsDraw',
                    annotations
                }
            }
        });
    }

    function updateHistoricalCharts(forceRender) {
        const allowRender = $('#historical-charts').hasClass('active show');
        if (!forceRender && !historicalChartsDirty && allowRender) {
            return;
        }

        const throughputSamples = parseSamples('#tpSamples');
        const leadTimeSamples = parseSamples('#ltSamples');

        renderHistogramChart({
            values: throughputSamples,
            canvasId: 'tp-histogram-chart',
            chartKey: 'throughputHistogram',
            emptySelector: '#tp-histogram-empty',
            containerSelector: '#tp-histogram-container',
            colors: chartColors.throughput,
            xLabel: 'Throughput semanal',
            allowRender
        });

        renderControlChart({
            values: throughputSamples,
            canvasId: 'tp-control-chart',
            chartKey: 'throughputControl',
            emptySelector: '#tp-control-empty',
            containerSelector: '#tp-control-container',
            colors: chartColors.throughput,
            seriesLabel: 'Throughput histórico',
            xLabel: 'Semana',
            yLabel: 'Itens por semana',
            allowRender
        });

        renderHistogramChart({
            values: leadTimeSamples,
            canvasId: 'lt-histogram-chart',
            chartKey: 'leadHistogram',
            emptySelector: '#lt-histogram-empty',
            containerSelector: '#lt-histogram-container',
            colors: chartColors.leadTime,
            xLabel: 'Lead time (dias)',
            allowRender
        });

        renderControlChart({
            values: leadTimeSamples,
            canvasId: 'lt-control-chart',
            chartKey: 'leadControl',
            emptySelector: '#lt-control-empty',
            containerSelector: '#lt-control-container',
            colors: chartColors.leadTime,
            seriesLabel: 'Lead time histórico',
            xLabel: 'Ordem de ocorrência',
            yLabel: 'Dias',
            allowRender
        });

        historicalChartsDirty = !allowRender;
    }

    function scheduleHistoricalUpdate() {
        if (historicalChartsUpdateTimer) {
            clearTimeout(historicalChartsUpdateTimer);
        }
        historicalChartsUpdateTimer = setTimeout(() => {
            updateHistoricalCharts(true);
            historicalChartsUpdateTimer = null;
        }, 250);
    }

    function markHistoricalChartsDirty() {
        historicalChartsDirty = true;
        updateHistoricalCharts(false);
        if ($('#historical-charts').hasClass('active show')) {
            scheduleHistoricalUpdate();
        }
    }

    function parseRisks(selector) {
        const risks = [];
        $(selector).find('tbody').find('.risk-row').each((_index, el) => {
            const $el = $(el);
            const risk = {
                likelihood: $el.find("input[name='likelihood']").val(),
                lowImpact: $el.find("input[name='lowImpact']").val(),
                mediumImpact: $el.find("input[name='mediumImpact']").val(),
                highImpact: $el.find("input[name='highImpact']").val(),
                description: $el.find("input[name='description']").val(),
            };
            if (risk.likelihood && (risk.lowImpact || risk.mediumImpact || risk.highImpact)) {
                if (!risk.lowImpact) risk.lowImpact = '0';
                if (!risk.mediumImpact) risk.mediumImpact = risk.lowImpact || '0';
                if (!risk.highImpact) risk.highImpact = risk.mediumImpact || risk.lowImpact || '0';
                risk.likelihood = parseInt(risk.likelihood) || 0;
                risk.lowImpact = parseInt(risk.lowImpact) || 0;
                risk.mediumImpact = parseInt(risk.mediumImpact) || 0;
                risk.highImpact = parseInt(risk.highImpact) || 0;
                risks.push(risk);
            }
        });
        return risks;
    }

    const $riskRowTemplate = $('#risk-row-template').clone();
    function addRisk() {
        const $row = $riskRowTemplate.clone();
        $row.insertBefore($('#add-risk-row'));
        $row.find("input[name='expectedImpact']").val('-');
        $row.find("input[name='impactRank']").val('-');
        return $row;
    }
    window.addRisk = addRisk;

    function fillRisk(risk, $row) {
        $row.find("input[name='likelihood']").val(risk.likelihood);
        $row.find("input[name='lowImpact']").val(risk.lowImpact);
        $row.find("input[name='mediumImpact']").val(risk.mediumImpact);
        $row.find("input[name='highImpact']").val(risk.highImpact);
        $row.find("input[name='description']").val(risk.description);
    }

    // Risk summary calculation and display
    async function updateRiskSummary() {
        const risks = parseRisks('#risks');

        if (risks.length === 0) {
            $('#risk-summary-container').hide();
            return;
        }

        const tpSamples = parseDataSeries($('#tp').val());

        try {
            const response = await fetch('/api/risk-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    risks: risks,
                    tpSamples: tpSamples
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            displayRiskSummary(result);
        } catch (error) {
            console.error('Error calculating risk summary:', error);
        }
    }

    function displayRiskSummary(result) {
        const $container = $('#risk-summary-container');
        const $content = $('#risk-summary-content');

        if (!result || !result.risk_summaries || result.risk_summaries.length === 0) {
            $container.hide();
            return;
        }

        let html = '';

        // Summary metrics
        html += '<div class="row mb-3">';
        html += '<div class="col-md-4">';
        html += '<div class="card border-warning">';
        html += '<div class="card-body text-center">';
        html += '<h6 class="text-muted">Impacto Total Esperado</h6>';
        html += `<h3 class="text-warning">${result.total_expected_impact}</h3>`;
        html += '<p class="mb-0 small">histórias adicionais</p>';
        html += '</div></div></div>';

        html += '<div class="col-md-4">';
        html += '<div class="card border-danger">';
        html += '<div class="card-body text-center">';
        html += '<h6 class="text-muted">Riscos de Alta Prioridade</h6>';
        html += `<h3 class="text-danger">${result.high_priority_count}</h3>`;
        html += `<p class="mb-0 small">de ${result.risk_count} riscos</p>`;
        html += '</div></div></div>';

        html += '<div class="col-md-4">';
        html += '<div class="card border-info">';
        html += '<div class="card-body text-center">';
        html += '<h6 class="text-muted">Impacto P85</h6>';
        html += `<h3 class="text-info">${result.total_p85_impact}</h3>`;
        html += '<p class="mb-0 small">histórias (conservador)</p>';
        html += '</div></div></div>';
        html += '</div>';

        // Recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            html += '<div class="alert alert-info" role="alert">';
            html += '<h6><i class="fas fa-lightbulb"></i> Recomendações</h6>';
            html += '<ul class="mb-0">';
            result.recommendations.forEach(rec => {
                const iconClass = rec.priority === 'HIGH' ? 'exclamation-triangle' : 'info-circle';
                html += `<li><i class="fas fa-${iconClass}"></i> ${rec.message}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }

        // Risks table
        html += '<h6 class="mt-3">Ranking de Riscos por Impacto Esperado</h6>';
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-hover">';
        html += '<thead class="thead-light">';
        html += '<tr>';
        html += '<th>Rank</th>';
        html += '<th>Descrição</th>';
        html += '<th>Prob.</th>';
        html += '<th>Impacto Esperado</th>';
        html += '<th>P85 Impacto</th>';
        html += '<th>Severidade</th>';
        html += '</tr>';
        html += '</thead>';
        html += '<tbody>';

        result.risk_summaries.forEach(risk => {
            let severityClass = 'secondary';
            let severityIcon = 'info-circle';
            if (risk.severity === 'HIGH') {
                severityClass = 'danger';
                severityIcon = 'exclamation-triangle';
            } else if (risk.severity === 'MEDIUM') {
                severityClass = 'warning';
                severityIcon = 'exclamation-circle';
            }

            html += '<tr>';
            html += `<td><span class="badge badge-${severityClass}">${risk.rank}</span></td>`;
            html += `<td>${risk.description || 'Sem descrição'}</td>`;
            html += `<td>${risk.likelihood_percent}%</td>`;
            html += `<td><strong>${risk.expected_impact}</strong> histórias</td>`;
            html += `<td>${risk.p85_impact} histórias</td>`;
            html += `<td><span class="badge badge-${severityClass}"><i class="fas fa-${severityIcon}"></i> ${risk.severity_label}</span></td>`;
            html += '</tr>';
        });

        html += '</tbody>';
        html += '</table>';
        html += '</div>';

        $content.html(html);
        $container.show();
    }

    // Dependencies handling functions
    function parseDependencies(selector) {
        const dependencies = [];
        $(selector).find('tbody').find('.dependency-row').each((_index, el) => {
            const $el = $(el);
            const dep = {
                id: `DEP-${_index + 1}`,
                name: $el.find("input[name='dependency_name']").val(),
                source_project: $el.find("input[name='dependency_source_project']").val(),
                target_project: $el.find("input[name='dependency_target_project']").val(),
                on_time_probability: parseFloat($el.find("input[name='dep_probability']").val()) / 100 || 0.5,
                delay_impact_days: parseFloat($el.find("input[name='dep_delay']").val()) || 0,
                criticality: $el.find("select[name='dependency_criticality']").val() || 'MEDIUM'
            };
            // Only add if name, source and target are filled
            if (dep.name && dep.source_project && dep.target_project) {
                dependencies.push(dep);
            }
        });
        return dependencies;
    }

    const $dependencyRowTemplate = $('#dependency-row-template').clone();
    function addDependency() {
        const $row = $dependencyRowTemplate.clone();
        $row.insertBefore($('#add-dependency-row'));
        return $row;
    }
    window.addDependency = addDependency;

    function fillDependency(dep, $row) {
        $row.find("input[name='dependency_name']").val(dep.name);
        $row.find("input[name='dependency_source_project']").val(dep.source_project);
        $row.find("input[name='dependency_target_project']").val(dep.target_project);
        $row.find("input[name='dep_probability']").val((dep.on_time_probability * 100) || 50);
        $row.find("input[name='dep_delay']").val(dep.delay_impact_days || 10);
        $row.find("select[name='dependency_criticality']").val(dep.criticality || 'MEDIUM');
    }

    const $probabilitiesRowTemplate = $('#probabilities').find('.probabilities-row').clone();
    function addProbabilityRow() {
        const $row = $probabilitiesRowTemplate.clone();
        $row.insertBefore('#show-more-row');
        return $row;
    }

    function clearProbabilities() {
        $('.probabilities-row').remove();
    }

    function share() {
        const simulationData = readSimulationData();
        if (simulationData) {
            // Encode data to base64
            $.ajax({
                url: '/api/encode',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(simulationData),
                success: function(response) {
                    const url = window.location.origin + window.location.pathname + '#' + response.encoded;
                    navigator.clipboard.writeText(url).then(() => {
                        alert('Link copied to clipboard!');
                    });
                },
                error: function() {
                    alert('Error encoding data for sharing');
                }
            });
        }
    }
    window.share = share;

    let currentlyLoadedHash = null;

    function readSimulationData(options = {}) {
        const { updateHash = true } = options;
        const backlogState = recalculateBacklog();

        if (backlogState.elementsPresent) {
            const hasMin = backlogState.normalizedMin !== null && backlogState.normalizedMin > 0;
            const hasMax = backlogState.normalizedMax !== null && backlogState.normalizedMax > 0;
            const invalidMessage = translate(
                'backlog_invalid_range',
                'Defina valores mínimos e máximos válidos e maiores que zero para o backlog.'
            );

            if (!hasMin && !hasMax) {
                alert(invalidMessage);
                return false;
            }

            if ((hasMin && (backlogState.adjustedMin === null || backlogState.adjustedMin <= 0)) ||
                (hasMax && (backlogState.adjustedMax === null || backlogState.adjustedMax <= 0))) {
                alert(invalidMessage);
                return false;
            }

            if (backlogState.average === null || backlogState.average <= 0) {
                alert(invalidMessage);
                return false;
            }
        }

        const teamFocusPercent = getTeamFocusPercent();
        const teamFocusFactor = Math.round((teamFocusPercent / 100) * 1000) / 1000;
        updateTeamFocusUI(teamFocusPercent);

        const rawThroughputSamples = parseSamples('#tpSamples');
        const throughputCadenceDays = parseInt($('#throughputCadence').val(), 10) || 7;
        const cadenceFactor = throughputCadenceDays > 0 ? throughputCadenceDays / 7 : 1;
        const normalizedThroughputSamples = rawThroughputSamples.map(value => cadenceFactor ? value / cadenceFactor : value);

        const horizonValueInput = parseInt($('#forecastHorizonValue').val(), 10);
        const forecastHorizonValue = Number.isFinite(horizonValueInput) && horizonValueInput > 0 ? horizonValueInput : 30;
        const forecastHorizonUnit = $('#forecastHorizonUnit').val() || 'days';

        const actualSeriesRaw = $('#actualRemainingSeries').val() || '';
        const actualSeriesParsed = parseActualRemainingSeries(actualSeriesRaw);

        const simulationData = {
            projectName: $('#projectName').val(),
            numberOfSimulations: parseInt($('#numberOfSimulations').val()),
            confidenceLevel: parseInt($('#confidenceLevel').val()) || 85,
            tpSamples: rawThroughputSamples,
            tpSamplesNormalized: normalizedThroughputSamples,
            ltSamples: parseSamples('#ltSamples'),
            splitRateSamples: parseSamples('#splitRateSamples'),
            risks: parseRisks('#risks'),
            dependencies: parseDependencies('#dependencies'),
            numberOfTasks: backlogState.average || parseInt($('#numberOfTasks').val()),
            totalContributors: parseInt($('#totalContributors').val()),
            minContributors: parseInt($('#minContributors').val()) || parseInt($('#totalContributors').val()),
            maxContributors: parseInt($('#maxContributors').val()) || parseInt($('#totalContributors').val()),
            sCurveSize: parseInt($('#sCurveSize').val()),
            historical_team_size: parseInt($('#historicalTeamSize').val()) || 1,
            startDate: $('#startDate').val() || undefined,
            deadlineDate: $('#deadlineDate').val() || undefined,
            teamFocus: teamFocusFactor,
            teamFocusPercent: teamFocusPercent,
            throughputCadenceDays,
            forecastHorizon: {
                value: forecastHorizonValue,
                unit: forecastHorizonUnit
            },
            actualRemainingRaw: actualSeriesRaw,
            actualRemainingValues: actualSeriesParsed.values,
            actualRemainingLabels: actualSeriesParsed.labels
        };

        if (backlogState.elementsPresent) {
            simulationData.backlogOriginalMin = backlogState.rawMin;
            simulationData.backlogOriginalMax = backlogState.rawMax;
            simulationData.backlogMin = backlogState.normalizedMin;
            simulationData.backlogMax = backlogState.normalizedMax;
            simulationData.backlogAdjustedMin = backlogState.adjustedMin;
            simulationData.backlogAdjustedMax = backlogState.adjustedMax;
            simulationData.backlogLowMultiplier = backlogState.lowMultiplier;
            simulationData.backlogHighMultiplier = backlogState.highMultiplier;
            simulationData.backlogComplexity = backlogState.complexityKey;
        }

        updateRiskSummaryUI(simulationData, null);

        if (!simulationData.tpSamples.some(n => n >= 1)) {
            alert("Must have at least one weekly throughput sample greater than zero");
            return false;
        }

        if (simulationData.splitRateSamples.length > 0 &&
            simulationData.splitRateSamples.some(n => n > 10 || n < 0.2)) {
            alert("Your split rates don't seem correct.\nFor a 10% split rate, put '1.1'");
            return false;
        }

        if (updateHash) {
            const hash = '#' + btoa(JSON.stringify(simulationData));
            currentlyLoadedHash = hash;
            location.hash = hash;
        }
        return simulationData;
    }

    function runSimulation() {
        const simulationData = readSimulationData();
        if (!simulationData) return;

        if (window.renderInputStats) {
            window.renderInputStats('#input-stats', null);
        }

        window.lastSimulationData = simulationData;

        $('#results-main').show();
        const $results = $('#results');
        $results.val('');
        $('#res-effort').val('Running...');

        const payload = JSON.parse(JSON.stringify(simulationData));
        if (Array.isArray(simulationData.tpSamplesNormalized) && simulationData.tpSamplesNormalized.length) {
            payload.tpSamples = simulationData.tpSamplesNormalized;
        }
        delete payload.tpSamplesNormalized;
        payload.actualRemaining = {
            values: simulationData.actualRemainingValues || [],
            labels: simulationData.actualRemainingLabels || []
        };
        delete payload.actualRemainingValues;
        delete payload.actualRemainingLabels;
        delete payload.actualRemainingRaw;

        // Call backend API
        $.ajax({
            url: '/api/simulate',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function(result) {
                displayResults(result, simulationData);
            },
            error: function(xhr) {
                alert('Error running simulation: ' + (xhr.responseJSON?.error || 'Unknown error'));
                $('#res-effort').val('Error');
            }
        });
    }

    function displayResults(result, simulationData) {
        const $results = $('#results');
        $results.val('');
        const write = str => $results.val($results.val() + str);

        const confidenceLevel = simulationData.confidenceLevel;
        const reportPercentile = confidenceLevel / 100;

        // Extract effort and duration at the confidence level
        const effortValues = result.simulations.map(s => s.effortWeeks).sort((a, b) => a - b);
        const durationValues = result.simulations.map(s => s.durationInCalendarWeeks).sort((a, b) => a - b);

        const effort = Math.round(percentile(effortValues, reportPercentile));
        const duration = Math.round(percentile(durationValues, reportPercentile));
        const backlogSummary = result.backlog_summary || {};

        console.log('Monte Carlo Simulation Results:', { effort, duration, effortValues, durationValues, confidenceLevel });

        const durationP50 = percentile(durationValues, 0.5);
        const durationP85 = percentile(durationValues, 0.85);
        const durationP95 = percentile(durationValues, 0.95);
        const effortP50 = percentile(effortValues, 0.5);
        const effortP85 = percentile(effortValues, 0.85);
        const effortP95 = percentile(effortValues, 0.95);

        let canMeetDeadline = null;
        if (simulationData.startDate && simulationData.deadlineDate) {
            const startMoment = moment(simulationData.startDate);
            const deadlineMoment = moment(simulationData.deadlineDate);
            if (startMoment.isValid() && deadlineMoment.isValid()) {
                const weeksAvailable = Math.max(0, deadlineMoment.diff(startMoment, 'weeks', true));
                canMeetDeadline = weeksAvailable >= durationP85;
            }
        }

        window.lastSimulationResults = {
            duration_p50: durationP50,
            duration_p85: durationP85,
            duration_p95: durationP95,
            effort_p50: effortP50,
            effort_p85: effortP85,
            effort_p95: effortP95,
            backlog: simulationData.numberOfTasks || null,
            confidence_level: confidenceLevel,
            timestamp: new Date().toISOString(),
            can_meet_deadline: canMeetDeadline,
            scope_completion_pct: result.scope_completion_pct || null
        };

        if (typeof window.updateCurrentKPIs === 'function') {
            window.updateCurrentKPIs();
        }
        if (typeof window.updateProjectHealth === 'function') {
            window.updateProjectHealth();
        }

        $('#res-summary-header').text(`Project forecast summary (with ${confidenceLevel}% of confidence):`);

        let endDate = '(No start date set)';
        if (simulationData.startDate) {
            endDate = moment(simulationData.startDate).add(duration, 'weeks').format('DD/MM/YYYY');
        } else if (simulationData.deadlineDate) {
            endDate = simulationData.deadlineDate;
        }

        console.log('Setting Monte Carlo Results:', {
            effort,
            duration,
            endDate,
            startDate: simulationData.startDate,
            deadlineDate: simulationData.deadlineDate
        });

        $('#res-effort').val(effort);
        $('#res-duration').val(duration);
        $('#res-endDate').val(endDate);

        // Probabilities
        clearProbabilities();
        $('#show-more-row').show();
        $('#show-more').show();

        const addProbability = (res) => {
            const comment = res.Likelihood > 80 ? 'Almost certain' :
                          res.Likelihood > 45 ? 'Somewhat certain' :
                          'Less than coin-toss odds';
            const style = res.Likelihood > 80 ? 'almost-certain' :
                         res.Likelihood > 45 ? 'somewhat-certain' :
                         'not-certain';
            const $row = addProbabilityRow();
            const $cells = $row.find('td');
            $cells.addClass(style);
            $cells.eq(0).text(res.Likelihood + '%');
            $cells.eq(1).text(res.Effort.toString());
            $cells.eq(2).text(res.Duration.toString());
            $cells.eq(3).text(res.TotalTasks.toString());
            if (simulationData.startDate) {
                $cells.eq(4).text(moment(simulationData.startDate).add(res.Duration, 'weeks').format("DD/MM/YYYY"));
            }
            $cells.eq(5).text(comment);
        };

        result.resultsTable.slice(0, 9).forEach(addProbability);
        $('#show-more').off('click').on('click', () => {
            result.resultsTable.slice(9).forEach(addProbability);
            $('#show-more').off('click').hide();
            $('#show-more-row').hide();
        });

        const probabilityReportContainer = $('#probability-report-30-days');
        probabilityReportContainer.empty();

        const itemsForecast30 = result.items_forecast_30_days;
        if (itemsForecast30 && Array.isArray(itemsForecast30.probability_table) && itemsForecast30.probability_table.length) {
            const probabilityRows = [...itemsForecast30.probability_table]
                .map(entry => ({
                    probability: Number(entry.probability),
                    items: entry.items != null ? entry.items : '—'
                }))
                .sort((a, b) => b.probability - a.probability);

            let highCount = 0;
            let mediumCount = 0;
            let lowCount = 0;

            const rowsHtml = probabilityRows.map(entry => {
                const probability = entry.probability;
                const items = entry.items;
                let rowClass;
                if (probability >= 80) {
                    rowClass = 'probability-row-high';
                    highCount += 1;
                } else if (probability >= 55) {
                    rowClass = 'probability-row-medium';
                    mediumCount += 1;
                } else {
                    rowClass = 'probability-row-low';
                    lowCount += 1;
                }
                return `<tr class="${rowClass}"><td>${probability}%</td><td>${items}</td></tr>`;
            }).join('');

            if (highCount === 0) highCount = 1;
            if (mediumCount === 0) mediumCount = 1;
            if (lowCount === 0) lowCount = 1;

            const periodStart = itemsForecast30.start_date || (simulationData.startDate || '—');
            const periodEnd = itemsForecast30.end_date || '—';
            const periodLabel = itemsForecast30.days ? `${itemsForecast30.days} dias` : '30 dias';

            probabilityReportContainer.html(`
                <div class="probability-report-wrapper mt-3">
                    <div class="probability-report-title">Itens estimados em 30 dias</div>
                    <div class="probability-report-content">
                        <div class="probability-table-wrapper">
                            <table class="table table-sm probability-table mb-0">
                                <thead>
                                    <tr>
                                        <th>Probabilidade</th>
                                        <th>Itens em 30 dias</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rowsHtml}
                                </tbody>
                            </table>
                            <div class="probability-report-meta small text-muted mt-2">
                                Horizonte: ${periodStart} → ${periodEnd} (${periodLabel})
                            </div>
                        </div>
                        <div class="probability-legend">
                            <div class="legend-item legend-high" style="flex:${highCount};">Quase certo</div>
                            <div class="legend-item legend-medium" style="flex:${mediumCount};">Algum grau de certeza</div>
                            <div class="legend-item legend-low" style="flex:${lowCount};">Chances baixas</div>
                        </div>
                    </div>
                </div>
            `);
        }

        // Draw charts
        drawHistogram('res-duration-histogram', durationValues, confidenceLevel);
        drawBurnDowns('res-burn-downs', result.burnDowns);
        drawScatterPlot('res-effort-scatter-plot', effortValues, confidenceLevel);

        // Write text report
        write(`Project forecast summary (with ${confidenceLevel}% of confidence):\n`);
        write(` - Up to ${effort} person-weeks of effort\n`);
        write(` - Can be delivered in up to ${duration} calendar weeks\n`);
        if (isFiniteNumber(backlogSummary.adjusted_min) && isFiniteNumber(backlogSummary.adjusted_max)) {
            write(` - Backlog sampled between ${backlogSummary.adjusted_min} and ${backlogSummary.adjusted_max} tasks\n`);
        } else if (simulationData.backlogAdjustedMin != null && simulationData.backlogAdjustedMax != null) {
            write(` - Backlog sampled between ${simulationData.backlogAdjustedMin} and ${simulationData.backlogAdjustedMax} tasks\n`);
        }
        if (simulationData.teamFocus != null) {
            const focusDisplay = Math.round(simulationData.teamFocus * 100);
            write(` - Team focus applied: ${focusDisplay}% of throughput\n`);
        }
        if (simulationData.startDate) {
            write(` - Can be delivered by ${endDate}\n`);
        }
        write(`\n\n`);
        write(`-----------------------------------------------------\n`);
        write(`                       DETAILS\n`);
        write(`-----------------------------------------------------\n`);
        write(`Number of simulations: ${simulationData.numberOfSimulations}\n`);
        write('All probabilities:\n');
        write(`  Likelihood\tDuration\tTasks\tEffort          \tComment\n`);
        for (const res of result.resultsTable) {
            const comment = res.Likelihood > 80 ? 'Almost certain' :
                          res.Likelihood > 45 ? 'Somewhat certain' :
                          'Less than coin-toss odds';
            write(`  ${res.Likelihood}%      \t${res.Duration} weeks \t${res.TotalTasks}\t${res.Effort} person-weeks  \t(${comment})\n`);
        }
        write(`\n`);
        write(`Error rates:\n - Weekly throughput: ${result.tpErrorRate}%\n - Task lead-times: ${result.ltErrorRate}%\n`);
        write(`  (Aim to keep these below 25% by adding more sample data)\n`);

        if (window.renderInputStats) {
            window.renderInputStats('#input-stats', result.input_stats);
        }

        // Display dependency analysis if available
        console.log('[DEBUG] Checking for dependency_analysis in result:', result.dependency_analysis);
        console.log('[DEBUG] simulationData.dependencies:', simulationData.dependencies);
        console.log('[DEBUG] result keys:', Object.keys(result));

        if (result.dependency_analysis) {
            console.log('[DEBUG] dependency_analysis found, displaying results');
            displayDependencyResults(result.dependency_analysis);
            displayDependencyTab(result.dependency_analysis, simulationData);
        } else {
            console.log('[DEBUG] No dependency_analysis in result');
            // Show empty state in tab
            $('#dependencyTabResults').hide();
            $('#dependencyTabEmpty').show();
        }
    }
    window.runSimulation = runSimulation;

    function displayDependencyTab(depAnalysis, simulationData) {
        // Populate the dependency analysis tab
        const $tabResults = $('#dependencyTabResults');
        const $tabEmpty = $('#dependencyTabEmpty');

        if (!depAnalysis || depAnalysis.total_dependencies === 0) {
            $tabResults.hide();
            $tabEmpty.show();
            return;
        }

        $tabEmpty.hide();
        $tabResults.show();

        // Populate metrics (same as main results)
        const onTimeProb = (depAnalysis.on_time_probability * 100).toFixed(1);
        $('#dep-tab-on-time-prob').text(onTimeProb + '%');
        $('#dep-tab-odds-ratio').text(depAnalysis.odds_ratio || '');

        const expectedDelay = depAnalysis.expected_delay_days.toFixed(1);
        $('#dep-tab-expected-delay').text(expectedDelay + ' dias');

        // Set risk level color
        const riskLevel = depAnalysis.risk_level;
        const riskColors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        };
        const riskColor = riskColors[riskLevel] || '#6c757d';
        $('#dep-tab-risk-level').text(riskLevel).css('color', riskColor);
        $('#dep-tab-risk-score').text(`Score: ${depAnalysis.risk_score.toFixed(0)}/100`);

        $('#dep-tab-total').text(depAnalysis.total_dependencies);

        // Delay distribution table
        const $delayBody = $('#dep-tab-delay-body');
        $delayBody.empty();
        const delayPercentiles = depAnalysis.delay_percentiles || {};
        const entries = Object.entries(delayPercentiles).map(([key, value]) => {
            const numericPercentile = parseFloat(key.replace(/[^0-9.]/g, '')) || 0;
            const label = key.toUpperCase().startsWith('P') ? key.toUpperCase() : `P${numericPercentile}`;
            const delayValue = typeof value === 'number' ? value : parseFloat(value) || 0;
            return { order: numericPercentile, label, value: delayValue };
        }).sort((a, b) => a.order - b.order);

        if (entries.length) {
            entries.forEach(({ label, value }) => {
                const formattedValue = `${value.toFixed(1)} dias`;
                $delayBody.append(`
                    <tr>
                        <td class="font-weight-bold">${label}</td>
                        <td>${formattedValue}</td>
                    </tr>
                `);
            });
        } else {
            $delayBody.append(`
                <tr>
                    <td colspan="2" class="text-muted">Sem dados de atraso disponíveis</td>
                </tr>
            `);
        }

        // Critical path
        const $criticalPath = $('#dep-tab-critical-path');
        $criticalPath.empty();
        if (depAnalysis.critical_path && depAnalysis.critical_path.length > 0) {
            depAnalysis.critical_path.forEach(dep => {
                $criticalPath.append(`<li class="list-group-item">${dep}</li>`);
            });
        } else {
            $criticalPath.append('<li class="list-group-item text-muted">Nenhuma dependência crítica</li>');
        }

        // Recommendations
        const $recommendations = $('#dep-tab-recommendations');
        $recommendations.empty();
        if (depAnalysis.recommendations && depAnalysis.recommendations.length > 0) {
            depAnalysis.recommendations.slice(0, 5).forEach(rec => {
                $recommendations.append(`<li class="list-group-item">${rec}</li>`);
            });
        } else {
            $recommendations.append('<li class="list-group-item text-muted">Sem recomendações</li>');
        }

        // Request visualization from backend
        if (simulationData.dependencies && simulationData.dependencies.length > 0) {
            $.ajax({
                url: '/api/visualize-dependencies',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    dependency_analysis: depAnalysis,
                    dependencies: simulationData.dependencies
                }),
                success: function(response) {
                    if (response.image) {
                        $('#dep-tab-visualization-image').attr('src', 'data:image/png;base64,' + response.image);
                    }
                },
                error: function(xhr) {
                    console.error('Error generating visualization:', xhr);
                    $('#dep-tab-visualization-container').html(
                        '<div class="alert alert-warning">Não foi possível gerar a visualização</div>'
                    );
                }
            });
        }
    }

    function displayDependencyResults(depAnalysis) {
        const $container = $('#dependency-results');

        // Show container
        $container.show();

        // Populate metrics
        const onTimeProb = (depAnalysis.on_time_probability * 100).toFixed(1);
        $('#dep-on-time-prob').text(onTimeProb + '%');
        $('#dep-odds-ratio').text(depAnalysis.odds_ratio || '');

        const expectedDelay = depAnalysis.expected_delay_days.toFixed(1);
        $('#dep-expected-delay').text(expectedDelay + ' dias');

        // Set risk level color
        const riskLevel = depAnalysis.risk_level;
        const riskColors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        };
        const riskColor = riskColors[riskLevel] || '#6c757d';
        $('#dep-risk-level').text(riskLevel).css('color', riskColor);
        $('#dep-risk-score').text(`Score: ${depAnalysis.risk_score.toFixed(0)}/100`);

        $('#dep-total').text(depAnalysis.total_dependencies);

        // Critical path
        const $criticalPath = $('#dep-critical-path');
        $criticalPath.empty();
        if (depAnalysis.critical_path && depAnalysis.critical_path.length > 0) {
            depAnalysis.critical_path.forEach(dep => {
                $criticalPath.append(`<li class="list-group-item">${dep}</li>`);
            });
        } else {
            $criticalPath.append('<li class="list-group-item text-muted">Nenhuma dependência crítica</li>');
        }

        // Recommendations
        const $recommendations = $('#dep-recommendations');
        $recommendations.empty();
        if (depAnalysis.recommendations && depAnalysis.recommendations.length > 0) {
            depAnalysis.recommendations.slice(0, 5).forEach(rec => {
                $recommendations.append(`<li class="list-group-item">${rec}</li>`);
            });
        } else {
            $recommendations.append('<li class="list-group-item text-muted">Sem recomendações</li>');
        }
    }

    function formatWeeks(value) {
        if (value === undefined || value === null || isNaN(Number(value))) {
            return '—';
        }
        return Number(value).toFixed(1);
    }

    function verdictBadge(canMeet) {
        return canMeet
            ? '<span class="badge badge-success">✓ On Track</span>'
            : '<span class="badge badge-danger">✗ At Risk</span>';
    }

    function clearDeadlineCharts() {
        while (deadlineCharts.length) {
            const chart = deadlineCharts.pop();
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        }
    }

    function numericOrNull(value) {
        const num = Number(value);
        return Number.isFinite(num) ? num : null;
    }

    function renderDeadlineCharts(mcData, mlData) {
        clearDeadlineCharts();

        const comparisonCtx = document.getElementById('deadlineComparisonChart');
        if (comparisonCtx) {
            const datasets = [{
                label: 'Monte Carlo',
                data: [numericOrNull(mcData.weeks.p50), numericOrNull(mcData.weeks.p85), numericOrNull(mcData.weeks.p95)],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2
            }];

            if (mlData && !mlData.error) {
                datasets.push({
                    label: 'Machine Learning',
                    data: [numericOrNull(mlData.weeks.p50), numericOrNull(mlData.weeks.p85), numericOrNull(mlData.weeks.p95)],
                    backgroundColor: 'rgba(255, 159, 64, 0.6)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2
                });
            }

            deadlineCharts.push(new Chart(comparisonCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['P50 (median)', 'P85 (recommended)', 'P95 (conservative)'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Completion Weeks by Confidence Level'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    scales: {
                        yAxes: [{
                            ticks: { beginAtZero: true },
                            scaleLabel: {
                                display: true,
                                labelString: 'Weeks'
                            }
                        }],
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Confidence'
                            }
                        }]
                    }
                }
            }));
        }

        const confidenceCtx = document.getElementById('deadlineConfidenceChart');
        if (confidenceCtx) {
            const datasets = [{
                label: 'Monte Carlo',
                data: [numericOrNull(mcData.weeks.p50), numericOrNull(mcData.weeks.p85), numericOrNull(mcData.weeks.p95)],
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 3,
                fill: true,
                lineTension: 0.3,
                pointRadius: 4
            }];

            if (mlData && !mlData.error) {
                datasets.push({
                    label: 'Machine Learning',
                    data: [numericOrNull(mlData.weeks.p50), numericOrNull(mlData.weeks.p85), numericOrNull(mlData.weeks.p95)],
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderWidth: 3,
                    fill: true,
                    lineTension: 0.3,
                    pointRadius: 4
                });
            }

            deadlineCharts.push(new Chart(confidenceCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['P50', 'P85', 'P95'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Confidence Curve'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    scales: {
                        yAxes: [{
                            ticks: { beginAtZero: true },
                            scaleLabel: {
                                display: true,
                                labelString: 'Weeks'
                            }
                        }],
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Confidence'
                            }
                        }]
                    }
                }
            }));
        }

        const effortCtx = document.getElementById('deadlineEffortChart');
        if (effortCtx && mlData && !mlData.error && mlData.projected_effort_p85) {
            deadlineCharts.push(new Chart(effortCtx.getContext('2d'), {
                type: 'horizontalBar',
                data: {
                    labels: ['Projected effort (P85)'],
                    datasets: [{
                        label: 'Person-weeks',
                        data: [numericOrNull(mlData.projected_effort_p85)],
                        backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Estimated Effort (Machine Learning)'
                    },
                    legend: {
                        display: false
                    },
                    scales: {
                        xAxes: [{
                            ticks: { beginAtZero: true },
                            scaleLabel: {
                                display: true,
                                labelString: 'Person-weeks'
                            }
                        }],
                        yAxes: [{
                            barThickness: 30
                        }]
                    }
                }
            }));
        }
    }

    function renderDeadlineSchedule(options) {
        const $navItem = $('#deadline-start-tab-item');
        const $tab = $('#deadline-start-window');
        if (!$navItem.length || !$tab.length) return;

        // Verificar se há deadline date
        if (!options.deadlineDate) {
            $navItem.hide();
            $tab.removeClass('show active');
            $('#deadlineResultsTabs a[href=\"#deadline-results-summary\"]').tab('show');
            return;
        }

        // Tentar obter percentis de lead time stats, ou usar valores padrão baseados em weeks
        const leadStats = options.leadStats || null;
        let p50, p85, p100;

        if (leadStats && leadStats.percentiles) {
            const percentiles = leadStats.percentiles;
            p50 = percentiles.p50;
            p85 = percentiles.p85;
            p100 = percentiles.p100;
        } else if (options.mcWeeks) {
            // Usar dados de weeks do Monte Carlo como fallback
            // Converter weeks para days (weeks * 7)
            p50 = (options.mcWeeks.p50 || 0) * 7;
            p85 = (options.mcWeeks.p85 || 0) * 7;
            p100 = (options.mcWeeks.p95 || options.mcWeeks.p85 || 0) * 7; // Usar p95 ou p85 como aproximação de p100
        }

        if (!p50 || !p85 || !p100) {
            $navItem.hide();
            $tab.removeClass('show active');
            $('#deadlineResultsTabs a[href=\"#deadline-results-summary\"]').tab('show');
            return;
        }

        const deadline = moment(options.deadlineDate, ['YYYY-MM-DD', 'DD/MM/YYYY', moment.ISO_8601], true);
        if (!deadline.isValid()) {
            $navItem.hide();
            $tab.removeClass('show active');
            return;
        }

        const today = moment(options.today, ['YYYY-MM-DD', moment.ISO_8601], true);
        const startDate = options.startDate ? moment(options.startDate, ['YYYY-MM-DD', 'DD/MM/YYYY', moment.ISO_8601], true) : null;

        // Display current date
        if (today && today.isValid()) {
            $('#current-date-display').text(today.format('DD/MM/YYYY'));
        }

        const tooEarly = deadline.clone().subtract(p100 * 2, 'days');
        const earlyStart = deadline.clone().subtract(p100 * 2, 'days');
        const earlyEnd = deadline.clone().subtract(p100, 'days');
        const justStart = deadline.clone().subtract(p100, 'days');
        const justEnd = deadline.clone().subtract(p85, 'days');
        const lateStart = deadline.clone().subtract(p85, 'days');
        const lateEnd = deadline.clone().subtract(p50, 'days');
        const umr = deadline.clone().subtract(p50, 'days');

        $('#window-too-early').text(tooEarly.format('DD/MM/YYYY'));
        $('#window-early-start').text(earlyStart.format('DD/MM/YYYY'));
        $('#window-early-end').text(earlyEnd.format('DD/MM/YYYY'));
        $('#window-just-start').text(justStart.format('DD/MM/YYYY'));
        $('#window-just-end').text(justEnd.format('DD/MM/YYYY'));
        $('#window-late-start').text(lateStart.format('DD/MM/YYYY'));
        $('#window-late-end').text(lateEnd.format('DD/MM/YYYY'));
        $('#window-umr').text(umr.format('DD/MM/YYYY'));

        // Calculate status based on TODAY (not start date) and place badge in correct row
        let statusElementId = '';
        let statusText = '';
        let statusClass = '';
        if (today && today.isValid()) {
            if (today.isBefore(earlyStart)) {
                statusElementId = '#window-too-early-status';
                statusText = 'Muito cedo';
                statusClass = 'badge-warning';
            } else if (today.isBetween(earlyStart, justStart, undefined, '[)')) {
                statusElementId = '#window-early-status';
                statusText = 'Cedo';
                statusClass = 'badge-warning';
            } else if (today.isBetween(justStart, lateStart, undefined, '[)')) {
                statusElementId = '#window-just-status';
                statusText = 'OK';
                statusClass = 'badge-success';
            } else if (today.isBetween(lateStart, umr, undefined, '[)')) {
                statusElementId = '#window-late-status';
                statusText = 'Tarde';
                statusClass = 'badge-warning';
            } else if (today.isSameOrAfter(umr)) {
                statusElementId = '#window-too-late-status';
                statusText = 'Atrasado';
                statusClass = 'badge-danger';
            }
        }

        // Clear all status cells
        $('#window-too-early-status, #window-early-status, #window-just-status, #window-late-status, #window-umr-status, #window-too-late-status').empty();

        // Place the status badge in the correct row
        if (statusElementId) {
            $(statusElementId).html(`<span class="badge ${statusClass}">${statusText}</span>`);
        }

        $('#window-too-late').text(umr.clone().add(1, 'days').format('DD/MM/YYYY'));

        $navItem.show();
    }

    function displayDeadlineAnalysis(response) {
        $('#deadline-analysis-loading').hide();

        if (!response) {
            alert('Error: empty deadline analysis response');
            return;
        }

        if (response.error) {
            alert('Error running deadline analysis: ' + response.error);
            return;
        }

        const mc = response.monte_carlo;
        if (!mc) {
            alert('Deadline analysis did not return Monte Carlo results.');
            return;
        }

        const ml = response.machine_learning;
        const consensus = response.consensus;

        const mcStats = mc.percentile_stats || {};
        const mcWeeks = {
            p50: mc.projected_weeks_p50 != null ? mc.projected_weeks_p50 : mcStats.p50,
            p85: mc.projected_weeks_p85 != null ? mc.projected_weeks_p85 : mcStats.p85,
            p95: mc.projected_weeks_p95 != null ? mc.projected_weeks_p95 : mcStats.p95
        };

        const mlStats = ml && !ml.error ? (ml.percentile_stats || {}) : {};
        const mlWeeks = {
            p50: ml && ml.projected_weeks_p50 != null ? ml.projected_weeks_p50 : mlStats.p50,
            p85: ml && ml.projected_weeks_p85 != null ? ml.projected_weeks_p85 : mlStats.p85,
            p95: ml && ml.projected_weeks_p95 != null ? ml.projected_weeks_p95 : mlStats.p95
        };

        // Machine Learning comparison (se disponível)
        let mlComparisonHtml = '';
        if (ml && !ml.error) {
            const mlDependencyHtml = ml.dependency_impact_days > 0
                ? `<p class="mb-1 text-muted small"><em>Includes dependency impact: +${ml.dependency_impact_days} days</em></p>`
                : '';

            mlComparisonHtml = `
                <div class="col-lg-12 mt-3">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">Comparação Machine Learning vs Monte Carlo</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Monte Carlo</h6>
                                    <p class="mb-1"><strong>P85 completion:</strong> ${formatWeeks(mcWeeks.p85)} weeks</p>
                                    <p class="mb-1"><strong>P50 completion:</strong> ${formatWeeks(mcWeeks.p50)} weeks</p>
                                    <p class="mb-1"><strong>Projected work (P85):</strong> ${mc.projected_work_p85 ?? '—'} tasks</p>
                                    <p class="mb-1"><strong>Projected effort (P85):</strong> ${mc.projected_effort_p85 ?? '—'} person-weeks</p>
                                    <div class="mt-2">${verdictBadge(mc.can_meet_deadline)}</div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Machine Learning</h6>
                                    <p class="mb-1"><strong>P85 completion:</strong> ${formatWeeks(mlWeeks.p85)} weeks</p>
                                    <p class="mb-1"><strong>P50 completion:</strong> ${formatWeeks(mlWeeks.p50)} weeks</p>
                                    <p class="mb-1"><strong>Projected work (P85):</strong> ${ml.projected_work_p85 ?? '—'} tasks</p>
                                    <p class="mb-1"><strong>Projected effort (P85):</strong> ${ml.projected_effort_p85 ?? '—'} person-weeks</p>
                                    ${mlDependencyHtml}
                                    <div class="mt-2">${verdictBadge(ml.can_meet_deadline)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
        }

        let consensusHtml = '';
        if (consensus) {
            const alertClass = consensus.both_agree ? 'alert-success' : 'alert-warning';
            const icon = consensus.both_agree ? '✅' : '⚠️';
            const percentageDiff = consensus.percentage_difference != null ? ` (${consensus.percentage_difference}%)` : '';

            consensusHtml = `
                <div class="col-lg-12 mt-3">
                    <div class="alert ${alertClass} mb-0 text-left" role="alert">
                        <h5 class="alert-heading">${icon} Consenso dos Métodos</h5>
                        <p class="mb-1"><strong>Ambos os métodos concordam:</strong> ${consensus.both_agree ? 'Sim' : 'Não'}</p>
                        <p class="mb-1"><strong>Diferença entre projeções P85:</strong> ${formatWeeks(consensus.difference_weeks)} semanas${percentageDiff}</p>
                        ${consensus.mc_more_conservative != null ? `<p class="mb-1"><strong>Método mais conservador:</strong> ${consensus.mc_more_conservative ? 'Monte Carlo' : 'Machine Learning'}</p>` : ''}
                        <p class="mb-${consensus.explanation ? '2' : '0'}"><strong>Recomendação:</strong> ${consensus.recommendation}</p>
                        ${consensus.explanation ? `<div class="small bg-light p-2 rounded">${consensus.explanation}</div>` : ''}
                    </div>
                </div>`;
        }

        const chartsHtml = `
            <div class="mt-4">
                <h5 class="text-left mb-3">Visualization</h5>
                <div class="row">
                    <div class="col-lg-6">
                        <div class="chart-container">
                            <canvas id="deadlineComparisonChart"></canvas>
                        </div>
                    </div>
                    <div class="col-lg-6 mt-3 mt-lg-0">
                        <div class="chart-container">
                            <canvas id="deadlineConfidenceChart"></canvas>
                        </div>
                    </div>
                </div>
                ${ml && !ml.error && ml.projected_effort_p85 ? `
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="chart-container" style="height: 220px;">
                            <canvas id="deadlineEffortChart"></canvas>
                        </div>
                    </div>
                </div>` : ''}
            </div>`;

        // Calcular effort e delivery date
        const simulationData = window.lastSimulationData || {};
        const teamSize = simulationData.totalContributors || mc.backlog || 1;
        const startDateMoment = mc.start_date_raw ? moment(mc.start_date_raw) : null;
        const duration = Math.round(mcWeeks.p85);
        // Effort = duration (weeks) × team size (pessoas)
        const effort = Math.round(duration * teamSize);
        const deliveryDate = startDateMoment ? startDateMoment.clone().add(duration, 'weeks').format('DD/MM/YYYY') : '—';

        console.log('Deadline Analysis Summary:', { teamSize, duration, effort, deliveryDate, mcWeeks, simulationData });

        // "Quantos?" - Items that CAN be completed in the deadline period (capacity)
        const howManyP95 = mc.items_possible_p95 || '—';
        const howManyP85 = mc.items_possible_p85 || '—';
        const howManyP50 = mc.items_possible_p50 || '—';

        // "Quando?" - Dates when the BACKLOG will be completed
        const whenP95 = mc.completion_date_p95 || '—';
        const whenP85 = mc.completion_date_p85 || '—';
        const whenP50 = mc.completion_date_p50 || '—';

        // Scope that WILL be completed from the backlog by the deadline
        const scopeCompletedP95 = mc.projected_work_p95 || '—';
        const scopeCompletedP85 = mc.projected_work_p85 || '—';
        const scopeCompletedP50 = mc.projected_work_p50 || '—';

        const weeksToDeadline = mc.weeks_to_deadline != null ? mc.weeks_to_deadline.toFixed(1) : '—';
        const projectedWeeks = mcWeeks.p85 != null ? mcWeeks.p85.toFixed(1) : '—';
        const projectedWork = mc.projected_work_p85 || '—';
        const canMeetDeadline = mc.can_meet_deadline ? 'Sim' : 'Não';

        // Format scope completion with raw value if > 100%
        let scopeCompletion = mc.scope_completion_pct != null ? mc.scope_completion_pct + '%' : '—';

        // Format deadline completion with raw value and explanation if > 100%
        let deadlineCompletion = mc.deadline_completion_pct != null ? mc.deadline_completion_pct + '%' : '—';
        if (mc.deadline_completion_pct_raw != null && mc.deadline_completion_pct_raw > 100) {
            deadlineCompletion = `100% <small class="text-danger">(precisa ${mc.deadline_completion_pct_raw.toFixed(1)}% do prazo)</small>`;
        }

        const daysToDeadline = mc.weeks_to_deadline != null ? Math.round(mc.weeks_to_deadline * 7) : '—';
        const startDateFormatted = mc.start_date || '—';
        const deadlineDateFormatted = mc.deadline_date || '—';

        // Generate visual forecast summary
        function generateProgressBar(completed, total, label, percentage) {
            const filledBlocks = Math.round((completed / total) * 24);
            const emptyBlocks = 24 - filledBlocks;
            const filled = '█'.repeat(filledBlocks);
            const empty = '░'.repeat(emptyBlocks);
            return `${label}: ${filled}${empty} ${completed} itens (${percentage}%)`;
        }

        function generateConclusion(backlog, p85Value, canMeet) {
            const percentageP85 = Math.round((p85Value / backlog) * 100);

            if (canMeet) {
                return `✅ <strong>Conclusão:</strong> Com os dados atuais, você <strong>CONSEGUIRÁ</strong> completar os ${backlog} itens no prazo. A equipe tem capacidade para entregar o backlog completo com ${percentageP85}% de confiança.`;
            } else {
                let fractionText = '';
                if (percentageP85 >= 90) fractionText = 'praticamente todo o backlog';
                else if (percentageP85 >= 75) fractionText = 'aproximadamente 3/4 do backlog';
                else if (percentageP85 >= 66) fractionText = 'aproximadamente 2/3 do backlog';
                else if (percentageP85 >= 50) fractionText = 'aproximadamente metade do backlog';
                else if (percentageP85 >= 33) fractionText = 'aproximadamente 1/3 do backlog';
                else fractionText = 'menos de 1/3 do backlog';

                return `⚠️ <strong>Conclusão:</strong> Com os dados atuais, você <strong>NÃO conseguirá</strong> completar todos os ${backlog} itens no prazo. Prepare-se para entregar ${fractionText} (${percentageP85}%) com boa confiança (P85).`;
            }
        }

        const backlog = mc.backlog || 0;
        const p95Items = parseInt(scopeCompletedP95) || 0;
        const p85Items = parseInt(scopeCompletedP85) || 0;
        const p50Items = parseInt(scopeCompletedP50) || 0;

        const visualSummaryHtml = backlog > 0 ? `
            <div class="col-lg-12 mt-3">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <h5 class="mb-0">📊 Visualização Rápida</h5>
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; background-color: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto;">
${generateProgressBar(backlog, backlog, 'Backlog total    ', 100)}

${generateProgressBar(p95Items, backlog, 'P95 (conservador)', Math.round((p95Items/backlog)*100))}
${generateProgressBar(p85Items, backlog, 'P85 (recomendado)', Math.round((p85Items/backlog)*100))}
${generateProgressBar(p50Items, backlog, 'P50 (arriscado)  ', Math.round((p50Items/backlog)*100))}
</pre>
                        <div class="alert alert-${mc.can_meet_deadline ? 'success' : 'warning'} mb-0 mt-3">
                            ${generateConclusion(backlog, p85Items, mc.can_meet_deadline)}
                        </div>
                    </div>
                </div>
            </div>
        ` : '';

        const summaryHtml = `
            <div class="row">
                <div class="col-lg-6">
                    <div class="card mb-3">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">RESULTADOS DA SIMULAÇÃO</h5>
                        </div>
                        <div class="card-body">
                            <table class="table table-sm table-borderless mb-0">
                                <tbody>
                                    <tr>
                                        <th scope="row">DEAD LINE</th>
                                        <td class="text-right font-weight-bold">${deadlineDateFormatted}</td>
                                    </tr>
                                    <tr>
                                        <th scope="row">Semanas para Dead Line</th>
                                        <td class="text-right font-weight-bold">${weeksToDeadline}</td>
                                    </tr>
                                    <tr>
                                        <th scope="row">Semanas Projetadas (P85)</th>
                                        <td class="text-right font-weight-bold">${projectedWeeks}</td>
                                    </tr>
                                    <tr>
                                        <th scope="row">Trabalho a ser entregue (projetado) (P85)</th>
                                        <td class="text-right font-weight-bold">${projectedWork}</td>
                                    </tr>
                                    <tr class="border-top">
                                        <th scope="row">Tem chance de cumprir o Dead Line?</th>
                                        <td class="text-right">
                                            <span class="badge ${mc.can_meet_deadline ? 'badge-success' : 'badge-danger'} font-weight-bold">
                                                ${canMeetDeadline}
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <th scope="row">% que será cumprido do escopo</th>
                                        <td class="text-right font-weight-bold">${scopeCompletion}</td>
                                    </tr>
                                    <tr>
                                        <th scope="row">% do prazo que será cumprido</th>
                                        <td class="text-right font-weight-bold">${deadlineCompletion}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="col-lg-6">
                    <div class="card mb-3">
                        <div class="card-header bg-info text-white">
                            <h5 class="mb-0">RESPOSTAS BASEADAS NO THROUGHPUT</h5>
                        </div>
                        <div class="card-body">
                            <h6 class="font-weight-bold">Quantos?</h6>
                            <p class="small text-muted">Considerando que tenho um período de tempo, quantos itens de trabalho provavelmente serão concluídos neste período?</p>
                            <table class="table table-sm table-bordered mb-3">
                                <tbody>
                                    <tr><th scope="row">INÍCIO</th><td>${startDateFormatted}</td></tr>
                                    <tr><th scope="row">FIM</th><td>${deadlineDateFormatted}</td></tr>
                                    <tr><th scope="row">DIAS</th><td>${daysToDeadline}</td></tr>
                                    <tr class="table-secondary"><th scope="row" colspan="2">Capacidade (sem limite de backlog)</th></tr>
                                    <tr><th scope="row">95% DE CONFIANÇA</th><td class="font-weight-bold">${howManyP95}</td></tr>
                                    <tr><th scope="row">85% DE CONFIANÇA</th><td class="font-weight-bold">${howManyP85}</td></tr>
                                    <tr><th scope="row">50% DE CONFIANÇA</th><td class="font-weight-bold">${howManyP50}</td></tr>
                                    <tr class="table-warning"><th scope="row" colspan="2">Escopo que será entregue (do backlog de ${mc.backlog})</th></tr>
                                    <tr><th scope="row">95% DE CONFIANÇA</th><td class="font-weight-bold">${scopeCompletedP95}</td></tr>
                                    <tr><th scope="row">85% DE CONFIANÇA</th><td class="font-weight-bold">${scopeCompletedP85}</td></tr>
                                    <tr><th scope="row">50% DE CONFIANÇA</th><td class="font-weight-bold">${scopeCompletedP50}</td></tr>
                                </tbody>
                            </table>

                            <h6 class="font-weight-bold mt-4">Quando?</h6>
                            <p class="small text-muted">"Dado que tenho um lote de trabalho, quando é provável que seja feito?"</p>
                            <table class="table table-sm table-bordered mb-0">
                                <tbody>
                                    <tr><th scope="row">BACKLOG</th><td>${mc.backlog || '—'}</td></tr>
                                    <tr><th scope="row">INÍCIO</th><td>${startDateFormatted}</td></tr>
                                    <tr><th scope="row">95% de confiança</th><td class="font-weight-bold">${whenP95}</td></tr>
                                    <tr><th scope="row">85% de confiança</th><td class="font-weight-bold">${whenP85}</td></tr>
                                    <tr><th scope="row">50% de confiança</th><td class="font-weight-bold">${whenP50}</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>`;

        const html = `
            <div class="card">
                <div class="card-header">
                    <h4 class="mb-0">Deadline Analysis Summary</h4>
                </div>
                <div class="card-body">
                    ${summaryHtml}
                    <div class="row">
                        ${visualSummaryHtml}
                        ${mlComparisonHtml}
                        ${consensusHtml}
                    </div>
                    ${chartsHtml}
                </div>
            </div>`;

        $('#deadline-results-summary').html(html);
        $('#deadline-analysis-panels').show();
        $('#deadlineResultsTabs a[href="#deadline-results-summary"]').tab('show');

        renderDeadlineCharts({
            weeks: mcWeeks,
            projected_work_p85: mc.projected_work_p85
        }, ml && !ml.error ? {
            weeks: mlWeeks,
            projected_effort_p85: ml.projected_effort_p85
        } : ml);

        const leadStats = (response.monte_carlo && response.monte_carlo.input_stats && response.monte_carlo.input_stats.lead_time)
            || (response.input_stats && response.input_stats.lead_time)
            || null;

        renderDeadlineSchedule({
            today: moment().format('YYYY-MM-DD'),
            startDate: mc.start_date_raw,
            deadlineDate: mc.deadline_date_raw,
            leadStats: leadStats,
            mcWeeks: mcWeeks
        });
    }

    function runDeadlineAnalysis() {
        const simulationData = readSimulationData({ updateHash: false });
        if (!simulationData) return;

        if (!simulationData.startDate) {
            alert('Please set a project start date before running the deadline analysis.');
            return;
        }

        const deadlineDate = $('#deadlineDate').val();
        if (!deadlineDate) {
            alert('Please provide a deadline date before running the deadline analysis.');
            return;
        }

        // Armazenar dados da simulação globalmente para uso posterior
        window.lastSimulationData = simulationData;

        clearDeadlineCharts();
        $('#deadline-analysis-panels').hide();
        $('#deadline-results-summary').empty();
        $('#deadline-start-window').removeClass('show active');
        $('#deadline-start-tab-item').hide();
        $('#window-too-early, #window-early-start, #window-early-end, #window-just-start, #window-just-end, #window-late-start, #window-late-end, #window-umr, #window-too-late').text('—');
        $('#window-too-early-status, #window-early-status, #window-just-status, #window-late-status, #window-umr-status, #window-too-late-status').empty();
        $('#deadline-analysis-loading').show();

        $.ajax({
            url: '/api/deadline-analysis',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                simulationData: simulationData,
                deadlineDate: deadlineDate,
                startDate: simulationData.startDate,
                nSimulations: simulationData.numberOfSimulations,
                teamFocus: simulationData.teamFocus
            }),
            success: function(result) {
                displayDeadlineAnalysis(result);
            },
            error: function(xhr) {
                $('#deadline-analysis-loading').hide();
                alert('Error running deadline analysis: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }

    function percentile(arr, p) {
        if (arr.length === 0) return 0;
        if (p <= 0) return arr[0];
        if (p >= 1) return arr[arr.length - 1];

        const index = (arr.length - 1) * p;
        const lower = Math.floor(index);
        const upper = lower + 1;
        const weight = index % 1;

        if (upper >= arr.length) return arr[lower];
        return arr[lower] * (1 - weight) + arr[upper] * weight;
    }

    const TAB_HASHES = new Set([
        '',
        '#mc-forecast',
        '#advanced-forecast',
        '#demand-forecast',
        '#deadline-analysis',
        '#historical-charts',
        '#cost-analysis',
        '#trend-analysis',
        '#forecast-vs-actual-tab',
        '#forecast-vs-actual',
        '#dependency-analysis-tab',
        '#dependency-analysis',
        '#executive-dashboard',
        '#dashboard',
        '#portfolio-dashboard',
        '#portfolio'
    ]);

    function loadDataFromUrl() {
        try {
            currentlyLoadedHash = location.hash;
            const normalizedHash = (location.hash || '').trim();
            if (!normalizedHash || TAB_HASHES.has(normalizedHash.toLowerCase())) {
                return false;
            }

            const encoded = normalizedHash.substring(1);
            if (!encoded) return false;

            $.ajax({
                url: '/api/decode',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ encoded: encoded }),
                success: function(simulationData) {
                    for (const name of Object.keys(simulationData)) {
                        const $el = $('#' + name);
                        if ($el.is('input,textarea')) {
                            const val = Array.isArray(simulationData[name]) ?
                                      simulationData[name].join(',') :
                                      simulationData[name];
                            $el.val(val);
                        }
                    }
                    $('#risks').find('.risk-row').remove();
                    if (simulationData.risks && simulationData.risks.length > 0) {
                        for (const risk of simulationData.risks) {
                            fillRisk(risk, addRisk());
                        }
                    }
                    if (simulationData.teamFocusPercent != null) {
                        updateTeamFocusUI(simulationData.teamFocusPercent);
                    } else if (simulationData.teamFocus != null) {
                        updateTeamFocusUI(simulationData.teamFocus * 100);
                    } else {
                        updateTeamFocusUI($('#teamFocusPercent').val());
                    }
                    recalculateBacklog();
                    runSimulation();
                    markHistoricalChartsDirty();
                },
                error: function() {
                    console.error('Error loading data from URL');
                }
            });
            return true;
        } catch (error) {
            console.error(error);
            return false;
        }
    }

        // Export functions and variables defined in window.on("load") to global scope for use by $(function()) block
        window.addRisk = addRisk;
        window.addDependency = addDependency;
        window.runSimulation = runSimulation;
        window.share = share;
        window.markHistoricalChartsDirty = markHistoricalChartsDirty;
        window.runDeadlineAnalysis = runDeadlineAnalysis;
        window.updateHistoricalCharts = updateHistoricalCharts;
        window.loadDataFromUrl = loadDataFromUrl;
        window.updateRiskSummary = updateRiskSummary;
        window.currentlyLoadedHash = currentlyLoadedHash;

        // Initialize UI when DOM is ready (moved inside window.on("load") to ensure functions are available)
        if ($('#backlogMin').length) {
            $('#backlogMin, #backlogMax').on('input change', recalculateBacklog);
            $('#backlogComplexity').on('change', recalculateBacklog);
            recalculateBacklog();
            window.addEventListener('languageChanged', () => {
                updateBacklogSummary(computeBacklogState());
            });
        }

        if ($('#teamFocusPercent').length) {
            $('#teamFocusPercent').on('input change', function() {
                updateTeamFocusUI($(this).val());
            });
            $('.team-focus-preset').on('click', function() {
                updateTeamFocusUI($(this).data('focus'));
            });
            updateTeamFocusUI($('#teamFocusPercent').val());
            window.addEventListener('languageChanged', () => {
                updateTeamFocusUI(getTeamFocusPercent());
            });
        }

        $('#tpSamples, #ltSamples').on('input change', markHistoricalChartsDirty);
        $('a[data-toggle="tab"][href="#historical-charts"]').on('shown.bs.tab', function() {
            updateHistoricalCharts(true);
        });

        updateHistoricalCharts(false);

        if (location.hash && location.hash.trim().length > 1) {
            loadDataFromUrl();
        }

        window.onhashchange = function () {
            if (currentlyLoadedHash != location.hash) {
                location.reload();
            }
        };

        // Risk summary update triggers
        let riskSummaryTimeout;
        function scheduleRiskSummaryUpdate() {
            clearTimeout(riskSummaryTimeout);
            riskSummaryTimeout = setTimeout(updateRiskSummary, 1000);
        }

        // Add risk button with risk summary update
        $('#addRisk').on('click', function() {
            addRisk();
            scheduleRiskSummaryUpdate();
        });

        // Listen for changes in risk inputs to update summary
        $(document).on('input change', '#risks input', function() {
            scheduleRiskSummaryUpdate();
        });

        // Also update on throughput changes (affects time impact calculation)
        $('#tp').on('input change', function() {
            scheduleRiskSummaryUpdate();
        });

        $('#addDependency').on('click', addDependency);
        $('#share').on('click', share);
        $('#run').on('click', runSimulation);
        $('#runDeadlineAnalysis').on('click', runDeadlineAnalysis);
    }); // Close $(window).on("load")

    // Export functions to global scope for inline onclick handlers
    window.recalculateBacklog = recalculateBacklog;
})(window);
