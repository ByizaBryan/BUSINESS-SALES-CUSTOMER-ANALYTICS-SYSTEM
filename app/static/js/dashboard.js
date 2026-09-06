/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/dashboard.js
 * Description: Interactive Dashboard visualization logic and dynamic cross-filtering.
 */

let revenueTrendChart = null;
let categoryChart = null;
let topProductsChart = null;
let storePerformanceChart = null;
let channelChart = null;
let paymentChart = null;

// Currency Formatter
const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

async function loadKPIs(filters) {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/dashboard/kpis?${query}`);
        const json = await res.json();
        if (json.success) {
            const d = json.data;
            document.getElementById('kpiRevenue').textContent = formatCurrency(d.total_revenue);
            document.getElementById('kpiProfit').textContent = formatCurrency(d.total_profit);
            document.getElementById('kpiMargin').textContent = `${d.profit_margin_pct}%`;
            document.getElementById('kpiOrders').textContent = formatNumber(d.total_orders);
            document.getElementById('kpiUnits').textContent = formatNumber(d.total_units_sold);
            document.getElementById('kpiAOV').textContent = formatCurrency(d.average_order_value);
        }
    } catch (err) {
        console.error("Failed loading KPIs:", err);
    }
}

async function loadRevenueTrendChart() {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/dashboard/revenue-trend?${query}`);
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const labels = data.map(d => d.month_year);
        const revenues = data.map(d => d.revenue);
        const profits = data.map(d => d.profit);

        const ctx = document.getElementById('revenueTrendChart').getContext('2d');
        if (revenueTrendChart) revenueTrendChart.destroy();

        revenueTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Gross Revenue',
                        data: revenues,
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Gross Profit',
                        data: profits,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, font: { weight: 600 } } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (v) => `$${(v / 1000).toFixed(0)}k`
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (err) {
        console.error("Failed loading revenue trend chart:", err);
    }
}

async function loadCategoryChart() {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/dashboard/category-performance?${query}`);
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const labels = data.map(d => d.category_name);
        const revenues = data.map(d => d.revenue);

        const ctx = document.getElementById('categoryChart').getContext('2d');
        if (categoryChart) categoryChart.destroy();

        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: revenues,
                    backgroundColor: [
                        '#2563eb', '#0d9488', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'
                    ],
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`
                        }
                    }
                },
                cutout: '68%'
            }
        });
    } catch (err) {
        console.error("Failed loading category chart:", err);
    }
}

async function loadTopProductsChart() {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/products/top?limit=8&${query}`);
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        // Truncate long product names for chart display
        const labels = data.map(d => d.product_name.length > 25 ? d.product_name.substring(0, 25) + '...' : d.product_name);
        const revenues = data.map(d => d.revenue);

        const ctx = document.getElementById('topProductsChart').getContext('2d');
        if (topProductsChart) topProductsChart.destroy();

        topProductsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue ($)',
                    data: revenues,
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: (items) => data[items[0].dataIndex].product_name,
                            label: (ctx) => `Revenue: ${formatCurrency(ctx.parsed.x)}`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    } catch (err) {
        console.error("Failed loading top products chart:", err);
    }
}

async function loadStorePerformanceChart() {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/dashboard/store-performance?${query}`);
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const labels = data.map(d => d.store_city);
        const revenues = data.map(d => d.revenue);

        const ctx = document.getElementById('storePerformanceChart').getContext('2d');
        if (storePerformanceChart) storePerformanceChart.destroy();

        storePerformanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Store Revenue',
                    data: revenues,
                    backgroundColor: '#0d9488',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Revenue: ${formatCurrency(ctx.parsed.y)}`
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (err) {
        console.error("Failed loading store performance chart:", err);
    }
}

async function loadChannelAndPaymentCharts() {
    try {
        const query = AppState.getQueryParams();
        // Channels
        const cRes = await fetch(`/api/dashboard/sales-channels?${query}`);
        const cJson = await cRes.json();
        if (cJson.success) {
            const ctx = document.getElementById('channelChart').getContext('2d');
            if (channelChart) channelChart.destroy();
            channelChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: cJson.data.map(d => d.sales_channel),
                    datasets: [{
                        data: cJson.data.map(d => d.revenue),
                        backgroundColor: ['#10b981', '#f97316'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`
                            }
                        }
                    }
                }
            });
        }

        // Payments
        const pRes = await fetch(`/api/dashboard/payment-methods?${query}`);
        const pJson = await pRes.json();
        if (pJson.success) {
            const ctx = document.getElementById('paymentChart').getContext('2d');
            if (paymentChart) paymentChart.destroy();
            paymentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: pJson.data.map(d => d.payment_method),
                    datasets: [{
                        data: pJson.data.map(d => d.revenue),
                        backgroundColor: ['#2563eb', '#38bdf8', '#a855f7', '#64748b'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { boxWidth: 10, font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}`
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }
    } catch (err) {
        console.error("Failed loading channel/payment charts:", err);
    }
}

async function loadTopCustomersTable() {
    try {
        const res = await fetch('/api/customers/top?limit=7');
        const json = await res.json();
        if (!json.success) return;

        const tbody = document.getElementById('topCustomersTableBody');
        tbody.innerHTML = '';

        json.data.forEach(c => {
            const tr = document.createElement('tr');
            const segClass = c.customer_segment.includes('High') ? 'badge-high' :
                             (c.customer_segment.includes('Medium') ? 'badge-medium' : 'badge-low');

            tr.innerHTML = `
                <td class="fw-bold text-dark">${c.customer_name}</td>
                <td><span class="badge-segment ${segClass}">${c.customer_segment}</span></td>
                <td>${c.customer_city}</td>
                <td class="text-center fw-bold">${c.orders}</td>
                <td class="text-end fw-bold text-primary">${formatCurrency(c.total_spent)}</td>
                <td class="text-end">${formatCurrency(c.aov)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed loading top customers table:", err);
    }
}

function refreshDashboard() {
    loadKPIs();
    loadRevenueTrendChart();
    loadCategoryChart();
    loadTopProductsChart();
    loadStorePerformanceChart();
    loadChannelAndPaymentCharts();
    loadTopCustomersTable();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    refreshDashboard();
});

window.addEventListener('filtersUpdated', () => {
    refreshDashboard();
});
