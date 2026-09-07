/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/insights.js
 * Description: Dynamically renders business findings, root-cause analyses, and recommendations.
 */

async function loadInsights() {
    try {
        const res = await fetch('/api/insights');
        const json = await res.json();
        if (!json.success) return;

        const container = document.getElementById('insightsContainer');
        container.innerHTML = '';

        json.data.forEach(item => {
            const card = document.createElement('div');
            card.className = `insight-card ${item.type || ''}`;

            const badgeColor = item.type === 'positive' ? 'bg-success' :
                              (item.type === 'warning' ? 'bg-warning text-dark' : 'bg-primary');

            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="insight-meta">${item.category}</span>
                    <span class="badge ${badgeColor}">${item.type.toUpperCase()}</span>
                </div>
                <h5 class="insight-title">${item.title}</h5>

                <div class="insight-section">
                    <div class="insight-section-title text-primary">
                        <i class="fa-solid fa-chart-line"></i> Empirical Observation
                    </div>
                    <div class="insight-text">${item.observation}</div>
                </div>

                <div class="insight-section">
                    <div class="insight-section-title text-secondary">
                        <i class="fa-solid fa-magnifying-glass-chart"></i> Commercial Business Meaning
                    </div>
                    <div class="insight-text">${item.business_meaning}</div>
                </div>

                <div class="insight-section mb-0">
                    <div class="insight-section-title text-success">
                        <i class="fa-solid fa-bullseye"></i> Actionable Management Recommendation
                    </div>
                    <div class="insight-text fw-medium" style="color: #0f766e;">${item.recommendation}</div>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed loading insights:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadInsights);
