(function () {
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
})();

$(window).on("load", function () {
    $('[data-toggle="tooltip"]').tooltip({ delay: 500 });

    function parseSamples(selector) {
        let val = $(selector).val() || '';
        if (val.trim().length === 0) return [];
        return val.split(/[\s\n,]/)
            .map(s => s.trim().length > 0 ? Number(s.trim()) : NaN)
            .filter(n => !isNaN(n))
            .filter(n => n >= 0);
    }

    const deadlineCharts = [];

    function parseRisks(selector) {
        const risks = [];
        $(selector).find('tbody').find('.risk-row').each((_index, el) => {
            const $el = $(el);
            const risk = {
                likelihood: $el.find("input[name='likelihood']").val(),
                lowImpact: $el.find("input[name='lowImpact']").val(),
                highImpact: $el.find("input[name='highImpact']").val(),
                description: $el.find("input[name='description']").val(),
            };
            if (risk.likelihood && (risk.lowImpact || risk.highImpact)) {
                if (!risk.lowImpact) risk.lowImpact = '1';
                else if (!risk.highImpact) risk.highImpact = risk.lowImpact;
                risk.likelihood = parseInt(risk.likelihood) || 0;
                risk.lowImpact = parseInt(risk.lowImpact) || 0;
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
        return $row;
    }

    function fillRisk(risk, $row) {
        $row.find("input[name='likelihood']").val(risk.likelihood);
        $row.find("input[name='lowImpact']").val(risk.lowImpact);
        $row.find("input[name='highImpact']").val(risk.highImpact);
        $row.find("input[name='description']").val(risk.description);
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

    let currentlyLoadedHash = null;

    function readSimulationData(options = {}) {
        const { updateHash = true } = options;
        const simulationData = {
            projectName: $('#projectName').val(),
            numberOfSimulations: parseInt($('#numberOfSimulations').val()),
            confidenceLevel: parseInt($('#confidenceLevel').val()) || 85,
            tpSamples: parseSamples('#tpSamples'),
            ltSamples: parseSamples('#ltSamples'),
            splitRateSamples: parseSamples('#splitRateSamples'),
            risks: parseRisks('#risks'),
            numberOfTasks: parseInt($('#numberOfTasks').val()),
            totalContributors: parseInt($('#totalContributors').val()),
            minContributors: parseInt($('#minContributors').val()) || parseInt($('#totalContributors').val()),
            maxContributors: parseInt($('#maxContributors').val()) || parseInt($('#totalContributors').val()),
            sCurveSize: parseInt($('#sCurveSize').val()),
            startDate: $('#startDate').val() || undefined,
            deadlineDate: $('#deadlineDate').val() || undefined
        };

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

        $('#results-main').show();
        const $results = $('#results');
        $results.val('');
        $('#res-effort').val('Running...');

        // Call backend API
        $.ajax({
            url: '/api/simulate',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(simulationData),
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

        $('#res-summary-header').text(`Project forecast summary (with ${confidenceLevel}% of confidence):`);
        $('#res-effort').val(effort);
        $('#res-duration').val(duration);

        let endDate = '(No start date set)';
        if (simulationData.startDate) {
            endDate = moment(simulationData.startDate).add(duration, 'weeks').format("MMM Do YYYY");
        }
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
                $cells.eq(4).text(moment(simulationData.startDate).add(res.Duration, 'weeks').format("MMM Do YYYY"));
            }
            $cells.eq(5).text(comment);
        };

        result.resultsTable.slice(0, 9).forEach(addProbability);
        $('#show-more').off('click').on('click', () => {
            result.resultsTable.slice(9).forEach(addProbability);
            $('#show-more').off('click').hide();
            $('#show-more-row').hide();
        });

        // Draw charts
        drawHistogram('res-duration-histogram', durationValues, confidenceLevel);
        drawBurnDowns('res-burn-downs', result.burnDowns);
        drawScatterPlot('res-effort-scatter-plot', effortValues, confidenceLevel);

        // Write text report
        write(`Project forecast summary (with ${confidenceLevel}% of confidence):\n`);
        write(` - Up to ${effort} person-weeks of effort\n`);
        write(` - Can be delivered in up to ${duration} calendar weeks\n`);
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
        const $block = $('#deadline-start-guidance');
        if (!$block.length) return;

        const leadStats = options.leadStats || null;
        if (!leadStats || !leadStats.percentiles) {
            $block.hide();
            return;
        }

        const percentiles = leadStats.percentiles;
        const p50 = percentiles.p50;
        const p85 = percentiles.p85;
        const p100 = percentiles.p100;

        if (!options.deadlineDate || !p50 || !p85 || !p100) {
            $block.hide();
            return;
        }

        const deadline = moment(options.deadlineDate, ['YYYY-MM-DD', 'DD/MM/YYYY', moment.ISO_8601], true);
        if (!deadline.isValid()) {
            $block.hide();
            return;
        }

        const today = moment(options.today, ['YYYY-MM-DD', moment.ISO_8601], true);
        const startDate = options.startDate ? moment(options.startDate, ['YYYY-MM-DD', 'DD/MM/YYYY', moment.ISO_8601], true) : null;

        const tooEarly = deadline.clone().subtract(p100 * 2, 'days');
        const earlyStart = deadline.clone().subtract(p100 * 2, 'days');
        const earlyEnd = deadline.clone().subtract(p100, 'days');
        const justStart = deadline.clone().subtract(p100, 'days');
        const justEnd = deadline.clone().subtract(p85, 'days');
        const lateStart = deadline.clone().subtract(p85, 'days');
        const lateEnd = deadline.clone().subtract(p50, 'days');
        const umr = deadline.clone().subtract(p50, 'days');

        $('#window-too-early').text(tooEarly.format('DD/MM/YY'));
        $('#window-early-start').text(earlyStart.format('DD/MM/YY'));
        $('#window-early-end').text(earlyEnd.format('DD/MM/YY'));
        $('#window-just-start').text(justStart.format('DD/MM/YY'));
        $('#window-just-end').text(justEnd.format('DD/MM/YY'));
        $('#window-late-start').text(lateStart.format('DD/MM/YY'));
        $('#window-late-end').text(lateEnd.format('DD/MM/YY'));
        $('#window-umr').text(umr.format('DD/MM/YY'));

        let statusText = '';
        let statusClass = '';
        if (startDate && startDate.isValid()) {
            if (startDate.isBefore(earlyStart)) {
                statusText = 'Muito cedo';
                statusClass = 'badge-warning';
            } else if (startDate.isBefore(earlyEnd)) {
                statusText = 'Cedo';
                statusClass = 'badge-warning';
            } else if (startDate.isBetween(justStart, justEnd, undefined, '[]')) {
                statusText = 'OK';
                statusClass = 'badge-success';
            } else if (startDate.isBetween(lateStart, lateEnd, undefined, '[]')) {
                statusText = 'Tarde';
                statusClass = 'badge-warning';
            } else if (startDate.isAfter(umr)) {
                statusText = 'Atrasado';
                statusClass = 'badge-danger';
            }
        } else if (today && today.isValid()) {
            if (today.isBefore(earlyStart)) {
                statusText = 'Muito cedo';
                statusClass = 'badge-warning';
            } else if (today.isBefore(earlyEnd)) {
                statusText = 'Cedo';
                statusClass = 'badge-warning';
            } else if (today.isBetween(justStart, justEnd, undefined, '[]')) {
                statusText = 'OK';
                statusClass = 'badge-success';
            } else if (today.isBetween(lateStart, lateEnd, undefined, '[]')) {
                statusText = 'Tarde';
                statusClass = 'badge-warning';
            } else if (today.isAfter(umr)) {
                statusText = 'Atrasado';
                statusClass = 'badge-danger';
            }
        }

        $('#window-just-status').html(statusText ? `<span class="badge ${statusClass}">${statusText}</span>` : '');
        $('#window-too-late').text(umr.clone().add(1, 'days').format('DD/MM/YY'));

        $block.show();
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

        const mcHtml = `
            <div class="col-lg-6">
                <div class="card h-100 shadow-sm">
                    <div class="card-body text-left">
                        <h5 class="card-title">Monte Carlo</h5>
                        <p class="mb-1"><strong>Deadline:</strong> ${mc.deadline_date || '—'}</p>
                        <p class="mb-1"><strong>Weeks to deadline:</strong> ${formatWeeks(mc.weeks_to_deadline)}</p>
                        <p class="mb-1"><strong>P85 completion:</strong> ${formatWeeks(mcWeeks.p85)} weeks</p>
                        <p class="mb-1"><strong>P50 completion:</strong> ${formatWeeks(mcWeeks.p50)} weeks</p>
                        <p class="mb-1"><strong>Projected work (P85):</strong> ${mc.projected_work_p85 ?? '—'} tasks</p>
                        <div class="mt-3">${verdictBadge(mc.can_meet_deadline)}</div>
                    </div>
                </div>
            </div>`;

        let mlHtml;
        if (ml && !ml.error) {
            mlHtml = `
                <div class="col-lg-6 mt-3 mt-lg-0">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body text-left">
                            <h5 class="card-title">Machine Learning</h5>
                            <p class="mb-1"><strong>P85 completion:</strong> ${formatWeeks(mlWeeks.p85)} weeks</p>
                            <p class="mb-1"><strong>P50 completion:</strong> ${formatWeeks(mlWeeks.p50)} weeks</p>
                            <p class="mb-1"><strong>Projected effort (P85):</strong> ${ml.projected_effort_p85 ?? '—'} person-weeks</p>
                            <div class="mt-3">${verdictBadge(ml.can_meet_deadline)}</div>
                        </div>
                    </div>
                </div>`;
        } else {
            const errorMsg = ml && ml.error ? ml.error : 'ML forecast requires at least 8 throughput samples.';
            mlHtml = `
                <div class="col-lg-6 mt-3 mt-lg-0">
                    <div class="alert alert-warning h-100 mb-0 text-left" role="alert">
                        <h5 class="alert-heading">Machine Learning</h5>
                        <p class="mb-0">${errorMsg}</p>
                    </div>
                </div>`;
        }

        let consensusHtml = '';
        if (consensus) {
            consensusHtml = `
                <div class="alert ${consensus.both_agree ? 'alert-success' : 'alert-warning'} mt-4 text-left" role="alert">
                    <h5 class="alert-heading">Consensus</h5>
                    <p class="mb-1">Both methods agree: <strong>${consensus.both_agree ? 'Yes' : 'No'}</strong></p>
                    <p class="mb-1">Difference between P85 projections: ${formatWeeks(consensus.difference_weeks)} weeks.</p>
                    <p class="mb-0">${consensus.recommendation}</p>
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

        const html = `
            <div class="card">
                <div class="card-header">
                    <h4 class="mb-0">Deadline Analysis Summary</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        ${mcHtml}
                        ${mlHtml}
                    </div>
                    ${consensusHtml}
                    ${chartsHtml}
                </div>
            </div>`;

        $('#deadline-analysis-results').html(html).fadeIn();
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
            leadStats: leadStats
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

        clearDeadlineCharts();
        $('#deadline-analysis-results').hide().empty();
        $('#deadline-analysis-loading').show();

        $.ajax({
            url: '/api/deadline-analysis',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                simulationData: simulationData,
                deadlineDate: deadlineDate,
                startDate: simulationData.startDate,
                nSimulations: simulationData.numberOfSimulations
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

    function loadDataFromUrl() {
        try {
            currentlyLoadedHash = location.hash;
            const encoded = location.hash.trim().substring(1);
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
                    runSimulation();
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

    if (location.hash && location.hash.trim().length > 1) {
        loadDataFromUrl();
    }

    window.onhashchange = function () {
        if (currentlyLoadedHash != location.hash) {
            location.reload();
        }
    };

    $('#addRisk').on('click', addRisk);
    $('#share').on('click', share);
    $('#run').on('click', runSimulation);
    $('#runDeadlineAnalysis').on('click', runDeadlineAnalysis);
});
