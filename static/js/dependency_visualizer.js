/**
 * Dependency Visualizer - Network Diagram for Project Dependencies
 *
 * Uses vis-network to create an interactive dependency graph
 * showing dependencies between projects in a portfolio.
 *
 * Features:
 * - Visual network diagram (nodes = projects, edges = dependencies)
 * - Drag-and-drop to create dependencies
 * - Click to remove dependencies
 * - Color-coded by status/risk
 * - Interactive tooltips
 */

class DependencyVisualizer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.network = null;
        this.projects = [];
        this.dependencies = [];
        this.portfolioId = null;

        // Callbacks
        this.onDependencyAdded = null;
        this.onDependencyRemoved = null;
        this.onProjectClicked = null;
    }

    /**
     * Initialize the network visualization
     */
    initialize(projects, dependencies, portfolioId) {
        this.projects = projects;
        this.dependencies = dependencies;
        this.portfolioId = portfolioId;

        // Create nodes from projects
        const nodes = this.createNodes();

        // Create edges from dependencies
        const edges = this.createEdges();

        // Create network
        const data = { nodes, edges };
        const options = this.getNetworkOptions();

        this.network = new vis.Network(this.container, data, options);

        // Setup event handlers
        this.setupEventHandlers();

        return this.network;
    }

    /**
     * Create nodes from projects
     */
    createNodes() {
        const nodes = new vis.DataSet();

        this.projects.forEach(project => {
            const node = {
                id: project.id,
                label: this.truncateLabel(project.name, 20),
                title: this.createTooltip(project),
                shape: 'box',
                color: this.getNodeColor(project),
                font: {
                    size: 14,
                    color: '#ffffff'
                },
                borderWidth: 2,
                shadow: true
            };

            nodes.add(node);
        });

        return nodes;
    }

    /**
     * Create edges from dependencies
     */
    createEdges() {
        const edges = new vis.DataSet();

        this.dependencies.forEach((dep, index) => {
            const edge = {
                id: `dep-${index}`,
                from: dep.source_id,
                to: dep.target_id,
                arrows: 'to',
                color: {
                    color: this.getEdgeColor(dep),
                    highlight: '#ff5722'
                },
                width: 2,
                smooth: {
                    type: 'curvedCW',
                    roundness: 0.2
                },
                title: dep.name || `${dep.source_name} → ${dep.target_name}`
            };

            edges.add(edge);
        });

        return edges;
    }

    /**
     * Get network visualization options
     */
    getNetworkOptions() {
        return {
            nodes: {
                shape: 'box',
                margin: 10,
                widthConstraint: {
                    minimum: 100,
                    maximum: 200
                }
            },
            edges: {
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 1
                    }
                },
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'horizontal'
                }
            },
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: 'LR',  // Left to Right
                    sortMethod: 'directed',
                    levelSeparation: 200,
                    nodeSpacing: 150
                }
            },
            physics: {
                enabled: false  // Disable physics for stable layout
            },
            interaction: {
                dragNodes: true,
                dragView: true,
                zoomView: true,
                hover: true,
                tooltipDelay: 200
            },
            manipulation: {
                enabled: false  // We'll handle this manually
            }
        };
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Click on node
        this.network.on('click', (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                if (this.onProjectClicked) {
                    this.onProjectClicked(nodeId);
                }
            }

            // Click on edge (to remove)
            if (params.edges.length > 0) {
                const edgeId = params.edges[0];
                this.handleEdgeClick(edgeId);
            }
        });

        // Double click to add dependency
        this.network.on('doubleClick', (params) => {
            if (params.nodes.length > 0) {
                this.startDependencyMode(params.nodes[0]);
            }
        });

        // Hover effects
        this.network.on('hoverNode', (params) => {
            this.highlightNodeDependencies(params.node);
        });

        this.network.on('blurNode', () => {
            this.resetHighlights();
        });
    }

    /**
     * Handle edge click (remove dependency)
     */
    handleEdgeClick(edgeId) {
        if (confirm('Remove this dependency?')) {
            const edges = this.network.body.data.edges;
            const edge = edges.get(edgeId);

            if (edge && this.onDependencyRemoved) {
                this.onDependencyRemoved(edge.from, edge.to);
            }

            edges.remove(edgeId);
        }
    }

    /**
     * Start dependency creation mode
     */
    startDependencyMode(sourceNodeId) {
        const message = document.createElement('div');
        message.id = 'dependency-mode-message';
        message.className = 'alert alert-info';
        message.style.position = 'fixed';
        message.style.top = '20px';
        message.style.right = '20px';
        message.style.zIndex = '9999';
        message.innerHTML = `
            <strong>Dependency Mode:</strong><br>
            Click on target project to create dependency<br>
            <button class="btn btn-sm btn-secondary mt-2" onclick="cancelDependencyMode()">Cancel</button>
        `;
        document.body.appendChild(message);

        // Store source node
        this.dependencySourceNode = sourceNodeId;

        // Setup temporary click handler
        this.tempClickHandler = (params) => {
            if (params.nodes.length > 0 && params.nodes[0] !== sourceNodeId) {
                this.createDependency(sourceNodeId, params.nodes[0]);
                this.endDependencyMode();
            }
        };

        this.network.on('click', this.tempClickHandler);
    }

    /**
     * End dependency creation mode
     */
    endDependencyMode() {
        const message = document.getElementById('dependency-mode-message');
        if (message) {
            message.remove();
        }

        if (this.tempClickHandler) {
            this.network.off('click', this.tempClickHandler);
            this.tempClickHandler = null;
        }

        this.dependencySourceNode = null;
    }

    /**
     * Create a new dependency
     */
    createDependency(sourceId, targetId) {
        // Check if dependency already exists
        const edges = this.network.body.data.edges;
        const existing = edges.get().find(e => e.from === sourceId && e.to === targetId);

        if (existing) {
            alert('Dependency already exists!');
            return;
        }

        // Check for circular dependency
        if (this.wouldCreateCircle(sourceId, targetId)) {
            alert('Cannot create circular dependency!');
            return;
        }

        // Add edge
        const sourceProject = this.projects.find(p => p.id === sourceId);
        const targetProject = this.projects.find(p => p.id === targetId);

        const newEdge = {
            id: `dep-${Date.now()}`,
            from: sourceId,
            to: targetId,
            arrows: 'to',
            color: { color: '#2196F3' },
            width: 2,
            title: `${sourceProject?.name} depends on ${targetProject?.name}`
        };

        edges.add(newEdge);

        // Callback
        if (this.onDependencyAdded) {
            this.onDependencyAdded(sourceId, targetId);
        }
    }

    /**
     * Check if adding dependency would create circular reference
     */
    wouldCreateCircle(fromId, toId) {
        const edges = this.network.body.data.edges.get();

        // Build adjacency list
        const graph = {};
        edges.forEach(edge => {
            if (!graph[edge.from]) graph[edge.from] = [];
            graph[edge.from].push(edge.to);
        });

        // Add proposed edge
        if (!graph[fromId]) graph[fromId] = [];
        graph[fromId].push(toId);

        // DFS to detect cycle
        const visited = new Set();
        const recStack = new Set();

        const hasCycle = (node) => {
            if (recStack.has(node)) return true;
            if (visited.has(node)) return false;

            visited.add(node);
            recStack.add(node);

            const neighbors = graph[node] || [];
            for (const neighbor of neighbors) {
                if (hasCycle(neighbor)) return true;
            }

            recStack.delete(node);
            return false;
        };

        // Check all nodes
        for (const node in graph) {
            if (hasCycle(parseInt(node))) {
                return true;
            }
        }

        return false;
    }

    /**
     * Highlight node and its dependencies
     */
    highlightNodeDependencies(nodeId) {
        const edges = this.network.body.data.edges.get();
        const connectedEdges = edges.filter(e => e.from === nodeId || e.to === nodeId);

        // Highlight connected edges
        connectedEdges.forEach(edge => {
            this.network.body.data.edges.update({
                id: edge.id,
                width: 4
            });
        });
    }

    /**
     * Reset all highlights
     */
    resetHighlights() {
        const edges = this.network.body.data.edges.get();
        edges.forEach(edge => {
            this.network.body.data.edges.update({
                id: edge.id,
                width: 2
            });
        });
    }

    /**
     * Get node color based on project status/risk
     */
    getNodeColor(project) {
        // Priority-based colors
        if (project.priority === 1) {
            return {
                background: '#f44336',  // Red (high priority)
                border: '#c62828',
                highlight: { background: '#ef5350', border: '#c62828' }
            };
        } else if (project.priority === 2) {
            return {
                background: '#ff9800',  // Orange (medium priority)
                border: '#f57c00',
                highlight: { background: '#ffa726', border: '#f57c00' }
            };
        } else {
            return {
                background: '#4caf50',  // Green (low priority)
                border: '#388e3c',
                highlight: { background: '#66bb6a', border: '#388e3c' }
            };
        }
    }

    /**
     * Get edge color based on dependency criticality
     */
    getEdgeColor(dependency) {
        if (dependency.criticality === 'CRITICAL') {
            return '#f44336';  // Red
        } else if (dependency.criticality === 'HIGH') {
            return '#ff9800';  // Orange
        } else if (dependency.criticality === 'MEDIUM') {
            return '#2196F3';  // Blue
        } else {
            return '#9e9e9e';  // Gray
        }
    }

    /**
     * Create tooltip for node
     */
    createTooltip(project) {
        return `
            <strong>${project.name}</strong><br>
            Priority: ${project.priority}<br>
            Status: ${project.status || 'active'}<br>
            ${project.backlog ? `Backlog: ${project.backlog} items` : ''}
        `;
    }

    /**
     * Truncate label to max length
     */
    truncateLabel(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    /**
     * Update visualization with new data
     */
    update(projects, dependencies) {
        this.projects = projects;
        this.dependencies = dependencies;

        if (this.network) {
            const nodes = this.createNodes();
            const edges = this.createEdges();

            this.network.setData({ nodes, edges });
        }
    }

    /**
     * Fit network to container
     */
    fit() {
        if (this.network) {
            this.network.fit({
                animation: {
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }
    }

    /**
     * Export network as image
     */
    exportAsImage() {
        if (this.network) {
            const canvas = this.network.canvas.frame.canvas;
            return canvas.toDataURL('image/png');
        }
        return null;
    }

    /**
     * Destroy network
     */
    destroy() {
        if (this.network) {
            this.network.destroy();
            this.network = null;
        }
    }
}

// Global function to cancel dependency mode (called from button)
function cancelDependencyMode() {
    const message = document.getElementById('dependency-mode-message');
    if (message) {
        message.remove();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DependencyVisualizer;
}
