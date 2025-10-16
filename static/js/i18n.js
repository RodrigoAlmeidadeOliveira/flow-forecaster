// Sistema de Internacionalização para Flow Forecasting
(function() {
    'use strict';

    const translations = {
        pt: {
            // Nome do site e cabeçalho
            site_name: 'Flow Forecasting',
            site_tagline: 'Previsão de esforço e duração de projetos usando simulações Monte Carlo e aprendizado de máquina.',
            site_description: 'Seus dados permanecem locais no seu navegador/servidor.',

            // Menu
            menu_advanced: 'Previsão Avançada',
            menu_deadline: 'Análise de Prazo',

            // Abas principais
            tab_monte_carlo: 'Monte Carlo',
            tab_advanced: 'Avançado (ML + MC)',
            tab_deadline: 'Análise de Prazo',
            tab_historical: 'Gráficos Históricos',
            tab_cost: 'Análise de Custos',

            // Dados de throughput compartilhados
            shared_throughput_title: 'Dados de Throughput Compartilhados',
            throughput_placeholder: 'Exemplo: 5, 6, 7, 4, 8, 6, 5, 7, 6, 8',
            throughput_help: 'Forneça amostras de throughput semanais uma vez e reutilize-as em simulações Monte Carlo e Aprendizado de Máquina.',

            // Propriedades do projeto
            project_props: 'Propriedades do Projeto',
            project_name: 'Nome do projeto',
            team_size: 'Tamanho da equipe',
            contributors: 'contribuidores',
            min_contributors: 'Contribuidores mínimos',
            max_contributors: 'Contribuidores máximos',
            num_tasks: 'Número de tarefas',
            historical_team_size: 'Tamanho histórico da equipe',
            historical_team_size_tooltip: 'Tamanho da equipe quando os dados históricos de throughput foram coletados',

            // Propriedades da simulação
            simulation_props: 'Propriedades da Simulação',
            num_simulations: 'Número de simulações',
            scurve_size: 'Tamanho da Curva-S',
            confidence_level: 'Nível de confiança',
            start_date: 'Data de início',
            deadline: 'Prazo',

            // Dados históricos
            historical_data: 'Dados históricos',
            weekly_throughput_note: 'As amostras de throughput semanais são definidas na seção compartilhada acima.',
            task_lead_times: 'Tempos de lead de tarefas',
            project_split_rates: 'Taxas de divisão de projetos',
            lead_time_placeholder: 'Opcionalmente cole seus dados históricos de tempo de lead de tarefas',
            split_rate_placeholder: 'Opcionalmente cole seus dados históricos de taxas de divisão de projetos',

            // Riscos
            risks_title: 'Riscos (opcional)',
            risks_description: 'Modele riscos discretos para adicionar buffer probabilístico à sua previsão.',
            likelihood: 'Probabilidade',
            low_impact: 'Impacto baixo',
            medium_impact: 'Impacto médio',
            high_impact: 'Impacto alto',
            description: 'Descrição',
            tasks: 'tarefas',
            add_row: 'Adicionar linha',

            // Botões de ação
            run_simulation: 'Executar a simulação!',
            share: 'Compartilhar',
            run_combined_forecast: 'Executar Previsão Combinada',
            run_ml_only: 'Apenas Previsão ML',
            run_deadline_analysis: 'Executar Análise de Prazo',
            run_cost_analysis: 'Executar Análise de Custos',

            // Resultados
            results_title: 'Resultados da Simulação',
            forecast_summary: 'Resumo da previsão do projeto',
            with_confidence: 'com {{level}}% de confiança',
            effort: 'Esforço',
            duration: 'Duração',
            delivery_date: 'Data de entrega',
            person_weeks: 'pessoa-semanas',
            calendar_weeks: 'semanas corridas',

            // Probabilidades
            all_probabilities: 'Todas as probabilidades',
            comment: 'Comentário',
            date: 'Data',
            show_more: 'Mostrar mais...',
            almost_certain: 'Quase certo',
            somewhat_certain: 'Algo certo',
            less_than_coin_toss: 'Menos que cara ou coroa',

            // Gráficos
            charts: 'Gráficos',
            simulation_report: 'Relatório da simulação',
            input_statistics: 'Estatísticas de entrada',

            // Previsão avançada
            advanced_forecasting: 'Previsão Avançada',
            advanced_description: 'Combine previsões de aprendizado de máquina com simulações de throughput Monte Carlo para perspectivas mais ricas.',
            advanced_min_samples: 'Forneça pelo menos oito amostras de throughput para desbloquear projeções baseadas em ML.',
            historical_data_title: 'Dados Históricos',
            weekly_throughput: 'Throughput Semanal',
            uses_shared_throughput: 'Usa as amostras de throughput compartilhadas definidas acima.',
            edit_data: 'Editar dados',
            min_8_values: 'Mínimo de 8 valores necessários para previsão ML.',
            forecast_params: 'Parâmetros de Previsão',
            forecast_steps: 'Passos de Previsão (semanas)',
            backlog: 'Backlog (tarefas)',
            mc_simulations: 'Simulações Monte Carlo',

            // Análise de prazo
            deadline_analysis: 'Análise de Prazo',
            deadline_description: 'Reutilize suas entradas de simulação e riscos existentes para avaliar se o prazo pode ser alcançado.',
            ensure_dates: 'Certifique-se de que os campos Data de início e Prazo no formulário Monte Carlo estejam preenchidos.',
            how_it_works: 'Como funciona',
            how_it_works_desc: 'Executamos a simulação Monte Carlo completa com seus riscos e configurações de equipe, depois comparamos os percentis de conclusão projetados com o prazo selecionado. O previsor de Aprendizado de Máquina também é executado quando pelo menos oito amostras de throughput estão disponíveis.',
            running_simulations: 'Executando simulações de prazo...',

            // Gráficos históricos
            historical_charts_title: 'Gráficos Históricos de Throughput e Tempo de Lead',
            historical_charts_desc: 'Visualize a distribuição e estabilidade das amostras fornecidas. Atualize os campos acima para atualizar esses gráficos.',
            throughput_histogram: 'Histograma de Throughput',
            throughput_control: 'Gráfico de Controle de Throughput',
            lead_time_histogram: 'Histograma de Tempo de Lead',
            lead_time_control: 'Gráfico de Controle de Tempo de Lead',
            min_3_samples_histogram: 'Forneça pelo menos 3 amostras de throughput para gerar o histograma.',
            min_samples_control: 'Forneça amostras de throughput para visualizar o gráfico de controle.',
            min_3_samples_lt_histogram: 'Forneça pelo menos 3 amostras de tempo de lead para gerar o histograma.',
            min_samples_lt_control: 'Forneça amostras de tempo de lead para visualizar o gráfico de controle.',

            // Análise de custos
            cost_analysis_title: 'Análise de Custos com PERT-Beta',
            cost_analysis_desc: 'Simule custos do projeto usando distribuição PERT-Beta com estimativas otimista, mais provável e pessimista. A simulação Monte Carlo com 10.000+ iterações fornece projeções realistas de custo.',
            cost_per_item: 'Custo por Item',
            avg_cost_per_item: 'Custo Médio por Item',
            avg_cost_help: 'Custo médio histórico por item de trabalho',
            pert_estimates: 'Estimativas PERT',
            optimistic_cost: 'Custo Otimista (a)',
            best_scenario: 'Melhor cenário',
            most_likely_cost: 'Custo Mais Provável (m)',
            realistic_scenario: 'Cenário mais realista',
            pessimistic_cost: 'Custo Pessimista (b)',
            worst_scenario: 'Pior cenário',
            num_sims: 'Número de Simulações',
            min_simulations: 'Mínimo: 10.000 simulações',
            uses_backlog: 'Usa o backlog definido na aba Monte Carlo',
            running_cost_sims: 'Executando simulações de custo...',

            // Cost analysis results
            cost_results_title: 'Resultados da Simulação',
            cost_statistics: 'Estatísticas de Custo',
            scenarios: 'Cenários',
            cost_distribution: 'Distribuição de Custos',
            cost_percentiles: 'Percentis de Custo',
            percentile: 'Percentil',
            cost_currency: 'Custo (R$)',
            probability: 'Probabilidade',
            pert_beta_params: 'Parâmetros PERT-Beta',

            // Rodapé e outros
            mandatory_fields: 'Campos marcados com um',
            are_mandatory: 'são obrigatórios',
            loading: 'Carregando...',
            running_forecast: 'Executando previsão... Isso pode levar alguns segundos.',

            // Mensagens de erro/sucesso
            error: 'Erro',
            success: 'Sucesso',
            link_copied: 'Link copiado para a área de transferência!',
            error_encoding: 'Erro ao codificar dados para compartilhamento',
            error_running_simulation: 'Erro ao executar simulação',
            unknown_error: 'Erro desconhecido',
            must_have_throughput: 'Deve ter pelo menos uma amostra de throughput semanal maior que zero',
            split_rates_incorrect: 'Suas taxas de divisão não parecem corretas.\nPara uma taxa de divisão de 10%, coloque "1.1"',
            provide_start_date: 'Por favor, defina uma data de início do projeto antes de executar a análise de prazo.',
            provide_deadline: 'Por favor, forneça uma data de prazo antes de executar a análise de prazo.',

            // Deadline Analysis - extra
            deadline_reuse_desc: 'Reutilize suas entradas de simulação e riscos existentes para avaliar se o prazo pode ser alcançado. Certifique-se de que os campos Data de início e Prazo no formulário Monte Carlo estejam preenchidos.',
            how_works_desc: 'executamos a simulação Monte Carlo completa com seus riscos e configurações de equipe, depois comparamos os percentis de conclusão projetados com o prazo selecionado. O previsor de Aprendizado de Máquina também é executado quando pelo menos oito amostras de throughput estão disponíveis.',
            just_in_time: 'Just in time',

            // Historical team size
            historical_team_size_label: 'Tamanho histórico da equipe',

            // Advanced Forecast - extra
            weekly_throughput_label: 'Throughput Semanal',
            uses_shared_samples: 'Usa as amostras de throughput compartilhadas definidas acima.',
            edit_data_link: 'Editar dados',
            min_8_ml: 'Mínimo de 8 valores necessários para previsão ML.',
            start_date_label: 'Data de Início',
            forecast_steps_label: 'Passos de Previsão (semanas)',
            backlog_tasks_label: 'Backlog (tarefas)',
            mc_simulations_label: 'Simulações Monte Carlo',
            run_combined: 'Executar Previsão Combinada',
            ml_only: 'Apenas Previsão ML',

            // ML Results
            ml_forecast_title: 'Previsão de Aprendizado de Máquina',
            risk_assessment_title: 'Avaliação de Risco',
            model_performance_title: 'Desempenho do Modelo',
            ml_ensemble_forecast: 'Previsão de Ensemble ML',
            historical_data_analysis: 'Análise de Dados Históricos',
            monte_carlo_simulation: 'Simulação Monte Carlo',
            completion_time_stats: 'Estatísticas de Tempo de Conclusão',
            monte_carlo_simulations: 'Simulações Monte Carlo',
            forecast_comparison: 'Comparação de Previsão',
            ml_vs_mc: 'ML vs Monte Carlo Comparação',
            ml_forecast_summary: 'Resumo de Previsão ML',
            mc_summary: 'Resumo Monte Carlo',
            walk_forward_validation: 'Validação Walk-forward',

            // Historical Charts - extra
            historical_throughput_lead: 'Gráficos Históricos de Throughput e Tempo de Lead',
            visualize_distribution: 'Visualize a distribuição e estabilidade das amostras fornecidas. Atualize os campos acima para atualizar esses gráficos.',
            throughput_histogram_title: 'Histograma de Throughput',
            throughput_control_title: 'Gráfico de Controle de Throughput',
            lead_time_histogram_title: 'Histograma de Tempo de Lead',
            lead_time_control_title: 'Gráfico de Controle de Tempo de Lead',

            // Additional fields
            task_lead_times: 'Tempos de lead de tarefas',
            projects_split_rates: 'Taxas de divisão de projetos',
            risks_optional: 'Riscos (opcional)',
            risks_description: 'Modele riscos discretos para adicionar buffer probabilístico à sua previsão.',
            add_row: 'Adicionar linha',
            fields_mandatory: 'Campos marcados com um',
            are_mandatory: 'vermelho são obrigatórios',

            // Results section
            all_probabilities: 'Todas as probabilidades',
            charts: 'Gráficos',
            simulation_report: 'Relatório da simulação',
            input_stats: 'Estatísticas de entrada',
            running_forecast: 'Executando previsão... Isso pode levar alguns segundos.',

            // ML Results section titles
            ml_forecast: 'Previsão de Aprendizado de Máquina',
            risk_assessment: 'Avaliação de Risco',
            model_performance: 'Desempenho do Modelo',
            ml_ensemble: 'Previsão de Ensemble ML',
            historical_analysis: 'Análise de Dados Históricos',
            mc_simulation: 'Simulação Monte Carlo',
            completion_stats: 'Estatísticas de Tempo de Conclusão',
            forecast_compare: 'Comparação de Previsão',
            ml_vs_mc_comparison: 'Comparação ML vs Monte Carlo',
            walk_forward: 'Validação Walk-forward',
        },

        en: {
            // Site name and header
            site_name: 'Flow Forecasting',
            site_tagline: 'Forecast project effort and duration using Monte Carlo simulations and machine learning.',
            site_description: 'Your data remains local to your browser/server.',

            // Menu
            menu_advanced: 'Advanced Forecast',
            menu_deadline: 'Deadline Analysis',

            // Main tabs
            tab_monte_carlo: 'Monte Carlo',
            tab_advanced: 'Advanced (ML + MC)',
            tab_deadline: 'Deadline Analysis',
            tab_historical: 'Historical Charts',
            tab_cost: 'Cost Analysis',

            // Shared throughput data
            shared_throughput_title: 'Shared Throughput Data',
            throughput_placeholder: 'Example: 5, 6, 7, 4, 8, 6, 5, 7, 6, 8',
            throughput_help: 'Provide weekly throughput samples once and reuse them across Monte Carlo and Machine Learning simulations.',

            // Project properties
            project_props: 'Project Properties',
            project_name: 'Project name',
            team_size: 'Team size',
            contributors: 'contributors',
            min_contributors: 'Minimum contributors',
            max_contributors: 'Maximum contributors',
            num_tasks: 'Number of tasks',
            historical_team_size: 'Historical team size',
            historical_team_size_tooltip: 'Team size when historical throughput data was collected',

            // Simulation properties
            simulation_props: 'Simulation Properties',
            num_simulations: 'Number of simulations',
            scurve_size: 'S-Curve size',
            confidence_level: 'Confidence level',
            start_date: 'Start date',
            deadline: 'Deadline',

            // Historical data
            historical_data: 'Historical data',
            weekly_throughput_note: 'Weekly throughput samples are defined in the shared section above.',
            task_lead_times: 'Task lead-times',
            project_split_rates: 'Projects split rates',
            lead_time_placeholder: 'Optionally paste your historical data of tasks lead-time',
            split_rate_placeholder: 'Optionally paste your historical data of project\'s split rates',

            // Risks
            risks_title: 'Risks (optional)',
            risks_description: 'Model discrete risks to add probabilistic buffer to your forecast.',
            likelihood: 'Likelihood',
            low_impact: 'Low impact',
            medium_impact: 'Medium impact',
            high_impact: 'High impact',
            description: 'Description',
            tasks: 'tasks',
            add_row: 'Add row',

            // Action buttons
            run_simulation: 'Run the simulation!',
            share: 'Share',
            run_combined_forecast: 'Run Combined Forecast',
            run_ml_only: 'ML Forecast Only',
            run_deadline_analysis: 'Run Deadline Analysis',
            run_cost_analysis: 'Run Cost Analysis',

            // Results
            results_title: 'Simulation Results',
            forecast_summary: 'Project forecast summary',
            with_confidence: 'with {{level}}% confidence',
            effort: 'Effort',
            duration: 'Duration',
            delivery_date: 'Delivery date',
            person_weeks: 'person-weeks',
            calendar_weeks: 'calendar weeks',

            // Probabilities
            all_probabilities: 'All probabilities',
            comment: 'Comment',
            date: 'Date',
            show_more: 'Show more...',
            almost_certain: 'Almost certain',
            somewhat_certain: 'Somewhat certain',
            less_than_coin_toss: 'Less than coin-toss odds',

            // Charts
            charts: 'Charts',
            simulation_report: 'Simulation report',
            input_statistics: 'Input statistics',

            // Advanced forecast
            advanced_forecasting: 'Advanced Forecasting',
            advanced_description: 'Combine machine learning forecasts with Monte Carlo throughput simulations for richer outlooks.',
            advanced_min_samples: 'Provide at least eight throughput samples to unlock ML-based projections.',
            historical_data_title: 'Historical Data',
            weekly_throughput: 'Weekly Throughput',
            uses_shared_throughput: 'Uses the shared throughput samples defined above.',
            edit_data: 'Edit data',
            min_8_values: 'Minimum of 8 values required for ML forecasting.',
            forecast_params: 'Forecast Parameters',
            forecast_steps: 'Forecast Steps (weeks)',
            backlog: 'Backlog (tasks)',
            mc_simulations: 'Monte Carlo Simulations',

            // Deadline analysis
            deadline_analysis: 'Deadline Analysis',
            deadline_description: 'Reuse your existing simulation inputs and risks to evaluate whether the deadline can be achieved.',
            ensure_dates: 'Ensure the Start date and Deadline fields in the Monte Carlo form are filled.',
            how_it_works: 'How it works',
            how_it_works_desc: 'We run the full Monte Carlo simulation with your risks and team settings, then compare the projected completion percentiles against the selected deadline. The Machine Learning forecaster is executed as well when at least eight throughput samples are available.',
            running_simulations: 'Running deadline simulations...',

            // Historical charts
            historical_charts_title: 'Historical Throughput & Lead Time Charts',
            historical_charts_desc: 'Visualize the distribution and stability of the samples you provided. Update the fields above to refresh these charts.',
            throughput_histogram: 'Throughput Histogram',
            throughput_control: 'Throughput Control Chart',
            lead_time_histogram: 'Lead Time Histogram',
            lead_time_control: 'Lead Time Control Chart',
            min_3_samples_histogram: 'Provide at least 3 throughput samples to generate the histogram.',
            min_samples_control: 'Provide throughput samples to view the control chart.',
            min_3_samples_lt_histogram: 'Provide at least 3 lead time samples to generate the histogram.',
            min_samples_lt_control: 'Provide lead time samples to view the control chart.',

            // Cost analysis
            cost_analysis_title: 'Cost Analysis with PERT-Beta',
            cost_analysis_desc: 'Simulate project costs using PERT-Beta distribution with optimistic, most likely, and pessimistic estimates. The Monte Carlo simulation with 10,000+ iterations provides realistic cost projections.',
            cost_per_item: 'Cost per Item',
            avg_cost_per_item: 'Average Cost per Item',
            avg_cost_help: 'Historical average cost per work item',
            pert_estimates: 'PERT Estimates',
            optimistic_cost: 'Optimistic Cost (a)',
            best_scenario: 'Best scenario',
            most_likely_cost: 'Most Likely Cost (m)',
            realistic_scenario: 'Most realistic scenario',
            pessimistic_cost: 'Pessimistic Cost (b)',
            worst_scenario: 'Worst scenario',
            num_sims: 'Number of Simulations',
            min_simulations: 'Minimum: 10,000 simulations',
            uses_backlog: 'Uses the backlog defined in the Monte Carlo tab',
            running_cost_sims: 'Running cost simulations...',

            // Cost analysis results
            cost_results_title: 'Simulation Results',
            cost_statistics: 'Cost Statistics',
            scenarios: 'Scenarios',
            cost_distribution: 'Cost Distribution',
            cost_percentiles: 'Cost Percentiles',
            percentile: 'Percentile',
            cost_currency: 'Cost (R$)',
            probability: 'Probability',
            pert_beta_params: 'PERT-Beta Parameters',

            // Footer and others
            mandatory_fields: 'Fields marked with a red',
            are_mandatory: 'are mandatory',
            loading: 'Loading...',
            running_forecast: 'Running forecast... This may take a few seconds.',

            // Error/success messages
            error: 'Error',
            success: 'Success',
            link_copied: 'Link copied to clipboard!',
            error_encoding: 'Error encoding data for sharing',
            error_running_simulation: 'Error running simulation',
            unknown_error: 'Unknown error',
            must_have_throughput: 'Must have at least one weekly throughput sample greater than zero',
            split_rates_incorrect: 'Your split rates don\'t seem correct.\nFor a 10% split rate, put "1.1"',
            provide_start_date: 'Please set a project start date before running the deadline analysis.',
            provide_deadline: 'Please provide a deadline date before running the deadline analysis.',

            // Deadline Analysis - extra
            deadline_reuse_desc: 'Reuse your existing simulation inputs and risks to evaluate whether the deadline can be achieved. Ensure the Start date and Deadline fields in the Monte Carlo form are filled.',
            how_works_desc: 'we run the full Monte Carlo simulation with your risks and team settings, then compare the projected completion percentiles against the selected deadline. The Machine Learning forecaster is executed as well when at least eight throughput samples are available.',
            just_in_time: 'Just in time',

            // Historical team size
            historical_team_size_label: 'Historical team size',

            // Advanced Forecast - extra
            weekly_throughput_label: 'Weekly Throughput',
            uses_shared_samples: 'Uses the shared throughput samples defined above.',
            edit_data_link: 'Edit data',
            min_8_ml: 'Minimum of 8 values required for ML forecasting.',
            start_date_label: 'Start Date',
            forecast_steps_label: 'Forecast Steps (weeks)',
            backlog_tasks_label: 'Backlog (tasks)',
            mc_simulations_label: 'Monte Carlo Simulations',
            run_combined: 'Run Combined Forecast',
            ml_only: 'ML Forecast Only',

            // ML Results
            ml_forecast_title: 'Machine Learning Forecast',
            risk_assessment_title: 'Risk Assessment',
            model_performance_title: 'Model Performance',
            ml_ensemble_forecast: 'ML Ensemble Forecast',
            historical_data_analysis: 'Historical Data Analysis',
            monte_carlo_simulation: 'Monte Carlo Simulation',
            completion_time_stats: 'Completion Time Statistics',
            monte_carlo_simulations: 'Monte Carlo Simulations',
            forecast_comparison: 'Forecast Comparison',
            ml_vs_mc: 'ML vs Monte Carlo Comparison',
            ml_forecast_summary: 'ML Forecast Summary',
            mc_summary: 'Monte Carlo Summary',
            walk_forward_validation: 'Walk-forward Validation',

            // Historical Charts - extra
            historical_throughput_lead: 'Historical Throughput & Lead Time Charts',
            visualize_distribution: 'Visualize the distribution and stability of the samples you provided. Update the fields above to refresh these charts.',
            throughput_histogram_title: 'Throughput Histogram',
            throughput_control_title: 'Throughput Control Chart',
            lead_time_histogram_title: 'Lead Time Histogram',
            lead_time_control_title: 'Lead Time Control Chart',

            // Additional fields
            task_lead_times: 'Task lead-times',
            projects_split_rates: 'Projects split rates',
            risks_optional: 'Risks (optional)',
            risks_description: 'Model discrete risks to add probabilistic buffer to your forecast.',
            add_row: 'Add row',
            fields_mandatory: 'Fields marked with a',
            are_mandatory: 'are mandatory',

            // Results section
            all_probabilities: 'All probabilities',
            charts: 'Charts',
            simulation_report: 'Simulation report',
            input_stats: 'Input statistics',
            running_forecast: 'Running forecast... This may take a few seconds.',

            // ML Results section titles
            ml_forecast: 'Machine Learning Forecast',
            risk_assessment: 'Risk Assessment',
            model_performance: 'Model Performance',
        },

        es: {
            // Nombre del sitio y encabezado
            site_name: 'Flow Forecasting',
            site_tagline: 'Pronóstico del esfuerzo y duración del proyecto usando simulaciones Monte Carlo y aprendizaje automático.',
            site_description: 'Sus datos permanecen locales en su navegador/servidor.',

            // Menú
            menu_advanced: 'Pronóstico Avanzado',
            menu_deadline: 'Análisis de Plazo',

            // Pestañas principales
            tab_monte_carlo: 'Monte Carlo',
            tab_advanced: 'Avanzado (ML + MC)',
            tab_deadline: 'Análisis de Plazo',
            tab_historical: 'Gráficos Históricos',
            tab_cost: 'Análisis de Costos',

            // Datos de rendimiento compartidos
            shared_throughput_title: 'Datos de Rendimiento Compartidos',
            throughput_placeholder: 'Ejemplo: 5, 6, 7, 4, 8, 6, 5, 7, 6, 8',
            throughput_help: 'Proporcione muestras de rendimiento semanales una vez y reutilícelas en simulaciones de Monte Carlo y Aprendizaje Automático.',

            // Propiedades del proyecto
            project_props: 'Propiedades del Proyecto',
            project_name: 'Nombre del proyecto',
            team_size: 'Tamaño del equipo',
            contributors: 'colaboradores',
            min_contributors: 'Colaboradores mínimos',
            max_contributors: 'Colaboradores máximos',
            num_tasks: 'Número de tareas',
            historical_team_size: 'Tamaño histórico del equipo',
            historical_team_size_tooltip: 'Tamaño del equipo cuando se recopilaron los datos históricos de rendimiento',

            // Propiedades de la simulación
            simulation_props: 'Propiedades de la Simulación',
            num_simulations: 'Número de simulaciones',
            scurve_size: 'Tamaño de la Curva S',
            confidence_level: 'Nivel de confianza',
            start_date: 'Fecha de inicio',
            deadline: 'Plazo',

            // Datos históricos
            historical_data: 'Datos históricos',
            weekly_throughput_note: 'Las muestras de rendimiento semanales se definen en la sección compartida arriba.',
            task_lead_times: 'Tiempos de entrega de tareas',
            project_split_rates: 'Tasas de división de proyectos',
            lead_time_placeholder: 'Opcionalmente pegue sus datos históricos de tiempo de entrega de tareas',
            split_rate_placeholder: 'Opcionalmente pegue sus datos históricos de tasas de división de proyectos',

            // Riesgos
            risks_title: 'Riesgos (opcional)',
            risks_description: 'Modele riesgos discretos para agregar un búfer probabilístico a su pronóstico.',
            likelihood: 'Probabilidad',
            low_impact: 'Impacto bajo',
            medium_impact: 'Impacto medio',
            high_impact: 'Impacto alto',
            description: 'Descripción',
            tasks: 'tareas',
            add_row: 'Agregar fila',

            // Botones de acción
            run_simulation: '¡Ejecutar la simulación!',
            share: 'Compartir',
            run_combined_forecast: 'Ejecutar Pronóstico Combinado',
            run_ml_only: 'Solo Pronóstico ML',
            run_deadline_analysis: 'Ejecutar Análisis de Plazo',
            run_cost_analysis: 'Ejecutar Análisis de Costos',

            // Resultados
            results_title: 'Resultados de la Simulación',
            forecast_summary: 'Resumen del pronóstico del proyecto',
            with_confidence: 'con {{level}}% de confianza',
            effort: 'Esfuerzo',
            duration: 'Duración',
            delivery_date: 'Fecha de entrega',
            person_weeks: 'persona-semanas',
            calendar_weeks: 'semanas calendario',

            // Probabilidades
            all_probabilities: 'Todas las probabilidades',
            comment: 'Comentario',
            date: 'Fecha',
            show_more: 'Mostrar más...',
            almost_certain: 'Casi seguro',
            somewhat_certain: 'Algo seguro',
            less_than_coin_toss: 'Menos que cara o cruz',

            // Gráficos
            charts: 'Gráficos',
            simulation_report: 'Informe de simulación',
            input_statistics: 'Estadísticas de entrada',

            // Pronóstico avanzado
            advanced_forecasting: 'Pronóstico Avanzado',
            advanced_description: 'Combine pronósticos de aprendizaje automático con simulaciones de rendimiento Monte Carlo para perspectivas más ricas.',
            advanced_min_samples: 'Proporcione al menos ocho muestras de rendimiento para desbloquear proyecciones basadas en ML.',
            historical_data_title: 'Datos Históricos',
            weekly_throughput: 'Rendimiento Semanal',
            uses_shared_throughput: 'Utiliza las muestras de rendimiento compartidas definidas arriba.',
            edit_data: 'Editar datos',
            min_8_values: 'Mínimo de 8 valores requeridos para pronóstico ML.',
            forecast_params: 'Parámetros de Pronóstico',
            forecast_steps: 'Pasos de Pronóstico (semanas)',
            backlog: 'Trabajo pendiente (tareas)',
            mc_simulations: 'Simulaciones Monte Carlo',

            // Análisis de plazo
            deadline_analysis: 'Análisis de Plazo',
            deadline_description: 'Reutilice sus entradas de simulación y riesgos existentes para evaluar si se puede cumplir el plazo.',
            ensure_dates: 'Asegúrese de que los campos Fecha de inicio y Plazo en el formulario de Monte Carlo estén completados.',
            how_it_works: 'Cómo funciona',
            how_it_works_desc: 'Ejecutamos la simulación completa de Monte Carlo con sus riesgos y configuraciones de equipo, luego comparamos los percentiles de finalización proyectados con el plazo seleccionado. El pronosticador de Aprendizaje Automático también se ejecuta cuando hay al menos ocho muestras de rendimiento disponibles.',
            running_simulations: 'Ejecutando simulaciones de plazo...',

            // Gráficos históricos
            historical_charts_title: 'Gráficos Históricos de Rendimiento y Tiempo de Entrega',
            historical_charts_desc: 'Visualice la distribución y estabilidad de las muestras proporcionadas. Actualice los campos arriba para actualizar estos gráficos.',
            throughput_histogram: 'Histograma de Rendimiento',
            throughput_control: 'Gráfico de Control de Rendimiento',
            lead_time_histogram: 'Histograma de Tiempo de Entrega',
            lead_time_control: 'Gráfico de Control de Tiempo de Entrega',
            min_3_samples_histogram: 'Proporcione al menos 3 muestras de rendimiento para generar el histograma.',
            min_samples_control: 'Proporcione muestras de rendimiento para ver el gráfico de control.',
            min_3_samples_lt_histogram: 'Proporcione al menos 3 muestras de tiempo de entrega para generar el histograma.',
            min_samples_lt_control: 'Proporcione muestras de tiempo de entrega para ver el gráfico de control.',

            // Análisis de costos
            cost_analysis_title: 'Análisis de Costos con PERT-Beta',
            cost_analysis_desc: 'Simule los costos del proyecto usando la distribución PERT-Beta con estimaciones optimistas, más probables y pesimistas. La simulación Monte Carlo con más de 10,000 iteraciones proporciona proyecciones de costos realistas.',
            cost_per_item: 'Costo por Artículo',
            avg_cost_per_item: 'Costo Promedio por Artículo',
            avg_cost_help: 'Costo promedio histórico por elemento de trabajo',
            pert_estimates: 'Estimaciones PERT',
            optimistic_cost: 'Costo Optimista (a)',
            best_scenario: 'Mejor escenario',
            most_likely_cost: 'Costo Más Probable (m)',
            realistic_scenario: 'Escenario más realista',
            pessimistic_cost: 'Costo Pesimista (b)',
            worst_scenario: 'Peor escenario',
            num_sims: 'Número de Simulaciones',
            min_simulations: 'Mínimo: 10,000 simulaciones',
            uses_backlog: 'Utiliza el backlog definido en la pestaña Monte Carlo',
            running_cost_sims: 'Ejecutando simulaciones de costos...',

            // Cost analysis results
            cost_results_title: 'Resultados de la Simulación',
            cost_statistics: 'Estadísticas de Costo',
            scenarios: 'Escenarios',
            cost_distribution: 'Distribución de Costos',
            cost_percentiles: 'Percentiles de Costo',
            percentile: 'Percentil',
            cost_currency: 'Costo (R$)',
            probability: 'Probabilidad',
            pert_beta_params: 'Parámetros PERT-Beta',

            // Pie de página y otros
            mandatory_fields: 'Los campos marcados con un',
            are_mandatory: 'son obligatorios',
            loading: 'Cargando...',
            running_forecast: 'Ejecutando pronóstico... Esto puede tomar unos segundos.',

            // Mensajes de error/éxito
            error: 'Error',
            success: 'Éxito',
            link_copied: '¡Enlace copiado al portapapeles!',
            error_encoding: 'Error al codificar datos para compartir',
            error_running_simulation: 'Error al ejecutar la simulación',
            unknown_error: 'Error desconocido',
            must_have_throughput: 'Debe tener al menos una muestra de rendimiento semanal mayor que cero',
            split_rates_incorrect: 'Sus tasas de división no parecen correctas.\nPara una tasa de división del 10%, ponga "1.1"',
            provide_start_date: 'Por favor, establezca una fecha de inicio del proyecto antes de ejecutar el análisis de plazo.',
            provide_deadline: 'Por favor, proporcione una fecha de plazo antes de ejecutar el análisis de plazo.',

            // Deadline Analysis - extra
            deadline_reuse_desc: 'Reutilice sus entradas de simulación y riesgos existentes para evaluar si se puede cumplir el plazo. Asegúrese de que los campos Fecha de inicio y Plazo en el formulario de Monte Carlo estén completados.',
            how_works_desc: 'ejecutamos la simulación completa de Monte Carlo con sus riesgos y configuraciones de equipo, luego comparamos los percentiles de finalización proyectados con el plazo seleccionado. El pronosticador de Aprendizaje Automático también se ejecuta cuando hay al menos ocho muestras de rendimiento disponibles.',
            just_in_time: 'Justo a tiempo',

            // Historical team size
            historical_team_size_label: 'Tamaño histórico del equipo',

            // Advanced Forecast - extra
            weekly_throughput_label: 'Rendimiento Semanal',
            uses_shared_samples: 'Utiliza las muestras de rendimiento compartidas definidas arriba.',
            edit_data_link: 'Editar datos',
            min_8_ml: 'Mínimo de 8 valores requeridos para pronóstico ML.',
            start_date_label: 'Fecha de Inicio',
            forecast_steps_label: 'Pasos de Pronóstico (semanas)',
            backlog_tasks_label: 'Trabajo pendiente (tareas)',
            mc_simulations_label: 'Simulaciones Monte Carlo',
            run_combined: 'Ejecutar Pronóstico Combinado',
            ml_only: 'Solo Pronóstico ML',

            // ML Results
            ml_forecast_title: 'Pronóstico de Aprendizaje Automático',
            risk_assessment_title: 'Evaluación de Riesgo',
            model_performance_title: 'Rendimiento del Modelo',
            ml_ensemble_forecast: 'Pronóstico de Ensemble ML',
            historical_data_analysis: 'Análisis de Datos Históricos',
            monte_carlo_simulation: 'Simulación Monte Carlo',
            completion_time_stats: 'Estadísticas de Tiempo de Finalización',
            monte_carlo_simulations: 'Simulaciones Monte Carlo',
            forecast_comparison: 'Comparación de Pronóstico',
            ml_vs_mc: 'Comparación ML vs Monte Carlo',
            ml_forecast_summary: 'Resumen de Pronóstico ML',
            mc_summary: 'Resumen Monte Carlo',
            walk_forward_validation: 'Validación Walk-forward',

            // Historical Charts - extra
            historical_throughput_lead: 'Gráficos Históricos de Rendimiento y Tiempo de Entrega',
            visualize_distribution: 'Visualice la distribución y estabilidad de las muestras proporcionadas. Actualice los campos arriba para actualizar estos gráficos.',
            throughput_histogram_title: 'Histograma de Rendimiento',
            throughput_control_title: 'Gráfico de Control de Rendimiento',
            lead_time_histogram_title: 'Histograma de Tiempo de Entrega',
            lead_time_control_title: 'Gráfico de Control de Tiempo de Entrega',

            // Additional fields
            task_lead_times: 'Tiempos de entrega de tareas',
            projects_split_rates: 'Tasas de división de proyectos',
            risks_optional: 'Riesgos (opcional)',
            risks_description: 'Modele riesgos discretos para agregar un búfer probabilístico a su pronóstico.',
            add_row: 'Agregar fila',
            fields_mandatory: 'Los campos marcados con un',
            are_mandatory: 'son obligatorios',

            // Results section
            all_probabilities: 'Todas las probabilidades',
            charts: 'Gráficos',
            simulation_report: 'Informe de simulación',
            input_stats: 'Estadísticas de entrada',
            running_forecast: 'Ejecutando pronóstico... Esto puede tomar unos segundos.',

            // ML Results section titles
            ml_forecast: 'Pronóstico de Aprendizaje Automático',
            risk_assessment: 'Evaluación de Riesgo',
            model_performance: 'Rendimiento del Modelo',
        }
    };

    // Estado atual do idioma
    let currentLanguage = localStorage.getItem('flowForecastingLang') || 'pt';

    // Função para obter tradução
    window.i18n = function(key, params) {
        let translation = translations[currentLanguage][key] || translations['en'][key] || key;

        // Substituir parâmetros
        if (params) {
            Object.keys(params).forEach(param => {
                translation = translation.replace(new RegExp('{{' + param + '}}', 'g'), params[param]);
            });
        }

        return translation;
    };

    // Função para mudar idioma
    window.changeLanguage = function(lang) {
        if (!translations[lang]) {
            console.error('Language not supported:', lang);
            return;
        }

        currentLanguage = lang;
        localStorage.setItem('flowForecastingLang', lang);

        // Atualizar todos os elementos com data-i18n
        updatePageLanguage();

        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    };

    // Função para obter idioma atual
    window.getCurrentLanguage = function() {
        return currentLanguage;
    };

    // Função para atualizar idioma da página
    function updatePageLanguage() {
        // Atualizar elementos com data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (!key) return;

            const translated = i18n(key);
            const hintIcon = element.querySelector('.doc-hint-icon');

            if (hintIcon) {
                const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                if (textNode) {
                    textNode.textContent = translated;
                } else {
                    element.insertBefore(document.createTextNode(translated), hintIcon);
                }
            } else {
                element.textContent = translated;
            }
        });

        // Atualizar placeholders com data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = i18n(key);
        });

        // Atualizar títulos com data-i18n-title
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = i18n(key);
        });

        // Atualizar HTML do documento
        document.documentElement.lang = currentLanguage;

        // Atualizar botões de idioma
        updateLanguageButtons();
    }

    // Função para atualizar estado visual dos botões de idioma
    function updateLanguageButtons() {
        document.querySelectorAll('.language-btn').forEach(btn => {
            const btnLang = btn.getAttribute('data-lang');
            if (btnLang === currentLanguage) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updatePageLanguage);
    } else {
        updatePageLanguage();
    }
})();
