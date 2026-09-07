/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/stores.js
 * Description: Store analytics, regional comparisons, and benchmarking matrix.
 */

let storesComparisonBarChart = null;
let regionalShareDonutChart = null;

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

async function loadStoreAnalytics() {
    try {
        const res = await fetch('/api/stores/performance');
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const labels = data.map(d => d.store_city);
        const revenues = data.map(d => d.revenue);
        const profits = data.map(d => d.profit);

        // 1. Comparison Bar Chart (Revenue & Profit)
        const ctxB = document.getElementById('storesComparisonBarChart').getContext('2d');
        if (storesComparisonBarChart) storesComparisonBarChart.destroy();

        storesComparisonBarChart = new Chart(ctxB, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Gross Revenue',
                        data: revenues,
                        backgroundColor: '#2563eb',
                        borderRadius: 4
                    },
                    {
                        label: 'Gross Profit',
                        data: profits,
                        backgroundColor: '#10b981',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`
                        }
                    }
                },
                scales: {
                    y: { ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` } },
                    x: { grid: { display: false } }
                }
            }
        });

        // 2. Regional Share Donut
        const regionalMap = {};
        data.forEach(d => {
            regionalMap[d.region] = (regionalMap[d.region] || 0) + d.revenue;
        });

        const regLabels = Object.keys(regionalMap);
        const regValues = Object.values(regionalMap);

        const ctxR = document.getElementById('regionalShareDonutChart').getContext('2d');
        if (regionalShareDonutChart) regionalShareDonutChart.destroy();

        regionalShareDonutChart = new Chart(ctxR, {
            type: 'doughnut',
            data: {
                labels: regLabels,
                datasets: [{
                    data: regValues,
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`
                        }
                    }
                },
                cutout: '65%'
            }
        });

        // 3. Populate Store Benchmarking Table
        const tbody = document.getElementById('storeBenchmarkTableBody');
        tbody.innerHTML = '';

        data.forEach((s, idx) => {
            const tr = document.createElement('tr');
            const tierBadge = idx < 3 ? '<span class="badge bg-primary">Tier 1 Flagship</span>' :
                              (idx < 8 ? '<span class="badge bg-light text-dark border">Tier 2 Core</span>' :
                                         '<span class="badge bg-warning text-dark">Tier 3 Developing</span>');

            tr.innerHTML = `
                <td class="fw-bold">#${idx + 1}</td>
                <td class="fw-bold text-dark">${s.store_name}</td>
                <td>${s.store_city}</td>
                <td><span class="badge bg-light text-dark border">${s.region}</span></td>
                <td class="text-center">${formatNumber(s.orders)}</td>
                <td class="text-center">${formatNumber(s.units)}</td>
                <td class="text-end fw-bold">${formatCurrency(s.revenue)}</td>
                <td class="text-end text-success fw-bold">${formatCurrency(s.profit)}</td>
                <td class="text-end">${formatCurrency(s.aov)}</td>
                <td class="text-end fw-semibold">${s.margin_pct}%</td>
                <td class="text-center">${tierBadge}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Failed loading store analytics:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadStoreAnalytics);
