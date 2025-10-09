const chartsCache = {};

function drawHistogram(id, durations, linePercentile = 85) {
    if (chartsCache[id]) {
        chartsCache[id].destroy();
        chartsCache[id] = null;
    }

    const ctx = document.getElementById(id).getContext('2d');
    const histogram = {};
    for (const val of durations) {
        histogram[val] = (histogram[val] || 0) + 1;
    }

    const keys = Object.keys(histogram).map(Number).sort((a, b) => a - b);
    const labels = keys.map(n => n.toString());
    const data = keys.map(key => histogram[key]);

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

    const lineValue = Math.round(percentile(durations.sort((a, b) => a - b), linePercentile / 100));
    const lineIndex = labels.findIndex(val => lineValue <= Number(val)) - 0.5;

    chartsCache[id] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderWidth: 1,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
            }]
        },
        options: {
            title: {
                display: true,
                text: "Duration histogram"
            },
            legend: {
                display: false
            },
            tooltips: {
                mode: 'index'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Frequency of occurrences'
                    }
                }],
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Calendar weeks'
                    }
                }]
            },
            annotation: {
                drawTime: 'afterDraw',
                annotations: [{
                    type: 'line',
                    mode: 'vertical',
                    value: lineIndex,
                    scaleID: 'x-axis-0',
                    borderColor: 'red',
                    borderWidth: 2,
                    borderDash: [2, 2],
                    label: {
                        enabled: true,
                        content: `p${linePercentile}`,
                        position: 'top',
                        yAdjust: 10,
                        fontSize: 10,
                        backgroundColor: 'rgba(0,0,0,0.6)',
                    }
                }]
            }
        }
    });
}

function drawBurnDowns(id, burnDowns) {
    if (chartsCache[id]) {
        chartsCache[id].destroy();
        chartsCache[id] = null;
    }

    const ctx = document.getElementById(id).getContext('2d');
    const max = Math.max(...burnDowns.map(b => b.length));
    const labels = [];
    for (let i = 1; i <= max; i++) {
        labels.push(i.toString());
    }

    const datasets = burnDowns.map(burnDown => ({
        label: { mode: 'disabled' },
        data: burnDown,
        fill: false,
        borderWidth: 1,
        pointRadius: 0,
        pointHoverRadius: 0,
    }));

    chartsCache[id] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            title: {
                display: true,
                text: "First 100 burn downs"
            },
            legend: {
                display: false
            },
            tooltips: {
                mode: 'disabled'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Remaining tasks'
                    }
                }],
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Week number'
                    }
                }]
            }
        }
    });
}

function drawScatterPlot(id, values, linePercentile = 85) {
    if (chartsCache[id]) {
        chartsCache[id].destroy();
        chartsCache[id] = null;
    }

    const data = values.slice(0, 500).map((val, index) => ({ x: index, y: val }));

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

    const lineValue = Math.round(percentile(values.sort((a, b) => a - b), linePercentile / 100));
    const ctx = document.getElementById(id).getContext('2d');

    chartsCache[id] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                data: data,
                pointBackgroundColor: 'rgba(54, 162, 235, 0.2)',
                pointBorderColor: 'rgba(54, 162, 235, 1)',
            }]
        },
        options: {
            title: {
                display: true,
                text: "Effort scatter plot (first 500 runs)"
            },
            legend: {
                display: false
            },
            tooltips: {
                mode: 'disabled'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Effort in person-weeks'
                    }
                }]
            },
            annotation: {
                drawTime: 'afterDraw',
                annotations: [{
                    type: 'line',
                    mode: 'horizontal',
                    value: lineValue,
                    scaleID: 'y-axis-1',
                    borderColor: 'red',
                    borderWidth: 2,
                    borderDash: [2, 2],
                    label: {
                        enabled: true,
                        content: `p${linePercentile}`,
                        fontSize: 10,
                        backgroundColor: 'rgba(0,0,0,0.6)',
                    }
                }]
            }
        }
    });
}
