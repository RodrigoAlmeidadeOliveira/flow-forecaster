/**
 * Forecast Persistence Module
 * Handles saving and loading forecasts to/from database
 */

// Open save modal
function openSaveModal() {
    $('#saveForecastModal').modal('show');
}

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

    try {
        const simulationData = window.lastSimulationData || {};
        const throughputSamples = (simulationData.tpSamples && simulationData.tpSamples.length)
            ? simulationData.tpSamples
            : collectThroughputSamples();
        const backlogValue = Number.isFinite(simulationData.numberOfTasks)
            ? simulationData.numberOfTasks
            : getCurrentBacklog();

        // Collect all current state
        const inputData = {
            tpSamples: throughputSamples,
            backlog: backlogValue,
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
        const payload = {
            name: name,
            description: $('#forecastDescription').val() || '',
            project_name: $('#projectName').val() || 'Default Project',
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

        // Save to API
        const response = await fetch('/api/forecasts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao salvar análise');
        }

        const result = await response.json();

        // Clear form and close modal
        $('#saveForecastForm')[0].reset();
        $('#saveForecastModal').modal('hide');

        alert('Análise salva com sucesso!');

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

        const response = await fetch('/api/forecasts');
        if (!response.ok) {
            throw new Error('Erro ao carregar análises');
        }

        const forecasts = await response.json();

        $('#loadingForecasts').hide();

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
        $('#forecastsList').html('<p class="text-danger">Erro ao carregar análises.</p>');
    }
}

// Load a specific forecast
async function loadForecast(id) {
    try {
        const response = await fetch(`/api/forecasts/${id}`);
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
            method: 'DELETE'
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
window.loadForecast = loadForecast;
window.deleteForecast = deleteForecast;
window.importForecastFromFile = importForecastFromFile;
