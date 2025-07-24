/**
 * ERPNext v15 Purchase Estimate Customizations
 * Client-side enhancements for purchase estimate management
 */

frappe.ui.form.on('Purchase Estimate', {
    // Form initialization
    onload: function(frm) {
        // Add custom buttons
        add_estimate_buttons(frm);
        
        // Set up field dependencies
        setup_estimate_dependencies(frm);
    },
    
    // Refresh event
    refresh: function(frm) {
        // Update button visibility based on status
        update_button_visibility(frm);
        
        // Set form title
        if (frm.doc.supplier_name) {
            frm.set_title(`Purchase Estimate from ${frm.doc.supplier_name}`);
        }
    },
    
    // Supplier selection
    supplier: function(frm) {
        if (frm.doc.supplier) {
            // Fetch supplier details
            fetch_supplier_details(frm);
            
            // Apply discount settings
            if (frm.doc.apply_discount) {
                calculate_estimate_discounts(frm);
            }
        }
    },
    
    // Apply discount checkbox
    apply_discount: function(frm) {
        if (frm.doc.apply_discount) {
            frm.toggle_display(['discount_type', 'total_discount_amount', 'effective_discount_percentage'], true);
            calculate_estimate_discounts(frm);
        } else {
            frm.toggle_display(['discount_type', 'total_discount_amount', 'effective_discount_percentage'], false);
            reset_estimate_discounts(frm);
        }
    },
    
    // Discount type change
    discount_type: function(frm) {
        if (frm.doc.apply_discount && frm.doc.discount_type) {
            calculate_estimate_discounts(frm);
        }
    },
    
    // Before save
    before_save: function(frm) {
        calculate_estimate_totals(frm);
        
        if (frm.doc.apply_discount) {
            calculate_estimate_discounts(frm);
        }
    },
    
    // After save
    after_save: function(frm) {
        // Update button visibility
        update_button_visibility(frm);
    }
});

// Item table events
frappe.ui.form.on('Purchase Estimate Item', {
    // Item selection
    item_code: function(frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        if (item.item_code) {
            // Fetch item details
            fetch_item_details(frm, item);
            
            // Apply discounts if enabled
            if (frm.doc.apply_discount && frm.doc.supplier) {
                apply_estimate_item_discount(frm, item);
            }
        }
    },
    
    // Quantity change
    qty: function(frm, cdt, cdn) {
        calculate_estimate_item_totals(frm, cdt, cdn);
    },
    
    // Rate change
    rate: function(frm, cdt, cdn) {
        calculate_estimate_item_totals(frm, cdt, cdn);
    },
    
    // Item removal
    items_remove: function(frm) {
        calculate_estimate_totals(frm);
    }
});

// Custom functions for Purchase Estimate
function add_estimate_buttons(frm) {
    // Convert to Invoice button
    if (frm.doc.docstatus === 1 && frm.doc.status !== 'Converted') {
        frm.add_custom_button(__('Convert to Invoice'), function() {
            convert_to_purchase_invoice(frm);
        }).addClass('btn-primary');
    }
    
    // Copy Estimate button
    if (frm.doc.name) {
        frm.add_custom_button(__('Copy Estimate'), function() {
            copy_estimate(frm);
        }, __('Actions'));
    }
    
    // Get Quotations button
    frm.add_custom_button(__('Get Quotations'), function() {
        get_supplier_quotations(frm);
    }, __('Actions'));
    
    // Print Preview button
    frm.add_custom_button(__('Print Preview'), function() {
        show_print_preview(frm);
    }, __('View'));
}

function setup_estimate_dependencies(frm) {
    // Field visibility setup
    frm.toggle_display(['discount_type'], frm.doc.apply_discount);
    frm.toggle_display(['total_discount_amount', 'effective_discount_percentage'], 
                      frm.doc.apply_discount && frm.doc.total_discount_amount > 0);
    
    // Set required by date default
    if (!frm.doc.required_by) {
        let required_date = frappe.datetime.add_days(frappe.datetime.get_today(), 7);
        frm.set_value('required_by', required_date);
    }
}

function update_button_visibility(frm) {
    // Show/hide buttons based on document status
    frm.remove_custom_button('Convert to Invoice');
    
    if (frm.doc.docstatus === 1 && frm.doc.status !== 'Converted') {
        frm.add_custom_button(__('Convert to Invoice'), function() {
            convert_to_purchase_invoice(frm);
        }).addClass('btn-primary');
    }
}

function fetch_supplier_details(frm) {
    if (!frm.doc.supplier) return;
    
    frappe.db.get_doc('Supplier', frm.doc.supplier).then(supplier => {
        // Set supplier-specific terms if available
        if (supplier.default_payment_terms_template) {
            frm.set_value('payment_terms_template', supplier.default_payment_terms_template);
        }
        
        // Set default currency
        if (supplier.default_currency) {
            frm.set_value('currency', supplier.default_currency);
        }
    });
}

function calculate_estimate_discounts(frm) {
    if (!frm.doc.apply_discount) return;
    
    frappe.call({
        method: 'cashiercounter.purchase.discount_calculations.apply_discounts',
        args: {
            doc: frm.doc
        },
        callback: function(r) {
            if (r.message) {
                frm.refresh_fields();
                frappe.show_alert({
                    message: __('Estimate discounts calculated'),
                    indicator: 'green'
                });
            }
        }
    });
}

function apply_estimate_item_discount(frm, item) {
    // Apply item-specific discounts similar to purchase invoice
    if (frm._supplier_discounts) {
        let applicable_discount = frm._supplier_discounts.find(d => d.item_code === item.item_code);
        
        if (applicable_discount) {
            let discount_percentage = applicable_discount.discount_percentage;
            let discount_amount = (item.amount * discount_percentage) / 100;
            
            frappe.model.set_value(item.doctype, item.name, 'discount_percentage', discount_percentage);
            frappe.model.set_value(item.doctype, item.name, 'discount_amount', discount_amount);
        }
    }
}

function calculate_estimate_item_totals(frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    
    // Calculate basic amount
    item.amount = flt(item.qty) * flt(item.rate);
    
    // Apply discount if applicable
    if (item.discount_percentage > 0) {
        item.discount_amount = (item.amount * item.discount_percentage) / 100;
    }
    
    refresh_field('amount', cdn, 'items');
    refresh_field('discount_amount', cdn, 'items');
    
    // Recalculate totals
    calculate_estimate_totals(frm);
}

function calculate_estimate_totals(frm) {
    let total_qty = 0;
    let total_amount = 0;
    
    // Calculate item totals
    frm.doc.items.forEach(item => {
        if (item.qty && item.rate) {
            item.amount = flt(item.qty) * flt(item.rate);
            if (item.discount_amount) {
                item.amount -= flt(item.discount_amount);
            }
            total_qty += flt(item.qty);
            total_amount += flt(item.amount);
        }
    });
    
    // Update document totals
    frm.set_value('total_qty', total_qty);
    frm.set_value('total', total_amount);
    
    // Calculate grand total after discounts
    let grand_total = total_amount - flt(frm.doc.total_discount_amount);
    frm.set_value('grand_total', grand_total);
}

function convert_to_purchase_invoice(frm) {
    if (frm.doc.status === 'Converted') {
        frappe.msgprint(__('This estimate has already been converted to an invoice'));
        return;
    }
    
    frappe.confirm(
        __('Are you sure you want to convert this estimate to a Purchase Invoice?'),
        function() {
            frappe.call({
                method: 'convert_to_invoice',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Purchase Invoice {0} has been created successfully', [r.message]),
                            indicator: 'green'
                        });
                        
                        // Refresh form to show updated status
                        frm.reload_doc();
                        
                        // Optionally open the new invoice
                        frappe.set_route('Form', 'Purchase Invoice', r.message);
                    }
                }
            });
        }
    );
}

function copy_estimate(frm) {
    frappe.new_doc('Purchase Estimate', {
        supplier: frm.doc.supplier,
        required_by: frappe.datetime.add_days(frappe.datetime.get_today(), 7),
        apply_discount: frm.doc.apply_discount,
        discount_type: frm.doc.discount_type,
        terms_and_conditions: frm.doc.terms_and_conditions
    });
}

function get_supplier_quotations(frm) {
    if (!frm.doc.items || frm.doc.items.length === 0) {
        frappe.msgprint(__('Please add items to the estimate first'));
        return;
    }
    
    // Create supplier quotation request
    frappe.new_doc('Request for Quotation', {
        transaction_date: frappe.datetime.get_today(),
        required_by: frm.doc.required_by,
        message_for_supplier: `Quotation request based on Purchase Estimate ${frm.doc.name}`,
        items: frm.doc.items.map(item => ({
            item_code: item.item_code,
            qty: item.qty,
            description: item.description,
            uom: item.uom
        }))
    });
}

function show_print_preview(frm) {
    if (!frm.doc.name) {
        frappe.msgprint(__('Please save the estimate first'));
        return;
    }
    
    // Open print preview
    frappe.print_preview({
        doctype: frm.doc.doctype,
        name: frm.doc.name,
        print_format: 'Standard'
    });
}

function fetch_item_details(frm, item) {
    if (!item.item_code) return;
    
    frappe.db.get_doc('Item', item.item_code).then(item_doc => {
        // Set item name and description
        frappe.model.set_value(item.doctype, item.name, 'item_name', item_doc.item_name);
        frappe.model.set_value(item.doctype, item.name, 'description', item_doc.description);
        frappe.model.set_value(item.doctype, item.name, 'uom', item_doc.stock_uom);
        
        // Set standard rate if available
        if (item_doc.standard_rate && !item.rate) {
            frappe.model.set_value(item.doctype, item.name, 'rate', item_doc.standard_rate);
        }
    });
}

function reset_estimate_discounts(frm) {
    // Reset all discount-related fields
    frm.set_value('discount_type', '');
    frm.set_value('total_discount_amount', 0);
    frm.set_value('effective_discount_percentage', 0);
    
    // Reset item-level discounts
    frm.doc.items.forEach(item => {
        frappe.model.set_value(item.doctype, item.name, 'discount_percentage', 0);
        frappe.model.set_value(item.doctype, item.name, 'discount_amount', 0);
        frappe.model.set_value(item.doctype, item.name, 'promotion_applied', '');
    });
    
    // Recalculate totals
    calculate_estimate_totals(frm);
    frm.refresh_fields();
}