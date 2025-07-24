/**
 * ERPNext v15 Purchase Invoice Customizations
 * Client-side enhancements for purchase invoice discount calculations
 */

frappe.ui.form.on('Purchase Invoice', {
    // Form initialization
    onload: function(frm) {
        // Add custom buttons
        add_custom_buttons(frm);
        
        // Set up field dependencies
        setup_field_dependencies(frm);
    },
    
    // Supplier selection
    supplier: function(frm) {
        if (frm.doc.supplier) {
            // Fetch supplier discounts
            fetch_supplier_discounts(frm);
            
            // Apply default invoice discount
            apply_default_invoice_discount(frm);
        }
    },
    
    // Apply discount checkbox
    apply_discount: function(frm) {
        if (frm.doc.apply_discount) {
            // Show discount fields
            frm.toggle_display(['discount_type', 'total_discount_amount', 'effective_discount_percentage'], true);
            
            // Apply discounts
            calculate_all_discounts(frm);
        } else {
            // Hide discount fields and reset values
            frm.toggle_display(['discount_type', 'total_discount_amount', 'effective_discount_percentage'], false);
            reset_discount_values(frm);
        }
    },
    
    // Discount type selection
    discount_type: function(frm) {
        if (frm.doc.apply_discount && frm.doc.discount_type) {
            calculate_all_discounts(frm);
        }
    },
    
    // Before save validation
    before_save: function(frm) {
        if (frm.doc.apply_discount) {
            calculate_all_discounts(frm);
        }
    }
});

// Item table events
frappe.ui.form.on('Purchase Invoice Item', {
    // Item selection
    item_code: function(frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        if (item.item_code && frm.doc.supplier && frm.doc.apply_discount) {
            // Apply item-specific discounts
            apply_item_discount(frm, item);
        }
    },
    
    // Quantity or rate change
    qty: function(frm, cdt, cdn) {
        calculate_item_totals(frm, cdt, cdn);
    },
    
    rate: function(frm, cdt, cdn) {
        calculate_item_totals(frm, cdt, cdn);
    }
});

// Custom functions
function add_custom_buttons(frm) {
    // Add button to refresh promotions
    frm.add_custom_button(__('Refresh Promotions'), function() {
        refresh_active_promotions(frm);
    }, __('Actions'));
    
    // Add button to show discount breakdown
    frm.add_custom_button(__('Discount Breakdown'), function() {
        show_discount_breakdown(frm);
    }, __('View'));
}

function setup_field_dependencies(frm) {
    // Set up field visibility based on conditions
    frm.toggle_display(['discount_type'], frm.doc.apply_discount);
    frm.toggle_display(['total_discount_amount', 'effective_discount_percentage'], 
                      frm.doc.apply_discount && frm.doc.total_discount_amount > 0);
}

function fetch_supplier_discounts(frm) {
    if (!frm.doc.supplier) return;
    
    frappe.call({
        method: 'cashiercounter.purchase.discount_calculations.get_supplier_discounts',
        args: {
            supplier: frm.doc.supplier
        },
        callback: function(r) {
            if (r.message) {
                frm._supplier_discounts = r.message;
                if (frm.doc.apply_discount) {
                    calculate_all_discounts(frm);
                }
            }
        }
    });
}

function apply_default_invoice_discount(frm) {
    if (!frm.doc.supplier) return;
    
    frappe.db.get_value('Supplier', frm.doc.supplier, 'default_invoice_discount').then(r => {
        if (r.message && r.message.default_invoice_discount) {
            frm.set_value('additional_discount_percentage', r.message.default_invoice_discount);
        }
    });
}

function calculate_all_discounts(frm) {
    if (!frm.doc.apply_discount) return;
    
    frappe.call({
        method: 'cashiercounter.purchase.discount_calculations.apply_discounts',
        args: {
            doc: frm.doc
        },
        callback: function(r) {
            if (r.message) {
                // Update the form with calculated values
                frm.refresh_fields();
                
                // Show success message
                frappe.show_alert({
                    message: __('Discounts calculated successfully'),
                    indicator: 'green'
                });
            }
        }
    });
}

function apply_item_discount(frm, item) {
    if (!frm._supplier_discounts) return;
    
    // Find applicable discount for this item
    let applicable_discount = frm._supplier_discounts.find(d => d.item_code === item.item_code);
    
    if (applicable_discount) {
        // Apply discount
        let discount_percentage = applicable_discount.discount_percentage;
        let discount_amount = (item.amount * discount_percentage) / 100;
        
        frappe.model.set_value(item.doctype, item.name, 'discount_percentage', discount_percentage);
        frappe.model.set_value(item.doctype, item.name, 'discount_amount', discount_amount);
        
        // Update rate
        let discounted_rate = item.rate - ((item.rate * discount_percentage) / 100);
        frappe.model.set_value(item.doctype, item.name, 'rate', discounted_rate);
    }
}

function calculate_item_totals(frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    
    // Calculate amount
    item.amount = flt(item.qty) * flt(item.rate);
    
    // Apply discount if applicable
    if (item.discount_percentage > 0) {
        item.discount_amount = (item.amount * item.discount_percentage) / 100;
        item.amount = item.amount - item.discount_amount;
    }
    
    refresh_field('amount', cdn, 'items');
    refresh_field('discount_amount', cdn, 'items');
    
    // Recalculate document totals
    frm.script_manager.trigger('calculate_taxes_and_totals');
}

function refresh_active_promotions(frm) {
    frappe.call({
        method: 'cashiercounter.purchase.discount_calculations.get_active_promotions',
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let promotion_list = r.message.map(p => 
                    `${p.promotion_name} (${p.discount_percentage}% discount)`
                ).join('<br>');
                
                frappe.msgprint({
                    title: __('Active Promotions'),
                    message: promotion_list,
                    indicator: 'blue'
                });
                
                // Reapply discounts with fresh promotion data
                if (frm.doc.apply_discount) {
                    calculate_all_discounts(frm);
                }
            } else {
                frappe.show_alert({
                    message: __('No active promotions found'),
                    indicator: 'orange'
                });
            }
        }
    });
}

function show_discount_breakdown(frm) {
    if (!frm.doc.total_discount_amount || frm.doc.total_discount_amount <= 0) {
        frappe.msgprint(__('No discounts applied to this invoice'));
        return;
    }
    
    let breakdown_html = '<table class="table table-bordered">';
    breakdown_html += '<tr><th>Discount Type</th><th>Amount</th></tr>';
    
    // Item-wise discounts
    if (frm.doc.discount_type === 'Item-wise') {
        frm.doc.items.forEach(item => {
            if (item.discount_amount > 0) {
                breakdown_html += `<tr>
                    <td>Item: ${item.item_code}</td>
                    <td>${format_currency(item.discount_amount)}</td>
                </tr>`;
            }
        });
    }
    
    // Invoice-wise discount
    if (frm.doc.additional_discount_amount > 0) {
        breakdown_html += `<tr>
            <td>Invoice Discount</td>
            <td>${format_currency(frm.doc.additional_discount_amount)}</td>
        </tr>`;
    }
    
    // Seasonal promotions and turnover incentives would be added here
    
    breakdown_html += `<tr class="active">
        <td><strong>Total Discount</strong></td>
        <td><strong>${format_currency(frm.doc.total_discount_amount)}</strong></td>
    </tr>`;
    breakdown_html += '</table>';
    
    frappe.msgprint({
        title: __('Discount Breakdown'),
        message: breakdown_html,
        indicator: 'blue'
    });
}

function reset_discount_values(frm) {
    // Reset document level discount fields
    frm.set_value('discount_type', '');
    frm.set_value('total_discount_amount', 0);
    frm.set_value('effective_discount_percentage', 0);
    
    // Reset item level discount fields
    frm.doc.items.forEach(item => {
        frappe.model.set_value(item.doctype, item.name, 'discount_percentage', 0);
        frappe.model.set_value(item.doctype, item.name, 'discount_amount', 0);
        frappe.model.set_value(item.doctype, item.name, 'promotion_applied', '');
    });
    
    frm.refresh_fields();
}