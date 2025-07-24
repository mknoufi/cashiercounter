frappe.pages['purchase-analytics'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Purchase Analytics Dashboard',
        single_column: true
    });

    // Add refresh button
    page.set_primary_action('Refresh', function() {
        load_analytics(page);
    }, 'fa fa-refresh');

    // Load initial data
    load_analytics(page);
};

function load_analytics(page) {
    // Clear existing content
    $(page.body).empty();

    // Create dashboard layout
    let dashboard_html = `
        <div class="row">
            <div class="col-sm-12">
                <h3>Purchase Analytics Dashboard</h3>
                <hr>
            </div>
        </div>
        
        <div class="row">
            <div class="col-sm-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h4 class="card-title">Monthly Purchase</h4>
                        <h2 class="text-primary" id="monthly-purchase">Loading...</h2>
                        <p class="card-text">This Month</p>
                    </div>
                </div>
            </div>
            
            <div class="col-sm-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h4 class="card-title">Total Discounts</h4>
                        <h2 class="text-success" id="total-discounts">Loading...</h2>
                        <p class="card-text">This Month</p>
                    </div>
                </div>
            </div>
            
            <div class="col-sm-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h4 class="card-title">Active Promotions</h4>
                        <h2 class="text-info" id="active-promotions">Loading...</h2>
                        <p class="card-text">Currently Running</p>
                    </div>
                </div>
            </div>
            
            <div class="col-sm-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h4 class="card-title">Avg Discount %</h4>
                        <h2 class="text-warning" id="avg-discount">Loading...</h2>
                        <p class="card-text">This Month</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-sm-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Top Suppliers by Volume</h5>
                    </div>
                    <div class="card-body">
                        <div id="top-suppliers">Loading...</div>
                    </div>
                </div>
            </div>
            
            <div class="col-sm-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Discount Distribution</h5>
                    </div>
                    <div class="card-body">
                        <div id="discount-distribution">Loading...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-sm-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Purchase Estimates</h5>
                    </div>
                    <div class="card-body">
                        <div id="recent-estimates">Loading...</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    $(page.body).html(dashboard_html);

    // Load dashboard data
    load_dashboard_data();
}

function load_dashboard_data() {
    // Load purchase analytics
    frappe.call({
        method: 'cashiercounter.purchase.tasks.get_purchase_analytics',
        callback: function(r) {
            if (r.message) {
                update_dashboard_metrics(r.message);
            }
        }
    });

    // Load recent estimates
    load_recent_estimates();
}

function update_dashboard_metrics(data) {
    // Update monthly purchase
    let monthly_data = data.monthly_purchase || {};
    $('#monthly-purchase').text(format_currency(monthly_data.total_amount || 0));

    // Update active promotions count
    $('#active-promotions').text(data.active_promotions || 0);

    // Calculate and display discount metrics
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Purchase Invoice',
            filters: {
                posting_date: ['>=', frappe.datetime.month_start()],
                docstatus: 1
            },
            fields: ['total_discount_amount', 'effective_discount_percentage', 'total']
        },
        callback: function(r) {
            if (r.message) {
                let total_discount = 0;
                let total_percentage = 0;
                let count = 0;

                r.message.forEach(function(invoice) {
                    if (invoice.total_discount_amount) {
                        total_discount += invoice.total_discount_amount;
                        total_percentage += invoice.effective_discount_percentage || 0;
                        count++;
                    }
                });

                $('#total-discounts').text(format_currency(total_discount));
                $('#avg-discount').text((count > 0 ? (total_percentage / count).toFixed(2) : 0) + '%');
            }
        }
    });

    // Update top suppliers
    if (data.top_suppliers) {
        let suppliers_html = '<table class="table table-sm">';
        suppliers_html += '<thead><tr><th>Supplier</th><th>Amount</th><th>Invoices</th></tr></thead><tbody>';
        
        data.top_suppliers.slice(0, 5).forEach(function(supplier) {
            suppliers_html += `<tr>
                <td>${supplier.supplier}</td>
                <td>${format_currency(supplier.total_amount)}</td>
                <td>${supplier.invoice_count}</td>
            </tr>`;
        });
        
        suppliers_html += '</tbody></table>';
        $('#top-suppliers').html(suppliers_html);
    }
}

function load_recent_estimates() {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Purchase Estimate',
            fields: ['name', 'supplier', 'posting_date', 'grand_total', 'status'],
            order_by: 'creation desc',
            limit_start: 0,
            limit_page_length: 10
        },
        callback: function(r) {
            if (r.message) {
                let estimates_html = '<table class="table table-sm">';
                estimates_html += '<thead><tr><th>Estimate</th><th>Supplier</th><th>Date</th><th>Amount</th><th>Status</th></tr></thead><tbody>';
                
                r.message.forEach(function(estimate) {
                    estimates_html += `<tr>
                        <td><a href="/app/purchase-estimate/${estimate.name}">${estimate.name}</a></td>
                        <td>${estimate.supplier}</td>
                        <td>${frappe.datetime.str_to_user(estimate.posting_date)}</td>
                        <td>${format_currency(estimate.grand_total)}</td>
                        <td><span class="badge badge-${get_status_color(estimate.status)}">${estimate.status}</span></td>
                    </tr>`;
                });
                
                estimates_html += '</tbody></table>';
                $('#recent-estimates').html(estimates_html);
            }
        }
    });
}

function get_status_color(status) {
    const colors = {
        'Draft': 'secondary',
        'Submitted': 'primary', 
        'Converted': 'success',
        'Cancelled': 'danger'
    };
    return colors[status] || 'secondary';
}

function format_currency(amount) {
    return frappe.format(amount, {fieldtype: 'Currency'});
}