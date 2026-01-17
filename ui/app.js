/**
 * Sentinel UI - Professional Trace Inspector
 * 
 * Handles trace listing, filtering, detail view, and replay.
 */

const API_BASE = '/v1';
let currentTraceId = null;
let traces = [];
let currentFilter = 'all';
let visibleCount = 5; // Pagination: show 5 at a time
const PAGE_SIZE = 5;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', () => {
    loadTraces();
});

/**
 * Load traces from the API
 */
async function loadTraces() {
    const traceList = document.getElementById('traceList');
    traceList.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/traces?limit=100`);
        const data = await response.json();

        traces = data.traces || [];
        visibleCount = PAGE_SIZE; // Reset pagination on reload

        // Update stats
        updateStats();

        // Render list
        renderTraceList();
    } catch (error) {
        traceList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error loading traces</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

/**
 * Update header stats
 */
function updateStats() {
    document.getElementById('totalTraces').textContent = traces.length;

    const passed = traces.filter(t => t.verdict?.status === 'pass').length;
    const failed = traces.filter(t => t.verdict?.status === 'fail').length;

    document.getElementById('passedTraces').textContent = passed || '-';
    document.getElementById('failedTraces').textContent = failed || '-';
}

/**
 * Set filter and re-render
 */
function setFilter(filter, element) {
    currentFilter = filter;
    visibleCount = PAGE_SIZE; // Reset pagination when filter changes

    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    }

    renderTraceList();
}

/**
 * Load more traces (pagination)
 */
function loadMore() {
    visibleCount += PAGE_SIZE;
    renderTraceList();
}

/**
 * Get filtered traces based on current filter
 */
function getFilteredTraces() {
    if (currentFilter === 'failed') {
        return traces.filter(t => t.verdict?.status === 'fail');
    } else if (currentFilter === 'passed') {
        return traces.filter(t => t.verdict?.status === 'pass');
    }
    return traces;
}

/**
 * Render the trace list
 */
function renderTraceList() {
    const traceList = document.getElementById('traceList');

    // Apply filter
    const filteredTraces = getFilteredTraces();

    if (filteredTraces.length === 0) {
        let emptyIcon = '📋';
        let emptyTitle = 'No traces yet';
        let emptyMsg = 'Make some LLM calls to see them here';

        if (currentFilter === 'failed') {
            emptyIcon = '✅';
            emptyTitle = 'No failed traces';
            emptyMsg = 'All traces are passing!';
        } else if (currentFilter === 'passed') {
            emptyIcon = '⏳';
            emptyTitle = 'No passed traces';
            emptyMsg = 'No traces with passing verdicts yet';
        }

        traceList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${emptyIcon}</div>
                <h3>${emptyTitle}</h3>
                <p>${emptyMsg}</p>
            </div>
        `;
        return;
    }

    // Paginate - show only visibleCount
    const visibleTraces = filteredTraces.slice(0, visibleCount);
    const hasMore = filteredTraces.length > visibleCount;

    let html = visibleTraces.map(trace => {
        const time = formatTime(trace.timestamp);
        const preview = trace.request.messages?.[0]?.content?.substring(0, 60) || 'No message';
        const isActive = trace.trace_id === currentTraceId ? 'active' : '';

        // Verdict styling
        let verdictClass = 'pending';
        let verdictIcon = '⏳';
        if (trace.verdict) {
            if (trace.verdict.status === 'pass') {
                verdictClass = 'pass';
                verdictIcon = '✓';
            } else {
                verdictClass = 'fail';
                verdictIcon = '✕';
            }
        }

        return `
            <div class="trace-item ${isActive} verdict-${verdictClass} fade-in" onclick="selectTrace('${trace.trace_id}')">
                <div class="trace-header">
                    <div class="verdict-badge ${verdictClass}">${verdictIcon}</div>
                    <span class="trace-model">${trace.request.model}</span>
                    <span class="trace-provider">${trace.request.provider}</span>
                </div>
                <div class="trace-preview">${escapeHtml(preview)}...</div>
                <div class="trace-meta">
                    <span class="trace-meta-item">⏱ ${trace.response.latency_ms}ms</span>
                    <span class="trace-meta-item">🕐 ${time}</span>
                    ${trace.blessed ? '<span class="tag tag-golden">⭐ Golden</span>' : ''}
                    ${trace.replay_of ? '<span class="tag tag-replay">↩ Replay</span>' : ''}
                </div>
            </div>
        `;
    }).join('');

    // Add "Load More" button if there are more traces
    if (hasMore) {
        const remaining = filteredTraces.length - visibleCount;
        html += `
            <button class="load-more-btn" onclick="loadMore()">
                Load More (${remaining} remaining)
            </button>
        `;
    }

    traceList.innerHTML = html;
}

/**
 * Select and show a trace
 */
async function selectTrace(traceId) {
    currentTraceId = traceId;
    const detail = document.getElementById('traceDetail');
    const replayBtn = document.getElementById('replayBtn');

    // Update active state in list
    renderTraceList();

    detail.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/traces/${traceId}`);
        const trace = await response.json();

        replayBtn.disabled = false;

        // Build verdict section
        let verdictHtml = '';
        if (trace.verdict) {
            const isPass = trace.verdict.status === 'pass';
            verdictHtml = `
                <div class="verdict-banner ${isPass ? 'pass' : 'fail'} fade-in">
                    <div class="verdict-banner-icon">${isPass ? '✓' : '✕'}</div>
                    <div class="verdict-banner-text">
                        <h3>VERDICT: ${isPass ? 'PASSED' : 'FAILED'}</h3>
                        <p>${isPass ? 'All expectations met' : `Severity: ${trace.verdict.severity?.toUpperCase() || 'UNKNOWN'}`}</p>
                    </div>
                </div>
            `;

            if (!isPass && trace.verdict.violations?.length > 0) {
                verdictHtml += `
                    <div class="violations-list fade-in">
                        <div class="violations-title">Violations</div>
                        ${trace.verdict.violations.map(v => `
                            <div class="violation-item">
                                <span class="violation-icon">⚠</span>
                                <span>${escapeHtml(v)}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        }

        detail.innerHTML = `
            ${verdictHtml}
            
            <div class="detail-section fade-in">
                <h3 class="section-title">Trace Information</h3>
                <div class="info-grid">
                    <div class="info-item" style="grid-column: span 2;">
                        <div class="info-label">Trace ID</div>
                        <div class="info-value" style="font-size: 12px; word-break: break-all;">${trace.trace_id}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Timestamp</div>
                        <div class="info-value">${formatTime(trace.timestamp)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Model</div>
                        <div class="info-value">${trace.request.model}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Provider</div>
                        <div class="info-value">${trace.request.provider}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Latency</div>
                        <div class="info-value ${trace.response.latency_ms > 2000 ? 'error' : 'success'}">${trace.response.latency_ms}ms</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Status</div>
                        <div class="info-value">${trace.blessed ? '⭐ Golden Reference' : 'Standard Trace'}</div>
                    </div>
                </div>
            </div>
            
            <div class="detail-section fade-in">
                <h3 class="section-title">Messages</h3>
                ${trace.request.messages.map(msg => `
                    <div class="message ${msg.role}">
                        <div class="message-role">${msg.role}</div>
                        <div class="message-content">${escapeHtml(msg.content)}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="detail-section fade-in">
                <h3 class="section-title">Response</h3>
                <div class="response-box">${escapeHtml(trace.response.text)}</div>
            </div>
            
            ${trace.response.usage ? `
                <div class="detail-section fade-in">
                    <h3 class="section-title">Token Usage</h3>
                    <div class="info-grid">
                        ${Object.entries(trace.response.usage).map(([key, value]) => `
                            <div class="info-item">
                                <div class="info-label">${key.replace(/_/g, ' ')}</div>
                                <div class="info-value">${value}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${trace.replay_of ? `
                <div class="detail-section fade-in">
                    <h3 class="section-title">Lineage</h3>
                    <div class="info-item">
                        <div class="info-label">Replay of</div>
                        <div class="info-value">${trace.replay_of}</div>
                    </div>
                </div>
            ` : ''}
        `;
    } catch (error) {
        detail.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error loading trace</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

/**
 * Replay the current trace
 */
async function replayTrace() {
    if (!currentTraceId) return;

    const replayBtn = document.getElementById('replayBtn');
    replayBtn.disabled = true;
    replayBtn.innerHTML = '↻ Replaying...';

    try {
        const response = await fetch(`${API_BASE}/replay/${currentTraceId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const result = await response.json();

        if (response.ok) {
            // Show success notification
            showNotification('Replay successful!', 'success');
            loadTraces();
            selectTrace(result.new_trace_id);
        } else {
            showNotification(`Replay failed: ${result.detail}`, 'error');
        }
    } catch (error) {
        showNotification(`Replay error: ${error.message}`, 'error');
    } finally {
        replayBtn.disabled = false;
        replayBtn.innerHTML = '↻ Replay';
    }
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 16px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 1000;
        animation: fadeIn 0.3s ease-out;
        ${type === 'success' ? 'background: #22c55e; color: white;' : ''}
        ${type === 'error' ? 'background: #ef4444; color: white;' : ''}
        ${type === 'info' ? 'background: #6366f1; color: white;' : ''}
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Format timestamp
 */
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // Format options
    const timeOpts = { hour: '2-digit', minute: '2-digit', hour12: true };
    const dateOpts = { month: 'short', day: 'numeric' };

    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }

    // Less than 1 hour
    if (diff < 3600000) {
        const mins = Math.floor(diff / 60000);
        return `${mins}m ago`;
    }

    // Less than 24 hours - show time
    if (diff < 86400000) {
        return date.toLocaleTimeString('en-US', timeOpts);
    }

    // Less than 7 days - show day + time
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days}d ago, ${date.toLocaleTimeString('en-US', timeOpts)}`;
    }

    // Otherwise show full date
    return `${date.toLocaleDateString('en-US', dateOpts)}, ${date.toLocaleTimeString('en-US', timeOpts)}`;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
