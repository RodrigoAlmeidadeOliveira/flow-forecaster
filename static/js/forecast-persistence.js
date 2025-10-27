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
        // Collect all current state
        const inputData = {
            tpSamples: collectThroughputSamples(),
            backlog: parseInt($('#backlog').val() || 0),
            teamSize: parseInt($('#team-size').val() || 1),
            workingDays: parseInt($('#working-days').val() || 5),
            startDate: $('#start-date').val(),
            endDate: $('#end-date').val(),
            deadlineDate: $('#deadlineDate').val(),
            risks: collectRisks(),
            dependencies: collectDependencies(),
            teamFocus: parseFloat($('#team-focus').val() || 1.0),
            sCurveA: parseFloat($('#s-curve-a').val() || 0),
            sCurveB: parseFloat($('#s-curve-b').val() || 0)
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
            $('#tp-samples-textarea').val(input.tpSamples.join('\n'));
        }

        // Restore basic fields
        $('#backlog').val(input.backlog || '');
        $('#team-size').val(input.teamSize || 1);
        $('#working-days').val(input.workingDays || 5);
        $('#start-date').val(input.startDate || '');
        $('#end-date').val(input.endDate || '');
        $('#deadlineDate').val(input.deadlineDate || '');
        $('#team-focus').val(input.teamFocus || 1.0);
        $('#s-curve-a').val(input.sCurveA || 0);
        $('#s-curve-b').val(input.sCurveB || 0);

        // Restore risks
        if (input.risks && Array.isArray(input.risks)) {
            // Clear existing risks
            $('#risk-list tbody').empty();
            // Add loaded risks
            input.risks.forEach(risk => {
                // This would need to call the addRisk function from ui.js
                // For now, we'll store it and let the user see it
            });
        }

        // Restore dependencies
        if (input.dependencies && Array.isArray(input.dependencies)) {
            $('#dependency-list tbody').empty();
            // Add loaded dependencies
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
    const text = $('#tp-samples-textarea').val();
    if (!text) return [];
    return text.split('\n')
        .map(line => parseFloat(line.trim()))
        .filter(n => !isNaN(n) && n > 0);
}

function collectRisks() {
    const risks = [];
    $('#risk-list tbody tr').each(function() {
        const row = $(this);
        risks.push({
            name: row.find('td:eq(0)').text(),
            probability: parseFloat(row.find('td:eq(1)').text()) / 100,
            impact: parseFloat(row.find('td:eq(2)').text())
        });
    });
    return risks;
}

function collectDependencies() {
    const dependencies = [];
    $('#dependency-list tbody tr').each(function() {
        const row = $(this);
        dependencies.push({
            name: row.find('td:eq(0)').text(),
            source_project: row.find('td:eq(1)').text(),
            target_project: row.find('td:eq(2)').text(),
            on_time_probability: parseFloat(row.find('td:eq(3)').text()) / 100,
            delay_impact_days: parseFloat(row.find('td:eq(4)').text())
        });
    });
    return dependencies;
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
