/**
 * InsightMart Business Sales & Customer Analytics System
 * File: app/static/js/customers.js
 * Description: Customer analytics page logic, segment distributions, and top spenders.
 */

let customerSegmentsDonutChart = null;
let segmentRevenueBarChart = null;

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatNumber = (val) => new Intl.NumberFormat('en-US').format(val);

async function loadCustomerSegments() {
    try {
        const res = await fetch('/api/customers/segments');
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        const labels = data.map(d => d.customer_segment);
        const counts = data.map(d => d.customer_count);
        const revenues = data.map(d => d.total_revenue);

        // 1. Donut Chart
        const ctxD = document.getElementById('customerSegmentsDonutChart').getContext('2d');
        if (customerSegmentsDonutChart) customerSegmentsDonutChart.destroy();

        customerSegmentsDonutChart = new Chart(ctxD, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: ['#ef4444', '#3b82f6', '#64748b'],
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
                            label: (ctx) => ` ${ctx.label}: ${formatNumber(ctx.parsed)} customers`
                        }
                    }
                },
                cutout: '65%'
            }
        });

        // 2. Revenue Contribution Bar Chart
        const ctxB = document.getElementById('segmentRevenueBarChart').getContext('2d');
        if (segmentRevenueBarChart) segmentRevenueBarChart.destroy();

        segmentRevenueBarChart = new Chart(ctxB, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue ($)',
                    data: revenues,
                    backgroundColor: ['#ef4444', '#3b82f6', '#64748b'],
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
                            label: (ctx) => `Total Revenue: ${formatCurrency(ctx.parsed.y)}`
                        }
                    }
                },
                scales: {
                    y: { ticks: { callback: (v) => `$${(v / 1000).toFixed(0)}k` } },
                    x: { grid: { display: false } }
                }
            }
        });

        // 3. Populate Segment Summary Table
        const tbody = document.getElementById('segmentSummaryTableBody');
        tbody.innerHTML = '';
        data.forEach(s => {
            const tr = document.createElement('tr');
            const segBadge = s.customer_segment.includes('High') ? 'badge-high' :
                             (s.customer_segment.includes('Medium') ? 'badge-medium' : 'badge-low');

            tr.innerHTML = `
                <td><span class="badge-segment ${segBadge}">${s.customer_segment}</span></td>
                <td class="text-center fw-bold">${formatNumber(s.customer_count)}</td>
                <td class="text-center fw-semibold">${formatNumber(s.total_orders)}</td>
                <td class="text-end fw-bold">${formatCurrency(s.total_revenue)}</td>
                <td class="text-end text-success fw-bold">${formatCurrency(s.total_profit)}</td>
                <td class="text-end fw-bold text-primary">${formatCurrency(s.revenue_per_customer)}</td>
                <td class="text-end">${formatCurrency(s.aov)}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Failed loading customer segments:", err);
    }
}

async function loadTopCustomersDetailed() {
    try {
        const res = await fetch('/api/customers/top?limit=15');
        const json = await res.json();
        if (!json.success) return;

        const tbody = document.getElementById('topCustomersDetailedTableBody');
        tbody.innerHTML = '';

        json.data.forEach((c, idx) => {
            const tr = document.createElement('tr');
            const segBadge = c.customer_segment.includes('High') ? 'badge-high' :
                             (c.customer_segment.includes('Medium') ? 'badge-medium' : 'badge-low');

            const rankBadge = idx < 3 ? `<span class="badge bg-warning text-dark"><i class="fa-solid fa-crown me-1"></i>#${idx + 1}</span>` :
                                        `<span class="badge bg-light text-dark border">#${idx + 1}</span>`;

            tr.innerHTML = `
                <td>${rankBadge}</td>
                <td class="fw-bold text-dark">${c.customer_name}</td>
                <td><span class="badge-segment ${segBadge}">${c.customer_segment}</span></td>
                <td>${c.customer_city}</td>
                <td class="text-center fw-bold">${c.orders}</td>
                <td class="text-center">${formatNumber(c.units)}</td>
                <td class="text-end fw-bold text-primary">${formatCurrency(c.total_spent)}</td>
                <td class="text-end text-success fw-bold">${formatCurrency(c.profit_contributed)}</td>
                <td class="text-end">${formatCurrency(c.aov)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed loading detailed customers:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadCustomerSegments();
    loadTopCustomersDetailed();
});
