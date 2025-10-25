(function () {
    const STORAGE_KEY = 'ff:lastDependencies';
    const SNAPSHOT_KEY = 'ff:lastSimulation';

    function cloneTemplate() {
        const template = document.getElementById('dependency-row-template');
        const anchor = document.getElementById('add-dependency-row');
        if (!template || !anchor) return null;
        const clone = template.cloneNode(true);
        clone.removeAttribute('id');
        anchor.parentNode.insertBefore(clone, anchor);
        return clone;
    }

    function clearDynamicRows() {
        const rows = document.querySelectorAll('#dependencies tbody .dependency-row');
        rows.forEach(row => {
            if (row.id === 'dependency-row-template') {
                row.querySelectorAll('input').forEach(input => input.value = '');
                const select = row.querySelector('select[name="dependency_criticality"]');
                if (select) select.value = 'MEDIUM';
            } else {
                row.remove();
            }
        });
    }

    function collectDependencies() {
        const dependencies = [];
        const rows = document.querySelectorAll('#dependencies tbody .dependency-row');
        rows.forEach(row => {
            if (row.id === 'dependency-row-template') return;
            const name = row.querySelector("input[name='dependency_name']")?.value?.trim();
            const source = row.querySelector("input[name='dependency_source_project']")?.value?.trim();
            const target = row.querySelector("input[name='dependency_target_project']")?.value?.trim();
            const probability = parseFloat(row.querySelector("input[name='dep_probability']")?.value);
            const delay = parseFloat(row.querySelector("input[name='dep_delay']")?.value);
            const criticality = row.querySelector("select[name='dependency_criticality']")?.value || 'MEDIUM';

            if (name || source || target) {
                dependencies.push({
                    name: name || '',
                    source_project: source || '',
                    target_project: target || '',
                    on_time_probability: Number.isFinite(probability) ? probability / 100 : 0.5,
                    delay_impact_days: Number.isFinite(delay) ? delay : 0,
                    criticality
                });
            }
        });
        return dependencies;
    }

    function fillDependenciesTable(dependencies) {
        clearDynamicRows();
        if (!Array.isArray(dependencies) || !dependencies.length) return;
        dependencies.forEach(dep => {
            const row = cloneTemplate();
            if (!row) return;
            row.querySelector("input[name='dependency_name']").value = dep.name || '';
            row.querySelector("input[name='dependency_source_project']").value = dep.source_project || '';
            row.querySelector("input[name='dependency_target_project']").value = dep.target_project || '';
            row.querySelector("input[name='dep_probability']").value = dep.on_time_probability != null ? Math.round(dep.on_time_probability * 100) : 75;
            row.querySelector("input[name='dep_delay']").value = dep.delay_impact_days != null ? dep.delay_impact_days : 10;
            row.querySelector("select[name='dependency_criticality']").value = dep.criticality || 'MEDIUM';
        });
    }

    function persistDependencies(dependencies) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(dependencies || []));
        } catch (error) {
            console.warn('[Flow Forecaster] Não foi possível salvar dependências.', error);
        }
    }

    function readStoredDependencies() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed) ? parsed : [];
        } catch (error) {
            console.warn('[Flow Forecaster] Não foi possível carregar dependências salvas.', error);
            return [];
        }
    }

    function readSnapshot() {
        try {
            const raw = localStorage.getItem(SNAPSHOT_KEY);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (error) {
            console.warn('[Flow Forecaster] Não foi possível carregar snapshot da simulação.', error);
            return null;
        }
    }

    function renderDependencyInsights(snapshot) {
        const container = document.getElementById('dependencyTabResults');
        const empty = document.getElementById('dependencyTabEmpty');
        if (!container || !empty) return;

        const analysis = snapshot?.result?.dependency_analysis;
        if (!analysis) {
            container.style.display = 'none';
            empty.style.display = 'block';
            return;
        }

        container.style.display = 'block';
        empty.style.display = 'none';

        const formatPercent = (value) => {
            if (!Number.isFinite(value)) return '-';
            return `${(value * 100).toFixed(1)}%`;
        };
        const formatDelay = (value) => {
            if (!Number.isFinite(value)) return '-';
            return `${Math.round(value)} dias`;
        };

        document.getElementById('dep-tab-on-time-prob').textContent = formatPercent(analysis.on_time_probability ?? 0);
        document.getElementById('dep-tab-expected-delay').textContent = formatDelay(analysis.expected_delay ?? 0);
        document.getElementById('dep-tab-total').textContent = analysis.total_dependencies ?? 0;
        document.getElementById('dep-tab-risk-level').textContent = analysis.risk_level || '-';

        const scoreElement = document.getElementById('dep-tab-risk-score');
        if (scoreElement) {
            const score = analysis.risk_score;
            scoreElement.textContent = Number.isFinite(score) ? `Score: ${Math.round(score)}/100` : '-';
        }

        if (analysis.delay_percentiles) {
            const tbody = document.getElementById('dep-tab-delay-body');
            if (tbody) {
                tbody.innerHTML = Object.entries(analysis.delay_percentiles)
                    .map(([percentile, value]) => `<tr><td>${percentile.toUpperCase()}</td><td>${formatDelay(value)}</td></tr>`)
                    .join('');
            }
        }

        const vizContainer = document.getElementById('dep-tab-visualization-container');
        const vizImg = document.getElementById('dep-tab-visualization-image');
        if (vizContainer && vizImg) {
            if (analysis.visualization_image) {
                vizImg.src = `data:image/png;base64,${analysis.visualization_image}`;
                vizImg.classList.remove('d-none');
                vizContainer.querySelector('p')?.classList.add('d-none');
            } else {
                vizImg.src = '';
                vizImg.classList.add('d-none');
                vizContainer.querySelector('p')?.classList.remove('d-none');
            }
        }

        const criticalList = document.getElementById('dep-tab-critical-path');
        if (criticalList) {
            const items = (analysis.critical_path || []).map(item => `<li class="list-group-item">${item}</li>`);
            criticalList.innerHTML = items.length ? items.join('') : '<li class="list-group-item text-muted">Nenhum caminho crítico identificado.</li>';
        }

        const recommendationList = document.getElementById('dep-tab-recommendations');
        if (recommendationList) {
            const items = (analysis.recommendations || []).map(item => `<li class="list-group-item">${item}</li>`);
            recommendationList.innerHTML = items.length ? items.join('') : '<li class="list-group-item text-muted">Nenhuma recomendação disponível.</li>';
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const addButton = document.getElementById('dependencyAddButton');
        const saveButton = document.getElementById('saveDependencies');
        const loadButton = document.getElementById('loadDependencies');
        const loadSnapshotButton = document.getElementById('loadLastSimulation');

        if (addButton) {
            addButton.addEventListener('click', () => {
                const row = cloneTemplate();
                if (row) {
                    const firstInput = row.querySelector('input, select');
                    if (firstInput) firstInput.focus();
                }
            });
        }

        if (saveButton) {
            saveButton.addEventListener('click', () => {
                const deps = collectDependencies();
                persistDependencies(deps);
                const snapshot = readSnapshot();
                if (snapshot) {
                    snapshot.simulationData = snapshot.simulationData || {};
                    snapshot.simulationData.dependencies = deps;
                    try {
                        localStorage.setItem(SNAPSHOT_KEY, JSON.stringify(snapshot));
                    } catch (error) {
                        console.warn('[Flow Forecaster] Não foi possível atualizar snapshot.', error);
                    }
                }
                const toast = document.createElement('div');
                toast.className = 'alert alert-success';
                toast.textContent = 'Dependências salvas com sucesso (armazenadas localmente no navegador).';
                saveButton.closest('.card-modern').prepend(toast);
                setTimeout(() => toast.remove(), 3200);
            });
        }

        if (loadButton) {
            loadButton.addEventListener('click', () => {
                const stored = readStoredDependencies();
                fillDependenciesTable(stored);
            });
        }

        if (loadSnapshotButton) {
            loadSnapshotButton.addEventListener('click', () => {
                const snapshot = readSnapshot();
                if (!snapshot) return;
                const deps = snapshot.simulationData?.dependencies || [];
                fillDependenciesTable(deps);
                persistDependencies(deps);
                renderDependencyInsights(snapshot);
            });
        }

        // Restore stored dependencies on load
        const stored = readStoredDependencies();
        if (stored.length) {
            fillDependenciesTable(stored);
        }

        // Render insights based on last simulation
        const snapshot = readSnapshot();
        if (snapshot) {
            renderDependencyInsights(snapshot);
        }

        if (!document.querySelector('#dependencies tbody .dependency-row:not(#dependency-row-template)')) {
            cloneTemplate();
        }
    });
})();
