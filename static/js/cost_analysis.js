$(document).ready(function() {
    let costChart = null;

    $('#runCostAnalysis').on('click', function() {
        runCostAnalysis();
    });

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

    function formatPercent(value) {
        if (value === null || value === undefined) return '—';
        return (value * 100).toFixed(2) + '%';
    }

    function runCostAnalysis() {
        // Get input values
        const optimistic = parseFloat($('#optimisticCost').val());
        const mostLikely = parseFloat($('#mostLikelyCost').val());
        const pessimistic = parseFloat($('#pessimisticCost').val());
        const backlog = parseInt($('#numberOfTasks').val());
        const nSimulations = parseInt($('#costSimulations').val());
        const avgCostPerItem = parseFloat($('#avgCostPerItem').val()) || null;

        // Get Monte Carlo parameters for team configuration
        const teamSize = parseInt($('#totalContributors').val()) || 1;
        const minContributors = parseInt($('#minContributors').val()) || null;
        const maxContributors = parseInt($('#maxContributors').val()) || null;

        // Get throughput samples
        const tpSamples = $('#tpSamples').val().trim();

        // Validation
        if (!optimistic || !mostLikely || !pessimistic) {
            alert('Por favor, preencha todas as estimativas de custo (otimista, mais provável e pessimista).');
            return;
        }

        if (!(optimistic < mostLikely && mostLikely < pessimistic)) {
            alert('Os valores devem seguir: Otimista < Mais Provável < Pessimista');
            return;
        }

        if (!backlog || backlog <= 0) {
            alert('Por favor, defina um backlog válido na aba Monte Carlo.');
            return;
        }

        if (!tpSamples) {
            alert('Por favor, forneça os dados de throughput na seção "Shared Throughput Data".');
            return;
        }

        // Show loading
        $('#cost-analysis-loading').show();
        $('#cost-analysis-results').hide();

        // Prepare request data
        const requestData = {
            optimistic: optimistic,
            mostLikely: mostLikely,
            pessimistic: pessimistic,
            backlog: backlog,
            nSimulations: nSimulations,
            avgCostPerItem: avgCostPerItem,
            teamSize: teamSize,
            minContributors: minContributors,
            maxContributors: maxContributors,
            tpSamples: tpSamples
        };

        // Call API
        $.ajax({
            url: '/api/cost-analysis',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                displayCostResults(response);
            },
            error: function(xhr) {
                $('#cost-analysis-loading').hide();
                alert('Erro na análise de custos: ' + (xhr.responseJSON?.error || 'Erro desconhecido'));
            }
        });
    }

    function displayCostResults(response) {
        $('#cost-analysis-loading').hide();
        $('#cost-analysis-results').show();

        const results = response.simulation_results;
        const riskMetrics = response.risk_metrics;

        // Display statistics
        let statsHtml = `
            <tr>
                <th scope="row">Custo Médio Total</th>
                <td class="text-right font-weight-bold">${formatCurrency(results.mean)}</td>
            </tr>
            <tr>
                <th scope="row">Desvio Padrão</th>
                <td class="text-right">${formatCurrency(results.std)}</td>
            </tr>
            <tr>
                <th scope="row">Custo Mínimo</th>
                <td class="text-right text-success">${formatCurrency(results.min)}</td>
            </tr>
            <tr>
                <th scope="row">Custo Máximo</th>
                <td class="text-right text-danger">${formatCurrency(results.max)}</td>
            </tr>
            <tr class="border-top">
                <th scope="row">Mediana (P50)</th>
                <td class="text-right font-weight-bold">${formatCurrency(results.percentiles.p50)}</td>
            </tr>
            <tr>
                <th scope="row">Amplitude (Range)</th>
                <td class="text-right">${formatCurrency(riskMetrics.range)}</td>
            </tr>
            <tr>
                <th scope="row">Coef. de Variação</th>
                <td class="text-right">${formatNumber(riskMetrics.coefficient_of_variation, 2)}%</td>
            </tr>
        `;
        $('#cost-stats-table').html(statsHtml);

        // Display scenarios
        let scenariosHtml = `
            <tr>
                <th scope="row">Cenário Otimista (P10)</th>
                <td class="text-right text-success font-weight-bold">${formatCurrency(results.percentiles.p10)}</td>
            </tr>
            <tr>
                <th scope="row">Cenário Realista (P50)</th>
                <td class="text-right text-primary font-weight-bold">${formatCurrency(results.percentiles.p50)}</td>
            </tr>
            <tr>
                <th scope="row">Cenário Conservador (P85)</th>
                <td class="text-right text-warning font-weight-bold">${formatCurrency(results.percentiles.p85)}</td>
            </tr>
            <tr>
                <th scope="row">Cenário Pessimista (P95)</th>
                <td class="text-right text-danger font-weight-bold">${formatCurrency(results.percentiles.p95)}</td>
            </tr>
            <tr class="border-top">
                <th scope="row">Assimetria</th>
                <td class="text-right">${riskMetrics.skewness_indicator}</td>
            </tr>
            <tr>
                <th scope="row">Intervalo Interquartil</th>
                <td class="text-right">${formatCurrency(riskMetrics.iqr)}</td>
            </tr>
        `;

        if (results.prob_below_avg !== null) {
            scenariosHtml += `
                <tr class="border-top">
                    <th scope="row">Prob. abaixo da média histórica</th>
                    <td class="text-right">${formatPercent(results.prob_below_avg)}</td>
                </tr>
            `;
        }

        $('#cost-scenarios-table').html(scenariosHtml);

        // Display percentiles table
        let percentilesHtml = '';
        const percentileLabels = {
            'p10': '10% (Otimista)',
            'p25': '25%',
            'p50': '50% (Mediana)',
            'p75': '75%',
            'p85': '85% (Recomendado)',
            'p90': '90%',
            'p95': '95% (Conservador)'
        };

        for (const [key, label] of Object.entries(percentileLabels)) {
            const cost = results.percentiles[key];
            const prob = parseInt(key.substring(1));
            percentilesHtml += `
                <tr>
                    <td>${label}</td>
                    <td class="text-right font-weight-bold">${formatCurrency(cost)}</td>
                    <td class="text-right">${prob}%</td>
                </tr>
            `;
        }
        $('#cost-percentiles-table').html(percentilesHtml);

        // Display PERT parameters
        let pertParamsHtml = `
            <tr>
                <th scope="row">Alpha (α)</th>
                <td class="text-right">${formatNumber(results.alpha, 4)}</td>
            </tr>
            <tr>
                <th scope="row">Beta (β)</th>
                <td class="text-right">${formatNumber(results.beta, 4)}</td>
            </tr>
            <tr class="border-top">
                <th scope="row">Média PERT por item</th>
                <td class="text-right">${formatCurrency(results.pert_mean_per_item)}</td>
            </tr>
            <tr>
                <th scope="row">Desvio Padrão por item</th>
                <td class="text-right">${formatCurrency(results.pert_std_per_item)}</td>
            </tr>
            <tr class="border-top">
                <th scope="row">Otimista (a) - Ajustado</th>
                <td class="text-right">${formatCurrency(results.optimistic)}</td>
            </tr>
            <tr>
                <th scope="row">Mais Provável (m) - Ajustado</th>
                <td class="text-right">${formatCurrency(results.most_likely)}</td>
            </tr>
            <tr>
                <th scope="row">Pessimista (b) - Ajustado</th>
                <td class="text-right">${formatCurrency(results.pessimistic)}</td>
            </tr>
        `;

        // Add team efficiency metrics if available
        if (results.team_size && results.team_efficiency) {
            pertParamsHtml += `
                <tr class="border-top">
                    <th scope="row">Tamanho da Equipe</th>
                    <td class="text-right">${results.team_size} ${results.team_size === 1 ? 'pessoa' : 'pessoas'}</td>
                </tr>
                <tr>
                    <th scope="row">Fator de Eficiência</th>
                    <td class="text-right">${formatNumber(results.team_efficiency, 4)}</td>
                </tr>
            `;

            if (results.avg_throughput_per_contributor) {
                pertParamsHtml += `
                    <tr>
                        <th scope="row">Throughput Médio/Pessoa</th>
                        <td class="text-right">${formatNumber(results.avg_throughput_per_contributor, 2)} itens/semana</td>
                    </tr>
                `;
            }
        }

        // Show original estimates if they were adjusted
        if (results.original_optimistic && results.team_efficiency !== 1.0) {
            pertParamsHtml += `
                <tr class="border-top">
                    <th scope="row" colspan="2" class="text-center"><em>Estimativas Originais (sem ajuste)</em></th>
                </tr>
                <tr>
                    <th scope="row">Otimista Original</th>
                    <td class="text-right">${formatCurrency(results.original_optimistic)}</td>
                </tr>
                <tr>
                    <th scope="row">Mais Provável Original</th>
                    <td class="text-right">${formatCurrency(results.original_most_likely)}</td>
                </tr>
                <tr>
                    <th scope="row">Pessimista Original</th>
                    <td class="text-right">${formatCurrency(results.original_pessimistic)}</td>
                </tr>
            `;
        }

        pertParamsHtml += `
            <tr class="border-top">
                <th scope="row">Backlog</th>
                <td class="text-right">${results.backlog} itens</td>
            </tr>
            <tr>
                <th scope="row">Simulações</th>
                <td class="text-right">${results.n_simulations.toLocaleString()}</td>
            </tr>
        `;
        $('#pert-params-table').html(pertParamsHtml);

        // Draw histogram
        drawCostHistogram(results);

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#cost-analysis-results').offset().top - 70
        }, 300);
    }

    function drawCostHistogram(results) {
        const ctx = document.getElementById('cost-histogram-chart').getContext('2d');

        // Destroy previous chart if exists
        if (costChart) {
            costChart.destroy();
        }

        // Prepare data
        const histogram = results.histogram;
        const labels = histogram.bin_centers.map(c => formatCurrency(c));

        // Calculate cumulative percentage
        const totalCount = histogram.counts.reduce((a, b) => a + b, 0);
        let cumulative = 0;
        const cumulativeData = histogram.counts.map(count => {
            cumulative += count;
            return (cumulative / totalCount) * 100;
        });

        costChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frequência',
                    data: histogram.counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    yAxisID: 'y-frequency'
                }, {
                    label: '% Cumulativo',
                    data: cumulativeData,
                    type: 'line',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'y-cumulative',
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Distribuição de Custos (PERT-Beta)'
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Custo Total'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45,
                            callback: function(value, index, values) {
                                // Show only every 5th label
                                return index % 5 === 0 ? value : '';
                            }
                        }
                    }],
                    yAxes: [{
                        id: 'y-frequency',
                        type: 'linear',
                        position: 'left',
                        scaleLabel: {
                            display: true,
                            labelString: 'Frequência'
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }, {
                        id: 'y-cumulative',
                        type: 'linear',
                        position: 'right',
                        scaleLabel: {
                            display: true,
                            labelString: '% Cumulativo'
                        },
                        ticks: {
                            beginAtZero: true,
                            max: 100,
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        gridLines: {
                            drawOnChartArea: false
                        }
                    }]
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const datasetLabel = data.datasets[tooltipItem.datasetIndex].label || '';
                            const value = tooltipItem.yLabel;
                            if (datasetLabel === '% Cumulativo') {
                                return datasetLabel + ': ' + value.toFixed(2) + '%';
                            }
                            return datasetLabel + ': ' + value;
                        }
                    }
                },
                annotation: {
                    annotations: [
                        {
                            type: 'line',
                            mode: 'vertical',
                            scaleID: 'x-axis-0',
                            value: formatCurrency(results.percentiles.p50),
                            borderColor: 'red',
                            borderWidth: 2,
                            label: {
                                enabled: true,
                                content: 'P50',
                                position: 'top'
                            }
                        }
                    ]
                }
            }
        });
    }

    // ===== EFFORT-BASED COST ANALYSIS =====
    $('#runEffortCostAnalysis').on('click', function() {
        runEffortCostAnalysis();
    });

    // PERT-Beta simulation for effort
    function runPertBetaEffortSimulation(optimistic, mostLikely, pessimistic, nSimulations) {
        // Calculate PERT-Beta parameters
        // Mean = (a + 4m + b) / 6
        const mean = (optimistic + 4 * mostLikely + pessimistic) / 6;

        // Standard deviation = (b - a) / 6
        const stdDev = (pessimistic - optimistic) / 6;

        // Calculate alpha and beta for Beta distribution
        // Using method of moments
        const range = pessimistic - optimistic;
        const variance = stdDev * stdDev;

        // Beta distribution parameters
        const alpha = ((mean - optimistic) / range) * (((mean - optimistic) * (pessimistic - mean) / variance) - 1);
        const beta = ((pessimistic - mean) / range) * (((mean - optimistic) * (pessimistic - mean) / variance) - 1);

        // Generate samples using Beta distribution
        const samples = [];
        for (let i = 0; i < nSimulations; i++) {
            // Generate beta-distributed random value
            const betaValue = generateBetaRandom(alpha, beta);
            // Scale to [optimistic, pessimistic] range
            const effort = optimistic + betaValue * range;
            samples.push(effort);
        }

        // Sort samples for percentile calculation
        samples.sort((a, b) => a - b);

        // Calculate percentiles
        const p50Index = Math.floor(nSimulations * 0.50);
        const p85Index = Math.floor(nSimulations * 0.85);
        const p95Index = Math.floor(nSimulations * 0.95);

        return {
            p50: samples[p50Index],
            p85: samples[p85Index],
            p95: samples[p95Index]
        };
    }

    // Generate Beta-distributed random number using Gamma distributions
    function generateBetaRandom(alpha, beta) {
        const x = generateGammaRandom(alpha);
        const y = generateGammaRandom(beta);
        return x / (x + y);
    }

    // Generate Gamma-distributed random number (Marsaglia and Tsang method)
    function generateGammaRandom(shape) {
        if (shape < 1) {
            // Use rejection method for shape < 1
            const u = Math.random();
            return generateGammaRandom(shape + 1) * Math.pow(u, 1 / shape);
        }

        const d = shape - 1/3;
        const c = 1 / Math.sqrt(9 * d);

        while (true) {
            let x, v;
            do {
                x = generateNormalRandom();
                v = 1 + c * x;
            } while (v <= 0);

            v = v * v * v;
            const u = Math.random();

            if (u < 1 - 0.0331 * x * x * x * x) {
                return d * v;
            }

            if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) {
                return d * v;
            }
        }
    }

    // Generate standard normal random number (Box-Muller transform)
    function generateNormalRandom() {
        const u1 = Math.random();
        const u2 = Math.random();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    function runEffortCostAnalysis() {
        const costPerWeek = parseFloat($('#costPerPersonWeek').val());
        const manualEffort = parseFloat($('#effortPersonWeeks').val());

        // PERT-Beta fields
        const effortOptimistic = parseFloat($('#effortOptimistic').val());
        const effortMostLikely = parseFloat($('#effortMostLikely').val());
        const effortPessimistic = parseFloat($('#effortPessimistic').val());
        const effortSimulations = parseInt($('#effortSimulations').val()) || 10000;

        // Validation
        if (!costPerWeek || costPerWeek <= 0) {
            alert('Por favor, defina um custo por pessoa-semana válido.');
            return;
        }

        // Try to get effort from PERT-Beta simulation first
        let effortData = null;

        if (effortOptimistic && effortMostLikely && effortPessimistic) {
            // Validate PERT values
            if (!(effortOptimistic < effortMostLikely && effortMostLikely < effortPessimistic)) {
                alert('Os valores PERT devem seguir: Otimista < Mais Provável < Pessimista');
                return;
            }

            // Run PERT-Beta simulation
            effortData = runPertBetaEffortSimulation(
                effortOptimistic,
                effortMostLikely,
                effortPessimistic,
                effortSimulations
            );
        } else if (window.lastSimulationResult && window.lastSimulationResult.percentile_stats) {
            // Use Monte Carlo projections
            const percentiles = window.lastSimulationResult.percentile_stats;
            const teamSize = parseInt($('#totalContributors').val()) || 1;

            effortData = {
                p50: (percentiles.p50 || 0) * teamSize,
                p85: (percentiles.p85 || 0) * teamSize,
                p95: (percentiles.p95 || 0) * teamSize
            };
        } else if (manualEffort && manualEffort > 0) {
            // Use manual effort input
            effortData = {
                p50: manualEffort * 0.83,  // Approximate P50
                p85: manualEffort,          // User input as P85
                p95: manualEffort * 1.17    // Approximate P95
            };
        } else {
            alert('Execute uma simulação Monte Carlo, insira um esforço estimado manualmente, ou preencha os campos PERT-Beta.');
            return;
        }

        // Calculate costs
        const costs = {
            p50: effortData.p50 * costPerWeek,
            p85: effortData.p85 * costPerWeek,
            p95: effortData.p95 * costPerWeek
        };

        // Display results
        $('#effort-cost-p50').text(formatCurrency(costs.p50));
        $('#effort-weeks-p50').text(`${effortData.p50.toFixed(1)} pessoa-semanas`);

        $('#effort-cost-p85').text(formatCurrency(costs.p85));
        $('#effort-weeks-p85').text(`${effortData.p85.toFixed(1)} pessoa-semanas`);

        $('#effort-cost-p95').text(formatCurrency(costs.p95));
        $('#effort-weeks-p95').text(`${effortData.p95.toFixed(1)} pessoa-semanas`);

        // Display rates table
        const monthlyRate = costPerWeek * 4.33;  // 4.33 weeks/month average
        const yearlyRate = costPerWeek * 52;     // 52 weeks/year

        let ratesHtml = `
            <tr>
                <th scope="row">Por Pessoa-Semana</th>
                <td class="text-right font-weight-bold">${formatCurrency(costPerWeek)}</td>
            </tr>
            <tr>
                <th scope="row">Por Pessoa-Mês (4.33 semanas)</th>
                <td class="text-right">${formatCurrency(monthlyRate)}</td>
            </tr>
            <tr>
                <th scope="row">Por Pessoa-Ano (52 semanas)</th>
                <td class="text-right">${formatCurrency(yearlyRate)}</td>
            </tr>
        `;
        $('#effort-cost-rates-table').html(ratesHtml);

        // Show results
        $('#effort-cost-results').show();

        // Scroll to results
        $('html, body').animate({
            scrollTop: $('#effort-cost-results').offset().top - 70
        }, 300);
    }
});
