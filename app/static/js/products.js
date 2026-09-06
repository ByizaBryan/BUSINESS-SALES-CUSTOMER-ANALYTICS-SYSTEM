/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/products.js
 * Description: Product analytics page charts, catalog matrix, sorting, and inventory flags.
 */

let topProductsBarChart = null;
let underperformingBarChart = null;
let catalogData = [];

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

async function loadProductCharts() {
    try {
        const query = AppState.getQueryParams();

        // 1. Top Products
        const topRes = await fetch(`/api/products/top?limit=10&${query}`);
        const topJson = await topRes.json();
        if (topJson.success) {
            const labels = topJson.data.map(d => d.product_name.length > 22 ? d.product_name.substring(0, 22) + '...' : d.product_name);
            const ctx = document.getElementById('topProductsBarChart').getContext('2d');
            if (topProductsBarChart) topProductsBarChart.destroy();

            topProductsBarChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Gross Revenue ($)',
                        data: topJson.data.map(d => d.revenue),
                        backgroundColor: '#2563eb',
                        borderRadius: 4
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
                                title: (items) => topJson.data[items[0].dataIndex].product_name,
                                label: (ctx) => `Revenue: ${formatCurrency(ctx.parsed.x)} (Margin: ${topJson.data[ctx.dataIndex].margin_pct}%)`
                            }
                        }
                    },
                    scales: {
                        x: { ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` } },
                        y: { grid: { display: false } }
                    }
                }
            });
        }

        // 2. Underperforming Products
        const underRes = await fetch(`/api/products/underperforming?limit=10&${query}`);
        const underJson = await underRes.json();
        if (underJson.success) {
            const labels = underJson.data.map(d => d.product_name.length > 22 ? d.product_name.substring(0, 22) + '...' : d.product_name);
            const ctxU = document.getElementById('underperformingBarChart').getContext('2d');
            if (underperformingBarChart) underperformingBarChart.destroy();

            underperformingBarChart = new Chart(ctxU, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Revenue ($)',
                        data: underJson.data.map(d => d.revenue),
                        backgroundColor: '#f59e0b',
                        borderRadius: 4
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
                                title: (items) => underJson.data[items[0].dataIndex].product_name,
                                label: (ctx) => `Revenue: ${formatCurrency(ctx.parsed.x)} | Profit: ${formatCurrency(underJson.data[ctx.dataIndex].profit)}`
                            }
                        }
                    },
                    scales: {
                        x: { ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` } },
                        y: { grid: { display: false } }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Failed loading product charts:", err);
    }
}

async function loadCatalogTable() {
    try {
        const res = await fetch('/api/products/catalog');
        const json = await res.json();
        if (!json.success) return;

        catalogData = json.data;
        renderCatalogTable();
    } catch (err) {
        console.error("Failed loading catalog table:", err);
    }
}

function renderCatalogTable() {
    const search = document.getElementById('catalogSearchInput').value.toLowerCase().trim();
    const sortMode = document.getElementById('catalogSortSelect').value;

    let filtered = catalogData.filter(p => {
        return p.product_name.toLowerCase().includes(search) ||
               p.category_name.toLowerCase().includes(search) ||
               p.supplier_name.toLowerCase().includes(search);
    });

    // Sort
    if (sortMode === 'rev_desc') {
        filtered.sort((a, b) => b.total_revenue - a.total_revenue);
    } else if (sortMode === 'margin_desc') {
        filtered.sort((a, b) => b.margin_pct - a.margin_pct);
    } else if (sortMode === 'profit_desc') {
        filtered.sort((a, b) => b.total_profit - a.total_profit);
    } else if (sortMode === 'units_desc') {
        filtered.sort((a, b) => b.units_sold - a.units_sold);
    } else if (sortMode === 'stock_asc') {
        filtered.sort((a, b) => a.stock_quantity - b.stock_quantity);
    }

    const tbody = document.getElementById('catalogTableBody');
    tbody.innerHTML = '';

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center text-muted py-4">No matching products found.</td></tr>';
        return;
    }

    filtered.forEach(p => {
        const tr = document.createElement('tr');
        const isLowStock = p.stock_quantity <= p.reorder_level;
        const stockBadge = isLowStock ? '<span class="badge bg-danger">Reorder</span>' :
                           (p.stock_quantity < 50 ? '<span class="badge bg-warning text-dark">Low</span>' : '<span class="badge bg-light text-dark">Adequate</span>');

        const marginColor = p.margin_pct >= 55 ? 'text-success fw-bold' :
                           (p.margin_pct >= 35 ? 'text-primary fw-bold' : 'text-warning fw-bold');

        tr.innerHTML = `
            <td><div class="fw-bold text-dark">${p.product_name}</div></td>
            <td><span class="badge bg-light text-dark border">${p.category_name}</span></td>
            <td class="text-muted small">${p.supplier_name}</td>
            <td class="text-end">${formatCurrency(p.unit_cost)}</td>
            <td class="text-end fw-semibold">${formatCurrency(p.selling_price)}</td>
            <td class="text-center">${p.stock_quantity} ${stockBadge}</td>
            <td class="text-center fw-bold">${formatNumber(p.units_sold)}</td>
            <td class="text-end fw-bold">${formatCurrency(p.total_revenue)}</td>
            <td class="text-end text-success fw-bold">${formatCurrency(p.total_profit)}</td>
            <td class="text-end ${marginColor}">${p.margin_pct}%</td>
            <td class="text-center"><span class="badge ${p.status === 'Active' ? 'bg-success' : 'bg-secondary'}">${p.status}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

document.getElementById('catalogSearchInput')?.addEventListener('input', renderCatalogTable);
document.getElementById('catalogSortSelect')?.addEventListener('change', renderCatalogTable);

function refreshProductsView() {
    loadProductCharts();
    loadCatalogTable();
}

document.addEventListener('DOMContentLoaded', refreshProductsView);
window.addEventListener('filtersUpdated', refreshProductsView);
