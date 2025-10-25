(function () {
    function safeGetSnapshot() {
        try {
            const raw = localStorage.getItem('ff:lastSimulation');
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (error) {
            console.warn('[Flow Forecaster] Não foi possível carregar o snapshot da simulação.', error);
            return null;
        }
    }

    function formatNumber(value, decimals = 2) {
        if (value === null || value === undefined || Number.isNaN(value)) return '—';
        const f = Number(value);
        if (!Number.isFinite(f)) return '—';
        return f.toFixed(decimals).replace('.', ',');
    }

    function formatInteger(value) {
        if (value === null || value === undefined || Number.isNaN(value)) return '—';
        return Math.round(value).toLocaleString('pt-BR');
    }

    function populateStatsTable(tableId, stats) {
        const tbody = document.querySelector(`${tableId} tbody`);
        if (!tbody || !stats) return;
        const rows = [];
        const labels = {
            count: 'Quantidade de pontos',
            mean: 'Média',
            median: 'Mediana',
            mode: 'Moda',
            std: 'Desvio padrão',
            mad: 'Desvio médio',
            cv: 'Coeficiente de variação (%)',
            min: 'Mínimo',
            max: 'Máximo',
            range: 'Amplitude',
            ratio_p98_p50: 'P98 / P50',
            iqr: 'Amplitude interquartil'
        };
        Object.entries(labels).forEach(([key, label]) => {
            if (stats[key] === undefined || stats[key] === null) return;
            const value = key === 'count' ? formatInteger(stats[key]) : formatNumber(stats[key]);
            rows.push(`<tr><td>${label}</td><td>${value}</td></tr>`);
        });
        const percentiles = stats.percentiles || {};
        if (Object.keys(percentiles).length) {
            Object.entries(percentiles).forEach(([key, value]) => {
                rows.push(`<tr><td>${key.toUpperCase()}</td><td>${formatNumber(value)}</td></tr>`);
            });
        }
        tbody.innerHTML = rows.join('');
    }

    function buildHistogramConfig(samples, opts = {}) {
        const data = Array.isArray(samples) ? samples.map(Number).filter(Number.isFinite) : [];
        if (!data.length) return null;
        data.sort((a, b) => a - b);
        const min = data[0];
        const max = data[data.length - 1];
        const binCount = opts.binCount || Math.min(12, Math.ceil(Math.sqrt(data.length)) + 2);
        const width = (max - min) / (binCount || 1) || 1;
        const bins = new Array(binCount).fill(0);
        data.forEach(value => {
            const idx = Math.min(binCount - 1, Math.floor((value - min) / width));
            bins[idx] += 1;
        });
        const labels = bins.map((_count, idx) => {
            const start = min + idx * width;
            const end = idx === binCount - 1 ? max : start + width;
            return `${formatNumber(start, 1)} - ${formatNumber(end, 1)}`;
        });
        return {
            labels,
            datasets: [{
                label: opts.label || 'Frequência',
                data: bins,
                backgroundColor: opts.color || 'rgba(37, 99, 235, 0.45)',
                borderColor: opts.borderColor || 'rgba(37, 99, 235, 0.9)',
                borderWidth: 1
            }]
        };
    }

    function renderBarChart(canvasId, chartConfig) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !chartConfig) return;
        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: chartConfig,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: { display: false },
                scales: {
                    xAxes: [{
                        gridLines: { display: false },
                        ticks: { fontFamily: 'Inter' }
                    }],
                    yAxes: [{
                        gridLines: { color: 'rgba(148, 163, 184, 0.2)' },
                        ticks: {
                            beginAtZero: true,
                            precision: 0,
                            fontFamily: 'Inter'
                        }
                    }]
                }
            }
        });
    }

    function renderLineChart(canvasId, labels, dataset, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !dataset || !dataset.length) return;
        new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: options.label || 'Série temporal',
                    data: dataset,
                    fill: false,
                    borderColor: options.color || '#2563eb',
                    backgroundColor: options.color || '#2563eb',
                    borderWidth: 2,
                    pointRadius: 2,
                    pointBackgroundColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: { display: false },
                scales: {
                    xAxes: [{ gridLines: { display: false } }],
                    yAxes: [{
                        gridLines: { color: 'rgba(148, 163, 184, 0.2)' },
                        ticks: { beginAtZero: false }
                    }]
                }
            }
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const snapshot = safeGetSnapshot();
        const emptyCard = document.getElementById('stats-empty');
        const content = document.getElementById('stats-content');
        if (!snapshot) {
            if (emptyCard) emptyCard.classList.remove('d-none');
            if (content) content.classList.add('d-none');
            return;
        }

        if (emptyCard) emptyCard.classList.add('d-none');
        if (content) content.classList.remove('d-none');

        const { simulationData = {}, result = {} } = snapshot;
        const backlog = simulationData.backlogAdjustedMax || simulationData.numberOfTasks || 0;
        const teamSize = simulationData.totalContributors || 1;
        const percentileStats = result.percentile_stats || {};

        document.getElementById('stat-backlog').textContent = formatInteger(backlog);
        document.getElementById('stat-team').textContent = formatInteger(teamSize);
        document.getElementById('stat-duration').textContent = formatNumber(percentileStats.p85 || 0, 1) + ' sem';
        document.getElementById('stat-effort').textContent = formatInteger(result.resultsTable ? result.resultsTable[0]?.Effort : null);

        const throughputStats = result.input_stats?.throughput || null;
        const leadStats = result.input_stats?.lead_time || null;
        populateStatsTable('#throughputStatsTable', throughputStats);
        populateStatsTable('#leadStatsTable', leadStats);

        const throughputSamples = simulationData.tpSamples || [];
        const leadSamples = simulationData.ltSamples || [];
        const durationSamples = result.completion_times || [];
        const taskSamples = Array.isArray(result.simulations)
            ? result.simulations.map(item => item.totalTasks)
            : [];

        renderBarChart('throughputHistogram', buildHistogramConfig(throughputSamples, { label: 'Throughput', color: 'rgba(37,99,235,0.45)', borderColor: 'rgba(37,99,235,0.9)' }));
        renderLineChart('throughputControl', throughputSamples.map((_v, idx) => `Semana ${idx + 1}`), throughputSamples, { color: '#22c55e', label: 'Throughput histórico' });

        renderBarChart('leadHistogram', buildHistogramConfig(leadSamples, { label: 'Lead time', color: 'rgba(235,137,37,0.45)', borderColor: 'rgba(235,137,37,0.9)' }));
        renderLineChart('leadControl', leadSamples.map((_v, idx) => `Tarefa ${idx + 1}`), leadSamples, { color: '#f97316', label: 'Lead time' });

        renderBarChart('durationHistogram', buildHistogramConfig(durationSamples, { label: 'Semanas', color: 'rgba(79, 70, 229, 0.4)', borderColor: 'rgba(79, 70, 229, 0.85)' }));
        renderBarChart('tasksHistogram', buildHistogramConfig(taskSamples, { label: 'Tarefas', color: 'rgba(16, 185, 129, 0.35)', borderColor: 'rgba(16, 185, 129, 0.85)' }));
    });
})();
