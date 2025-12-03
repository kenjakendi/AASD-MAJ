// Dashboard JavaScript - Real-time Communication Visualization

// Global state
let socket;
let network;
let messageTypeChart;
let physicsEnabled = true;
let messageCount = 0;

// Agent role icons
const roleIcons = {
    'coordinator': '🎯',
    'caretaker': '👤',
    'cleaner': '🧹',
    'veterinarian': '⚕️',
    'reception': '📋',
    'adoption': '🏠',
    'animal': '🐾',
    'room': '🚪',
    'default': '🤖'
};

// Agent role colors
const roleColors = {
    'coordinator': '#ef4444',
    'caretaker': '#3b82f6',
    'cleaner': '#8b5cf6',
    'veterinarian': '#10b981',
    'reception': '#f59e0b',
    'adoption': '#ec4899',
    'animal': '#14b8a6',
    'room': '#6366f1',
    'default': '#64748b'
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    
    // Wait for libraries to load
    if (typeof io === 'undefined') {
        console.error('Socket.IO not loaded!');
        return;
    }
    if (typeof vis === 'undefined') {
        console.error('vis.js not loaded!');
        return;
    }
    if (typeof Chart === 'undefined') {
        console.error('Chart.js not loaded!');
        return;
    }
    
    console.log('All libraries loaded successfully');
    initializeNetwork();
    initializeChart();
    setupEventListeners();
    initializeSocket(); // Initialize socket last
});

// Socket.IO initialization
function initializeSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('init_data', (data) => {
        console.log('Received initial data', data);
        try {
            if (data.agents) {
                console.log('Updating agents:', Object.keys(data.agents).length);
                updateAgents(data.agents);
            }
            if (data.messages) {
                console.log('Updating messages:', data.messages.length);
                updateMessages(data.messages);
            }
            if (data.statistics) {
                console.log('Updating statistics');
                updateStatistics(data.statistics);
            }
            if (data.agents) {
                console.log('Updating network graph with agents:', Object.keys(data.agents).length);
                // Always update graph if we have agents, even without explicit connections
                const connections = data.connections || [];
                console.log('Connections:', connections.length);
                updateNetworkGraph(data.agents, connections);
            }
        } catch (error) {
            console.error('Error processing init_data:', error);
        }
    });
    
    socket.on('new_message', (message) => {
        try {
            addMessageToTimeline(message);
            messageCount++;
            updateNetworkWithMessage(message);
        } catch (error) {
            console.error('Error processing new_message:', error);
        }
    });
    
    socket.on('statistics_update', (stats) => {
        try {
            if (stats) updateStatistics(stats);
        } catch (error) {
            console.error('Error processing statistics_update:', error);
        }
    });
    
    socket.on('agents_update', (agents) => {
        try {
            if (agents) updateAgents(agents);
        } catch (error) {
            console.error('Error processing agents_update:', error);
        }
    });
}

// Network graph initialization
function initializeNetwork() {
    const container = document.getElementById('network-graph');
    
    const data = {
        nodes: new vis.DataSet([]),
        edges: new vis.DataSet([])
    };
    
    const options = {
        nodes: {
            shape: 'dot',
            size: 25,
            font: {
                size: 14,
                color: '#f1f5f9'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            arrows: {
                to: { enabled: true, scaleFactor: 0.5 }
            },
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'none'
            },
            color: {
                color: '#64748b',
                highlight: '#3b82f6',
                opacity: 0.6
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.04
            },
            stabilization: {
                iterations: 150
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100
        }
    };
    
    network = new vis.Network(container, data, options);
    
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            console.log('Clicked node:', nodeId);
        }
    });
}

// Chart initialization
function initializeChart() {
    const ctx = document.getElementById('message-type-chart').getContext('2d');
    
    messageTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#3b82f6',
                    '#8b5cf6',
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#ec4899',
                    '#14b8a6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f1f5f9',
                        padding: 10,
                        font: { size: 11 }
                    }
                },
                title: {
                    display: true,
                    text: 'Messages by Type',
                    color: '#f1f5f9',
                    font: { size: 14 }
                }
            }
        }
    });
}

// Event listeners
function setupEventListeners() {
    document.getElementById('reset-view').addEventListener('click', () => {
        network.fit();
    });
    
    document.getElementById('toggle-physics').addEventListener('click', (e) => {
        physicsEnabled = !physicsEnabled;
        network.setOptions({ physics: { enabled: physicsEnabled } });
        e.target.textContent = `Physics: ${physicsEnabled ? 'ON' : 'OFF'}`;
    });
    
    document.getElementById('clear-timeline').addEventListener('click', () => {
        document.getElementById('message-timeline').innerHTML = '';
        messageCount = 0;
    });
}

// Update functions
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const dot = statusElement.querySelector('.status-dot');
    
    if (connected) {
        statusElement.innerHTML = '<span class="status-dot"></span> Connected';
        dot.classList.remove('disconnected');
    } else {
        statusElement.innerHTML = '<span class="status-dot disconnected"></span> Disconnected';
    }
}

function updateAgents(agents) {
    const agentList = document.getElementById('agent-list');
    const agentCount = document.getElementById('agent-count');
    
    agentCount.innerHTML = `Agents: <strong>${Object.keys(agents).length}</strong>`;
    
    agentList.innerHTML = '';
    
    Object.entries(agents).forEach(([name, agent]) => {
        const role = agent.role || 'default';
        const icon = roleIcons[role] || roleIcons.default;
        
        const agentItem = document.createElement('div');
        agentItem.className = 'agent-item';
        agentItem.innerHTML = `
            <div class="agent-icon">${icon}</div>
            <div class="agent-info">
                <div class="agent-name">${name}</div>
                <div class="agent-role">${role}</div>
            </div>
            <div class="agent-status"></div>
        `;
        agentList.appendChild(agentItem);
    });
}

function updateMessages(messages) {
    const timeline = document.getElementById('message-timeline');
    timeline.innerHTML = '';
    
    messages.slice(-20).reverse().forEach(msg => {
        addMessageToTimeline(msg, false);
    });
}

function addMessageToTimeline(message, animate = true) {
    const timeline = document.getElementById('message-timeline');
    
    const messageItem = document.createElement('div');
    messageItem.className = 'message-item';
    if (!animate) messageItem.style.animation = 'none';
    
    const time = new Date(message.timestamp).toLocaleTimeString();
    const contentPreview = JSON.stringify(message.content).substring(0, 100);
    
    messageItem.innerHTML = `
        <div class="message-header">
            <span class="message-from-to">${message.from} → ${message.to}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-meta">
            <span class="badge performative">${message.performative}</span>
            <span class="badge protocol">${message.protocol}</span>
        </div>
        <div class="message-content">${contentPreview}</div>
    `;
    
    timeline.insertBefore(messageItem, timeline.firstChild);
    
    // Keep only last 50 messages in DOM
    while (timeline.children.length > 50) {
        timeline.removeChild(timeline.lastChild);
    }
}

function updateStatistics(stats) {
    try {
        document.getElementById('total-messages').textContent = stats.total_messages || 0;
        document.getElementById('active-agents').textContent = stats.active_agents || 0;
        document.getElementById('message-count').innerHTML = 
            `Messages: <strong>${stats.total_messages || 0}</strong>`;
        document.getElementById('messages-per-sec').innerHTML = 
            `Rate: <strong>${(stats.messages_per_second || 0).toFixed(2)}</strong> msg/s`;
        
        // Update uptime
        const uptime = stats.uptime_seconds || 0;
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = Math.floor(uptime % 60);
        document.getElementById('uptime').textContent = 
            `${hours}h ${minutes}m ${seconds}s`;
        
        // Update chart (check if it exists first)
        if (messageTypeChart && stats.messages_by_type) {
            const labels = Object.keys(stats.messages_by_type);
            const data = Object.values(stats.messages_by_type);
            
            messageTypeChart.data.labels = labels;
            messageTypeChart.data.datasets[0].data = data;
            messageTypeChart.update('none'); // Update without animation for performance
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

function updateNetworkGraph(agents, connections) {
    try {
        if (!network) {
            console.error('Network not initialized');
            return;
        }
        
        console.log('updateNetworkGraph called with', Object.keys(agents).length, 'agents');
        
        const nodes = new vis.DataSet();
        const edges = new vis.DataSet();
        
        // Add agent nodes
        Object.entries(agents).forEach(([name, agent]) => {
            const role = agent.role || 'default';
            const color = roleColors[role] || roleColors.default;
            const icon = roleIcons[role] || roleIcons.default;
            
            console.log('Adding node:', name, role);
            
            nodes.add({
                id: name,
                label: `${icon}\n${name}`,
                color: {
                    background: color,
                    border: color,
                    highlight: { background: color, border: '#ffffff' }
                },
                title: `${name} (${role})\nMessages: ${agent.message_count || 0}`,
                font: { color: '#f1f5f9' }
            });
        });
        
        // Add edges from connections
        if (connections && Array.isArray(connections)) {
            console.log('Adding', connections.length, 'connections');
            connections.forEach((conn, index) => {
                edges.add({
                    id: `edge-${index}`,
                    from: conn.from,
                    to: conn.to,
                    value: conn.count || 1,
                    title: `${conn.count} messages\nProtocols: ${(conn.protocols || []).join(', ')}`,
                    label: (conn.count || 1).toString()
                });
            });
        }
        
        console.log('Setting network data: nodes=', nodes.length, 'edges=', edges.length);
        network.setData({ nodes: nodes, edges: edges });
        
        // Fit network to view
        setTimeout(() => {
            console.log('Fitting network to view');
            network.fit({
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }, 200);
    } catch (error) {
        console.error('Error updating network graph:', error);
        console.error('Stack:', error.stack);
    }
}

function updateNetworkWithMessage(message) {
    try {
        if (!network || !network.body || !network.body.data) {
            return;
        }
        
        const edges = network.body.data.edges;
        const edgeId = `${message.from}-${message.to}`;
        
        // Find or create edge
        let edge = edges.get(edgeId);
        if (edge) {
            edge.value = (edge.value || 1) + 1;
            edge.label = edge.value.toString();
            edges.update(edge);
            
            // Flash effect only if edge exists
            try {
                network.selectEdges([edgeId]);
                setTimeout(() => network.unselectAll(), 500);
            } catch (e) {
                // Edge selection failed, ignore
            }
        } else {
            // Create new edge
            try {
                edges.add({
                    id: edgeId,
                    from: message.from,
                    to: message.to,
                    value: 1,
                    label: '1',
                    arrows: {
                        to: { enabled: true, scaleFactor: 0.5 }
                    },
                    color: {
                        color: '#64748b',
                        highlight: '#3b82f6'
                    }
                });
            } catch (e) {
                console.log('Could not create edge:', edgeId);
            }
        }
        
    } catch (error) {
        console.error('Error updating network:', error);
    }
}

