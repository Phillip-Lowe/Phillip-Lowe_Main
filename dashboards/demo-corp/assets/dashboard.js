// SyStack White-Label Dashboard JS
// Auto-refreshes every 30 seconds

const CONFIG = {
    refreshInterval: 30000,
    apiBase: '/api/v1',
    clientId: '{{client_id}}'
};

// Mock data for scaffolding — replace with real API calls
const AGENTS = [
    { name: 'Invoice Agent', emoji: '📄', status: 'online', tasks: 245 },
    { name: 'Booking Agent', emoji: '📅', status: 'online', tasks: 189 },
    { name: 'Communication', emoji: '💬', status: 'busy', tasks: 56 },
    { name: 'Compliance', emoji: '⚖️', status: 'online', tasks: 12 },
    { name: 'Analytics', emoji: '📊', status: 'online', tasks: 78 }
];

const LOCATIONS = [
    { region: 'ord', name: 'Chicago', status: 'active', ip: '192.0.2.1', uptime: '99.99%' },
    { region: 'lax', name: 'Los Angeles', status: 'active', ip: '192.0.2.2', uptime: '99.97%' },
    { region: 'lon', name: 'London', status: 'active', ip: '192.0.2.3', uptime: '99.98%' }
];

const COMPLIANCE = [
    { framework: 'SOC 2 Type I', status: 'ready', last_audit: '2026-06-01' },
    { framework: 'GDPR', status: 'ready', last_audit: '2026-06-01' },
    { framework: 'HIPAA', status: 'pending', last_audit: '—' },
    { framework: 'CCPA', status: 'ready', last_audit: '2026-06-01' }
];

function renderAgents() {
    const container = document.getElementById('agent-status-container');
    if (!container) return;
    
    container.innerHTML = AGENTS.map(agent => `
        <div class="agent-card">
            <div class="agent-header">
                <span class="agent-emoji">${agent.emoji}</span>
                <span class="agent-name">${agent.name}</span>
                <span class="agent-status status-${agent.status}"></span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600);">
                ${agent.tasks} tasks completed today
            </div>
        </div>
    `).join('');
}

function renderLocations() {
    const container = document.getElementById('location-container');
    if (!container) return;
    
    container.innerHTML = LOCATIONS.map(loc => `
        <div class="location-card">
            <div class="agent-header">
                <span class="agent-emoji">🌍</span>
                <span class="agent-name">${loc.name} (${loc.region.toUpperCase()})</span>
                <span class="agent-status status-${loc.status === 'active' ? 'online' : 'offline'}"></span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">
                IP: ${loc.ip} | Uptime: ${loc.uptime}
            </div>
        </div>
    `).join('');
}

function renderCompliance() {
    const container = document.querySelector('.compliance-grid');
    if (!container) return;
    
    container.innerHTML = COMPLIANCE.map(item => `
        <div class="compliance-card">
            <div class="agent-header">
                <span class="agent-emoji">${item.status === 'ready' ? '✅' : '⏳'}</span>
                <span class="agent-name">${item.framework}</span>
                <span style="margin-left: auto; font-size: 0.75rem; color: ${item.status === 'ready' ? 'var(--success)' : 'var(--warning)'};">
                    ${item.status.toUpperCase()}
                </span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">
                Last audit: ${item.last_audit}
            </div>
        </div>
    `).join('');
}

function init() {
    renderAgents();
    renderLocations();
    renderCompliance();
    
    // Auto-refresh
    setInterval(() => {
        renderAgents();
        renderLocations();
    }, CONFIG.refreshInterval);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
