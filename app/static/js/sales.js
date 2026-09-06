/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/sales.js
 * Description: Sales analytics page charts, paginated ledger, live search, and export.
 */

let salesVolumeChart = null;
let salesChannelChart = null;
let currentPage = 1;
let totalPages = 1;
let searchQuery = "";
let searchDebounceTimer = null;

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

async function loadSalesKPIs() {
    try {
        const query = AppState.getQueryParams();
        const res = await fetch(`/api/dashboard/kpis?${query}`);
        const json = await res.json();
        if (json.success) {
            const d = json.data;
            document.getElementById('salesKpiRevenue').textContent = formatCurrency(d.total_revenue);
            document.getElementById('salesKpiProfit').textContent = formatCurrency(d.total_profit);
            document.getElementById('salesKpiOrders').textContent = formatNumber(d.total_orders);
            document.getElementById('salesKpiAOV').textContent = formatCurrency(d.average_order_value);
        }
    } catch (err) {
        console.error("Failed loading sales KPIs:", err);
    }
}

async function loadSalesCharts() {
    try {
        const query = AppState.getQueryParams();
        // Volume & Trend
        const res = await fetch(`/api/dashboard/revenue-trend?${query}`);
        const json = await res.json();
        if (json.success) {
            const labels = json.data.map(d => d.month_year);
            const orders = json.data.map(d => d.orders);
            const revenues = json.data.map(d => d.revenue);

            const ctx = document.getElementById('salesVolumeChart').getContext('2d');
            if (salesVolumeChart) salesVolumeChart.destroy();

            salesVolumeChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            type: 'bar',
                            label: 'Orders Count',
                            data: orders,
                            backgroundColor: '#93c5fd',
                            yAxisID: 'yOrders',
                            borderRadius: 4
                        },
                        {
                            type: 'line',
                            label: 'Revenue ($)',
                            data: revenues,
                            borderColor: '#1e40af',
                            backgroundColor: 'transparent',
                            yAxisID: 'yRevenue',
                            tension: 0.3,
                            borderWidth: 2.5,
                            pointRadius: 3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        yOrders: {
                            type: 'linear',
                            position: 'left',
                            beginAtZero: true,
                            grid: { display: false }
                        },
                        yRevenue: {
                            type: 'linear',
                            position: 'right',
                            beginAtZero: true,
                            ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // Channels
        const cRes = await fetch(`/api/dashboard/sales-channels?${query}`);
        const cJson = await cRes.json();
        if (cJson.success) {
            const ctxC = document.getElementById('salesChannelChart').getContext('2d');
            if (salesChannelChart) salesChannelChart.destroy();

            salesChannelChart = new Chart(ctxC, {
                type: 'doughnut',
                data: {
                    labels: cJson.data.map(d => d.sales_channel),
                    datasets: [{
                        data: cJson.data.map(d => d.revenue),
                        backgroundColor: ['#0d9488', '#f59e0b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: { label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.parsed)}` }
                        }
                    },
                    cutout: '65%'
                }
            });
        }
    } catch (err) {
        console.error("Failed loading sales charts:", err);
    }
}

async function loadTransactionsTable(page = 1) {
    try {
        currentPage = page;
        const queryParams = AppState.getQueryParams();
        const searchParam = searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : '';
        const url = `/api/sales/transactions?page=${page}&per_page=15&${queryParams}${searchParam}`;

        const res = await fetch(url);
        const json = await res.json();
        if (!json.success) return;

        const d = json.data;
        totalPages = d.total_pages;

        const tbody = document.getElementById('transactionsTableBody');
        tbody.innerHTML = '';

        if (d.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted py-4">No matching sales records found.</td></tr>';
        } else {
            d.records.forEach(r => {
                const tr = document.createElement('tr');
                const chBadge = r.sales_channel === 'In-Store' ? 'badge-instore' : 'badge-online';
                tr.innerHTML = `
                    <td class="fw-bold text-dark">#${r.sale_id}</td>
                    <td>${r.sale_date}</td>
                    <td><div class="fw-semibold">${r.customer_name}</div><div class="text-muted small">${r.customer_segment}</div></td>
                    <td>${r.store_name}</td>
                    <td><div class="fw-semibold text-truncate" style="max-width: 220px;" title="${r.product_name}">${r.product_name}</div><div class="text-muted small">${r.category_name}</div></td>
                    <td><span class="badge-segment ${chBadge}">${r.sales_channel}</span></td>
                    <td class="text-center fw-bold">${r.quantity}</td>
                    <td class="text-end fw-bold">${formatCurrency(r.line_revenue)}</td>
                    <td class="text-end text-success fw-bold">${formatCurrency(r.line_profit)}</td>
                    <td class="text-end">${r.profit_margin_pct}%</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Update pagination UI
        const startRecord = (d.page - 1) * d.per_page + (d.records.length > 0 ? 1 : 0);
        const endRecord = (d.page - 1) * d.per_page + d.records.length;
        document.getElementById('paginationInfo').textContent =
            `Showing ${formatNumber(startRecord)} to ${formatNumber(endRecord)} of ${formatNumber(d.total_records)} line items`;

        document.getElementById('currentPageDisplay').textContent = d.page;
        document.getElementById('prevPageBtn').disabled = d.page <= 1;
        document.getElementById('nextPageBtn').disabled = d.page >= d.total_pages;
    } catch (err) {
        console.error("Failed loading transactions:", err);
    }
}

// Export Table Data to CSV
function exportTransactionsCSV() {
    const table = document.getElementById('transactionsTable');
    let csv = [];
    for (let row of table.rows) {
        let cols = [];
        for (let cell of row.cells) {
            cols.push(`"${cell.innerText.replace(/"/g, '""').replace(/\n/g, ' ')}"`);
        }
        csv.push(cols.join(','));
    }
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `InsightMart_Transactions_Page_${currentPage}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Event Listeners
document.getElementById('prevPageBtn')?.addEventListener('click', () => {
    if (currentPage > 1) loadTransactionsTable(currentPage - 1);
});

document.getElementById('nextPageBtn')?.addEventListener('click', () => {
    if (currentPage < totalPages) loadTransactionsTable(currentPage + 1);
});

document.getElementById('transactionSearchInput')?.addEventListener('input', (e) => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        searchQuery = e.target.value.trim();
        loadTransactionsTable(1);
    }, 350);
});

document.getElementById('exportCsvBtn')?.addEventListener('click', exportTransactionsCSV);

function refreshSalesView() {
    loadSalesKPIs();
    loadSalesCharts();
    loadTransactionsTable(1);
}

document.addEventListener('DOMContentLoaded', () => {
    refreshSalesView();
});

window.addEventListener('filtersUpdated', () => {
    refreshSalesView();
});
