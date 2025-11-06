/**
 * Async Simulator - Client for Background Task Processing
 * Handles submission and polling of long-running simulations via Celery
 */

(function(global) {
    'use strict';

    class AsyncSimulator {
        constructor() {
            this.pollInterval = 1000; // Poll every 1 second
            this.activeTasks = new Map(); // Map of task_id -> polling timer
            this.maxRetries = 3;
            this.retryDelay = 2000;
        }

        /**
         * Submit a simulation to run asynchronously
         * @param {string} endpoint - API endpoint (e.g., '/api/async/simulate')
         * @param {Object} data - Simulation data
         * @param {Object} callbacks - Object with onProgress, onComplete, onError callbacks
         * @param {boolean} save - Whether to save forecast to database
         * @returns {Promise<string>} - Task ID
         */
        async submitSimulation(endpoint, data, callbacks, save = false) {
            const { onProgress, onComplete, onError } = callbacks || {};

            try {
                // Show initial progress
                if (onProgress) {
                    onProgress({
                        progress: 0,
                        total: 100,
                        stage: 'Submitting...',
                        status: 'Preparing simulation request'
                    });
                }

                // Add save parameter to URL if needed
                const url = save ? `${endpoint}?save=true` : endpoint;

                // Submit to backend
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }

                const result = await response.json();
                const taskId = result.task_id;

                console.log(`[AsyncSimulator] Task submitted: ${taskId}`);

                // Start polling for status
                this.pollTask(taskId, onProgress, onComplete, onError);

                return taskId;

            } catch (error) {
                console.error('[AsyncSimulator] Submission error:', error);
                if (onError) {
                    onError(error);
                }
                throw error;
            }
        }

        /**
         * Poll task status until complete
         * @param {string} taskId - Task ID to poll
         * @param {Function} onProgress - Progress callback
         * @param {Function} onComplete - Completion callback
         * @param {Function} onError - Error callback
         */
        pollTask(taskId, onProgress, onComplete, onError) {
            let retries = 0;

            const pollerId = setInterval(async () => {
                try {
                    const response = await fetch(`/api/tasks/${taskId}`);

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const status = await response.json();
                    console.log(`[AsyncSimulator] Task ${taskId} status:`, status.state);

                    if (status.state === 'PENDING') {
                        // Task is queued
                        if (onProgress) {
                            onProgress({
                                progress: 0,
                                total: 100,
                                stage: status.stage || 'Pending',
                                status: status.status || 'Task is waiting in queue...'
                            });
                        }

                    } else if (status.state === 'PROGRESS') {
                        // Task is running - show progress
                        if (onProgress) {
                            onProgress({
                                progress: status.progress || 0,
                                total: status.total || 100,
                                stage: status.stage || 'Processing',
                                status: status.status || 'Processing...'
                            });
                        }
                        // Reset retries on successful poll
                        retries = 0;

                    } else if (status.state === 'SUCCESS') {
                        // Task completed - stop polling
                        clearInterval(pollerId);
                        this.activeTasks.delete(taskId);

                        console.log(`[AsyncSimulator] Task ${taskId} completed successfully`);

                        if (onComplete) {
                            onComplete(status.result);
                        }

                    } else if (status.state === 'FAILURE') {
                        // Task failed - stop polling
                        clearInterval(pollerId);
                        this.activeTasks.delete(taskId);

                        console.error(`[AsyncSimulator] Task ${taskId} failed:`, status.error);

                        const error = new Error(status.error || 'Task failed');
                        if (onError) {
                            onError(error);
                        }

                    } else {
                        // Unknown state
                        console.warn(`[AsyncSimulator] Unknown task state: ${status.state}`);
                    }

                } catch (error) {
                    retries++;
                    console.error(`[AsyncSimulator] Polling error (retry ${retries}/${this.maxRetries}):`, error);

                    if (retries >= this.maxRetries) {
                        // Max retries reached - stop polling
                        clearInterval(pollerId);
                        this.activeTasks.delete(taskId);

                        const finalError = new Error(`Polling failed after ${this.maxRetries} retries: ${error.message}`);
                        if (onError) {
                            onError(finalError);
                        }
                    }
                }
            }, this.pollInterval);

            // Store poller ID for cancellation
            this.activeTasks.set(taskId, {
                pollerId,
                startTime: Date.now()
            });
        }

        /**
         * Cancel a running task
         * @param {string} taskId - Task ID to cancel
         * @returns {Promise<void>}
         */
        async cancelTask(taskId) {
            console.log(`[AsyncSimulator] Cancelling task ${taskId}`);

            // Stop local polling
            const taskInfo = this.activeTasks.get(taskId);
            if (taskInfo) {
                clearInterval(taskInfo.pollerId);
                this.activeTasks.delete(taskId);
            }

            // Send cancellation to backend
            try {
                const response = await fetch(`/api/tasks/${taskId}`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    console.warn(`[AsyncSimulator] Failed to cancel task on server: HTTP ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('[AsyncSimulator] Error cancelling task:', error);
                throw error;
            }
        }

        /**
         * Cancel all active tasks
         */
        cancelAll() {
            console.log(`[AsyncSimulator] Cancelling ${this.activeTasks.size} active tasks`);

            const taskIds = Array.from(this.activeTasks.keys());
            return Promise.all(taskIds.map(id => this.cancelTask(id)));
        }

        /**
         * Check if Celery workers are available
         * @returns {Promise<Object>} - Health status
         */
        async checkHealth() {
            try {
                const response = await fetch('/api/health/celery');
                return await response.json();
            } catch (error) {
                console.error('[AsyncSimulator] Health check failed:', error);
                return {
                    status: 'unhealthy',
                    error: error.message
                };
            }
        }

        /**
         * Get number of active tasks
         * @returns {number}
         */
        getActiveTaskCount() {
            return this.activeTasks.size;
        }

        /**
         * Get list of active task IDs
         * @returns {Array<string>}
         */
        getActiveTaskIds() {
            return Array.from(this.activeTasks.keys());
        }
    }

    // ========================================================================
    // UI Helper Functions
    // ========================================================================

    /**
     * Create a progress bar element
     * @param {string} containerId - Container element ID
     * @returns {Object} - Object with update and remove methods
     */
    function createProgressBar(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[AsyncSimulator] Container #${containerId} not found`);
            return null;
        }

        // Create progress bar HTML
        const progressHtml = `
            <div class="async-progress-container" style="margin: 20px 0;">
                <div class="progress-header" style="margin-bottom: 10px;">
                    <strong class="progress-stage">Initializing...</strong>
                    <span class="progress-percentage" style="float: right;">0%</span>
                </div>
                <div class="progress-bar-outer" style="width: 100%; height: 30px; background: #e0e0e0; border-radius: 5px; overflow: hidden;">
                    <div class="progress-bar-inner" style="width: 0%; height: 100%; background: linear-gradient(90deg, #4CAF50, #8BC34A); transition: width 0.3s ease;">
                    </div>
                </div>
                <div class="progress-status" style="margin-top: 5px; font-size: 0.9em; color: #666;">
                    Preparing...
                </div>
                <button class="progress-cancel-btn" style="margin-top: 10px; padding: 5px 15px; background: #f44336; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    Cancel Simulation
                </button>
            </div>
        `;

        container.innerHTML = progressHtml;

        const progressBar = container.querySelector('.progress-bar-inner');
        const progressPercentage = container.querySelector('.progress-percentage');
        const progressStage = container.querySelector('.progress-stage');
        const progressStatus = container.querySelector('.progress-status');
        const cancelBtn = container.querySelector('.progress-cancel-btn');

        return {
            update: (progress, total, stage, status) => {
                const percentage = Math.round((progress / total) * 100);
                progressBar.style.width = `${percentage}%`;
                progressPercentage.textContent = `${percentage}%`;
                if (stage) progressStage.textContent = stage;
                if (status) progressStatus.textContent = status;
            },
            remove: () => {
                container.innerHTML = '';
            },
            onCancel: (callback) => {
                cancelBtn.addEventListener('click', callback);
            },
            setError: (error) => {
                progressBar.style.background = '#f44336';
                progressStage.textContent = 'Error';
                progressStatus.textContent = error;
                cancelBtn.textContent = 'Close';
            },
            setSuccess: () => {
                progressBar.style.background = '#4CAF50';
                progressStage.textContent = 'Complete';
                progressStatus.textContent = 'Simulation completed successfully!';
                cancelBtn.textContent = 'Close';
            }
        };
    }

    // ========================================================================
    // Export to global scope
    // ========================================================================

    global.AsyncSimulator = AsyncSimulator;
    global.asyncSimulator = new AsyncSimulator(); // Global singleton
    global.createProgressBar = createProgressBar;

    console.log('[AsyncSimulator] Loaded successfully');

})(typeof window !== 'undefined' ? window : this);
