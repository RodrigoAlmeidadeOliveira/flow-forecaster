/**
 * Forecast Persistence Module
 * Handles saving and loading forecasts to/from database
 */

let saveModalLoading = false;
let cachedProjects = [];
let cachedPortfolios = [];

// Open save modal
function openSaveModal() {
    populateSaveForecastSelectors();
    $('#saveForecastModal').modal('show');
}

async function populateSaveForecastSelectors() {
    if (saveModalLoading) {
        return;
    }

    saveModalLoading = true;
    const projectSelect = $('#forecastProjectSelect');
    const portfolioSelect = $('#forecastPortfolioSelect');

    try {
        projectSelect.html('<option value="">Carregando projetos...</option>');
        portfolioSelect.html('<option value="">Carregando portfólios...</option>');

        const [projects, portfolios] = await Promise.all([
            fetch('/api/projects', { credentials: 'include' }),
            fetch('/api/portfolios', { credentials: 'include' })
        ]);

        if (!projects.ok) {
            throw new Error('Não foi possível obter a lista de projetos.');
        }
        if (!portfolios.ok) {
            throw new Error('Não foi possível obter a lista de portfólios.');
        }

        cachedProjects = await projects.json();
        cachedPortfolios = await portfolios.json();

        projectSelect.empty();
        projectSelect.append('<option value="">Selecione um projeto existente...</option>');
        cachedProjects.forEach(project => {
            projectSelect.append(`<option value="${project.id}">${escapeHtml(project.name)}</option>`);
        });

        portfolioSelect.empty();
        portfolioSelect.append('<option value="">Não associar agora</option>');
        cachedPortfolios.forEach(portfolio => {
            portfolioSelect.append(`<option value="${portfolio.id}">${escapeHtml(portfolio.name)} (${portfolio.projects_count || 0} projetos)</option>`);
        });

    } catch (error) {
        console.error('Erro ao carregar projetos/portfólios:', error);
        projectSelect.html('<option value="">Erro ao carregar projetos</option>');
        portfolioSelect.html('<option value="">Erro ao carregar portfólios</option>');
    } finally {
        saveModalLoading = false;
    }
}

function normalizeSamples(samples) {
    if (!Array.isArray(samples)) {
        return [];
    }
    return samples
        .map(value => {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : null;
        })
        .filter(value => Number.isFinite(value) && value > 0);
}

async function ensureProjectInPortfolio(portfolioId, projectId) {
    if (!portfolioId || !projectId) {
        return;
    }

    try {
        const response = await fetch(`/api/portfolios/${portfolioId}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ project_id: projectId })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            if (error.error && !/already in portfolio/i.test(error.error)) {
                throw new Error(error.error);
            }
        }
    } catch (error) {
        console.error('Erro ao vincular projeto ao portfólio:', error);
        alert('Aviso: não foi possível vincular o projeto ao portfólio. Adicione manualmente pelo gerenciador de portfólio.');
    }
}

$(document).ready(function() {
    $('#forecastProjectSelect').on('change', function() {
        if ($(this).val()) {
            $('#projectName').val('');
        }
    });

    $('#projectName').on('input', function() {
        if ($(this).val().trim().length) {
            $('#forecastProjectSelect').val('');
        }
    });
});

// Open load modal and fetch forecasts
function openLoadModal() {
    $('#loadForecastModal').modal('show');
    loadForecasts();
}

// Save forecast to database
async function saveForecast() {
    const name = $('#forecastName').val().trim();
    if (!name) {
        alert('Por favor, informe um nome para a análise');
        return;
    }

    const projectIdValue = $('#forecastProjectSelect').val();
    const projectNameInput = $('#projectName').val().trim();
    const portfolioIdValue = $('#forecastPortfolioSelect').val();

    if (!projectIdValue && !projectNameInput) {
        alert('Selecione um projeto existente ou informe um novo nome de projeto.');
        return;
    }

    try {
        const simulationData = window.lastSimulationData || {};
        const throughputSamples = (simulationData.tpSamples && simulationData.tpSamples.length)
            ? simulationData.tpSamples
            : collectThroughputSamples();
        const cleanedSamples = normalizeSamples(throughputSamples);

        if (!cleanedSamples.length) {
            alert('Nenhuma amostra de throughput válida foi encontrada. Execute a simulação antes de salvar.');
            return;
        }

        const backlogValue = Number.isFinite(simulationData.numberOfTasks)
            ? simulationData.numberOfTasks
            : getCurrentBacklog();

        // Collect all current state
        const inputData = {
            tpSamples: cleanedSamples,
            tp_samples: cleanedSamples,
            throughput_samples: cleanedSamples,
            backlog: backlogValue,
            numberOfTasks: backlogValue,
            teamSize: Number.isFinite(simulationData.totalContributors)
                ? simulationData.totalContributors
                : parseInt($('#totalContributors').val() || 0, 10),
            workingDays: Number.isFinite(simulationData.throughputCadenceDays)
                ? simulationData.throughputCadenceDays
                : 5,
            startDate: simulationData.startDate || $('#startDate').val(),
            endDate: simulationData.endDate || '',
            deadlineDate: simulationData.deadlineDate || $('#deadlineDate').val(),
            risks: collectRisks(),
            dependencies: collectDependencies(),
            teamFocus: Number.isFinite(simulationData.teamFocus)
                ? simulationData.teamFocus
                : getTeamFocusFactor(),
            confidenceLevel: Number.isFinite(simulationData.confidenceLevel)
                ? simulationData.confidenceLevel
                : parseInt($('#confidenceLevel').val() || 85, 10),
            numberOfSimulations: Number.isFinite(simulationData.numberOfSimulations)
                ? simulationData.numberOfSimulations
                : parseInt($('#numberOfSimulations').val() || 10000, 10)
        };

        // Get last simulation results if available
        const forecastData = window.lastSimulationResults || {};

        // Prepare payload
        const projectNameForPayload = projectNameInput ||
            $('#forecastProjectSelect option:selected').text().trim() ||
            'Default Project';

        const payload = {
            name: name,
            description: $('#forecastDescription').val() || '',
            project_name: projectNameForPayload,
            forecast_type: 'deadline',
            input_data: inputData,
            forecast_data: forecastData,
            backlog: inputData.backlog,
            deadline_date: inputData.deadlineDate,
            start_date: inputData.startDate,
            projected_weeks_p85: forecastData.duration_p85,
            can_meet_deadline: forecastData.can_meet_deadline,
            scope_completion_pct: forecastData.scope_completion_pct
        };

        if (projectIdValue) {
            payload.project_id = parseInt(projectIdValue, 10);
        }

        if (portfolioIdValue) {
            payload.portfolio_context = {
                portfolio_id: parseInt(portfolioIdValue, 10)
            };
        }

        // Save to API
        const response = await fetch('/api/forecasts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao salvar análise');
        }

        const result = await response.json();

        if (portfolioIdValue) {
            await ensureProjectInPortfolio(parseInt(portfolioIdValue, 10), result.project_id);
        }

        // Clear form and close modal
        $('#saveForecastForm')[0].reset();
        $('#saveForecastModal').modal('hide');

        alert('Análise salva com sucesso! Os dados agora estão disponíveis para simulação no portfólio.');

    } catch (error) {
        console.error('Error saving forecast:', error);
        alert('Erro ao salvar análise: ' + error.message);
    }
}

// Load forecasts list from database
async function loadForecasts() {
    try {
        $('#loadingForecasts').show();
        $('#forecastsList').empty();

        const response = await fetch('/api/forecasts', { credentials: 'include' });

        if (!response.ok) {
            throw new Error('Erro ao carregar análises');
        }

        const forecasts = await response.json();

        $('#loadingForecasts').hide();

        if (!Array.isArray(forecasts)) {
            $('#forecastsList').html('<p class="text-danger">Erro: resposta inválida da API.</p>');
            return;
        }

        if (forecasts.length === 0) {
            $('#forecastsList').html('<p class="text-muted">Nenhuma análise salva ainda.</p>');
            return;
        }

        // Build forecast cards
        let html = '<div class="list-group">';
        forecasts.forEach(forecast => {
            const date = new Date(forecast.created_at).toLocaleDateString('pt-BR');
            const time = new Date(forecast.created_at).toLocaleTimeString('pt-BR');

            html += `
                <div class="list-group-item list-group-item-action flex-column align-items-start">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${escapeHtml(forecast.name)}</h5>
                        <small>${date} ${time}</small>
                    </div>
                    ${forecast.description ? `<p class="mb-1">${escapeHtml(forecast.description)}</p>` : ''}
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            Projeto: ${escapeHtml(forecast.project_name || 'N/A')} |
                            Backlog: ${forecast.backlog || 'N/A'} |
                            Prazo: ${forecast.deadline_date || 'N/A'}
                        </small>
                        <div>
                            <button class="btn btn-sm btn-primary" onclick="loadForecast(${forecast.id})">
                                <i class="fas fa-upload"></i> Carregar
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteForecast(${forecast.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                            <a href="/api/forecasts/${forecast.id}/export" class="btn btn-sm btn-info" download>
                                <i class="fas fa-download"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        $('#forecastsList').html(html);

    } catch (error) {
        console.error('Error loading forecasts:', error);
        $('#loadingForecasts').hide();
        $('#forecastsList').html(`<p class="text-danger">Erro ao carregar análises: ${error.message}</p>`);
    }
}

// Load a specific forecast
async function loadForecast(id) {
    try {
        const response = await fetch(`/api/forecasts/${id}`, { credentials: 'include' });
        if (!response.ok) {
            throw new Error('Erro ao carregar análise');
        }

        const forecast = await response.json();

        // Restore input data
        const input = forecast.input_data;

        // Restore throughput samples
        if (input.tpSamples && Array.isArray(input.tpSamples)) {
            $('#tpSamples').val(input.tpSamples.join(', '));
        }

        // Restore basic fields
        if (Number.isFinite(input.backlog)) {
            $('#numberOfTasks').val(input.backlog);
            $('#backlog').val(input.backlog);
            if (typeof window.recalculateBacklog === 'function') {
                window.recalculateBacklog();
            }
        }

        if (Number.isFinite(input.teamSize)) {
            $('#totalContributors').val(input.teamSize);
            $('#minContributors').val(input.teamSize);
            $('#maxContributors').val(input.teamSize);
        }

        if (Number.isFinite(input.numberOfSimulations)) {
            $('#numberOfSimulations').val(input.numberOfSimulations);
        }

        if (Number.isFinite(input.confidenceLevel)) {
            $('#confidenceLevel').val(input.confidenceLevel);
        }

        $('#startDate').val(input.startDate || '');
        $('#deadlineDate').val(input.deadlineDate || '');
        if (typeof input.teamFocus === 'number') {
            const percent = Math.round(input.teamFocus * 100);
            $('#teamFocusPercent').val(percent).trigger('change');
        }

        // Restore risks
        if (input.risks && Array.isArray(input.risks)) {
            // Clear existing risks
            $('#risks .risk-row').not('#risk-row-template').remove();
            input.risks.forEach(risk => {
                if (typeof window.addRisk === 'function') {
                    const $row = window.addRisk();
                    if ($row && $row.length) {
                        $row.find("input[name='likelihood']").val(risk.likelihood || '');
                        $row.find("input[name='lowImpact']").val(risk.lowImpact || '');
                        $row.find("input[name='mediumImpact']").val(risk.mediumImpact || '');
                        $row.find("input[name='highImpact']").val(risk.highImpact || '');
                        $row.find("input[name='description']").val(risk.description || '');
                    }
                }
            });
            if (typeof window.updateRiskSummary === 'function') {
                window.updateRiskSummary();
            }
        }

        // Restore dependencies
        if (input.dependencies && Array.isArray(input.dependencies)) {
            $('#dependencies .dependency-row').not('#dependency-row-template').remove();
            input.dependencies.forEach(dep => {
                if (typeof window.addDependency === 'function') {
                    const $row = window.addDependency();
                    if ($row && $row.length) {
                        $row.find("input[name='dependency_name']").val(dep.name || '');
                        $row.find("input[name='dependency_source_project']").val(dep.source_project || '');
                        $row.find("input[name='dependency_target_project']").val(dep.target_project || '');
                        $row.find("input[name='dep_probability']").val(
                            dep.on_time_probability != null ? Math.round(dep.on_time_probability * 100) : ''
                        );
                        $row.find("input[name='dep_delay']").val(dep.delay_impact_days || '');
                        $row.find("select[name='dependency_criticality']").val(dep.criticality || 'MEDIUM');
                    }
                }
            });
        }

        window.lastSimulationData = input;
        if (forecast.forecast_data) {
            window.lastSimulationResults = forecast.forecast_data;
        }
        if (typeof window.updateCurrentKPIs === 'function') {
            window.updateCurrentKPIs();
        }
        if (typeof window.updateProjectHealth === 'function') {
            window.updateProjectHealth();
        }

        // Close modal
        $('#loadForecastModal').modal('hide');

        alert('Análise carregada com sucesso! Execute a simulação para ver os resultados.');

    } catch (error) {
        console.error('Error loading forecast:', error);
        alert('Erro ao carregar análise: ' + error.message);
    }
}

// Delete a forecast
async function deleteForecast(id) {
    if (!confirm('Tem certeza que deseja excluir esta análise?')) {
        return;
    }

    try {
        const response = await fetch(`/api/forecasts/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao excluir análise');
        }

        // Reload list
        loadForecasts();

    } catch (error) {
        console.error('Error deleting forecast:', error);
        alert('Erro ao excluir análise: ' + error.message);
    }
}

// Helper functions

function collectThroughputSamples() {
    const text = $('#tpSamples').val() || '';
    if (!text.trim()) return [];
    return text
        .split(/[\s,;]+/)
        .map(value => parseFloat(value.trim()))
        .filter(value => !Number.isNaN(value) && value > 0);
}

function collectRisks() {
    const risks = [];
    $('#risks .risk-row')
        .not('#risk-row-template')
        .each(function() {
            const $row = $(this);
            const likelihood = parseInt($row.find("input[name='likelihood']").val() || '0', 10);
            const lowImpact = parseInt($row.find("input[name='lowImpact']").val() || '0', 10);
            const mediumImpact = parseInt($row.find("input[name='mediumImpact']").val() || '0', 10);
            const highImpact = parseInt($row.find("input[name='highImpact']").val() || '0', 10);
            const description = $row.find("input[name='description']").val() || '';

            if (likelihood || lowImpact || mediumImpact || highImpact || description) {
                risks.push({
                    likelihood,
                    lowImpact,
                    mediumImpact,
                    highImpact,
                    description
                });
            }
        });
    return risks;
}

function collectDependencies() {
    const dependencies = [];
    $('#dependencies .dependency-row')
        .not('#dependency-row-template')
        .each(function() {
            const $row = $(this);
            const name = $row.find("input[name='dependency_name']").val();
            const source = $row.find("input[name='dependency_source_project']").val();
            const target = $row.find("input[name='dependency_target_project']").val();

            if (!name || !source || !target) {
                return;
            }

            dependencies.push({
                name,
                source_project: source,
                target_project: target,
                on_time_probability: parseFloat($row.find("input[name='dep_probability']").val() || '0') / 100,
                delay_impact_days: parseFloat($row.find("input[name='dep_delay']").val() || '0'),
                criticality: $row.find("select[name='dependency_criticality']").val() || 'MEDIUM'
            });
        });
    return dependencies;
}

function getCurrentBacklog() {
    const hiddenBacklog = parseInt($('#numberOfTasks').val() || '0', 10);
    if (Number.isFinite(hiddenBacklog) && hiddenBacklog > 0) {
        return hiddenBacklog;
    }
    const advancedBacklog = parseInt($('#backlog').val() || '0', 10);
    return Number.isFinite(advancedBacklog) ? advancedBacklog : 0;
}

function getTeamFocusFactor() {
    const slider = parseFloat($('#teamFocusPercent').val() || '100');
    if (!Number.isFinite(slider)) return 1;
    return Math.round((slider / 100) * 1000) / 1000;
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Import forecast from JSON file
async function importForecastFromFile() {
    const fileInput = document.getElementById('importFileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Por favor, selecione um arquivo JSON');
        return;
    }

    try {
        const text = await file.text();
        const data = JSON.parse(text);

        // Call import API
        const response = await fetch('/api/forecasts/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao importar análise');
        }

        const result = await response.json();

        // Clear file input
        fileInput.value = '';
        $('.custom-file-label').text('Escolher arquivo...');

        // Reload forecasts list
        loadForecasts();

        alert('Análise importada com sucesso!');

    } catch (error) {
        console.error('Error importing forecast:', error);
        alert('Erro ao importar análise: ' + error.message);
    }
}

// Update file input label when file is selected
$(document).on('change', '#importFileInput', function() {
    const fileName = $(this).val().split('\\').pop();
    $(this).next('.custom-file-label').text(fileName || 'Escolher arquivo...');
});

// Export functions to global scope
window.openSaveModal = openSaveModal;
window.openLoadModal = openLoadModal;
window.saveForecast = saveForecast;
window.loadForecasts = loadForecasts;
window.loadForecast = loadForecast;
window.deleteForecast = deleteForecast;
window.importForecastFromFile = importForecastFromFile;
