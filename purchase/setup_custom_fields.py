"""
Custom Fields for Purchase Customizations
Adds fields to standard ERPNext doctypes to support discount functionality
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Create custom fields for purchase customizations"""
    
    # Custom fields for Purchase Invoice
    purchase_invoice_fields = {
        "Purchase Invoice": [
            {
                "fieldname": "purchase_type",
                "label": "Purchase Type",
                "fieldtype": "Select",
                "options": "Purchase Invoice\nPurchase Estimate",
                "default": "Purchase Invoice",
                "insert_after": "title",
                "reqd": 1
            },
            {
                "fieldname": "apply_discount",
                "label": "Apply Discount",
                "fieldtype": "Check",
                "default": 0,
                "insert_after": "purchase_type"
            },
            {
                "fieldname": "discount_type",
                "label": "Discount Type",
                "fieldtype": "Select",
                "options": "\nItem-wise\nInvoice-wise",
                "depends_on": "apply_discount",
                "insert_after": "apply_discount"
            },
            {
                "fieldname": "total_discount_amount",
                "label": "Total Discount Amount",
                "fieldtype": "Currency",
                "read_only": 1,
                "depends_on": "apply_discount",
                "insert_after": "discount_type"
            },
            {
                "fieldname": "effective_discount_percentage",
                "label": "Effective Discount %",
                "fieldtype": "Percent",
                "read_only": 1,
                "depends_on": "apply_discount",
                "insert_after": "total_discount_amount"
            },
            {
                "fieldname": "turnover_incentive",
                "label": "Turnover Incentive",
                "fieldtype": "Currency",
                "read_only": 1,
                "depends_on": "apply_discount",
                "insert_after": "effective_discount_percentage"
            },
            {
                "fieldname": "purchase_estimate_ref",
                "label": "Purchase Estimate Reference",
                "fieldtype": "Link",
                "options": "Purchase Estimate",
                "read_only": 1,
                "insert_after": "turnover_incentive"
            }
        ]
    }
    
    # Custom fields for Purchase Invoice Item
    purchase_invoice_item_fields = {
        "Purchase Invoice Item": [
            {
                "fieldname": "discount_percentage",
                "label": "Discount %",
                "fieldtype": "Percent",
                "insert_after": "rate"
            },
            {
                "fieldname": "discount_amount",
                "label": "Discount Amount",
                "fieldtype": "Currency",
                "read_only": 1,
                "insert_after": "discount_percentage"
            },
            {
                "fieldname": "promotion_applied",
                "label": "Promotion Applied",
                "fieldtype": "Data",
                "read_only": 1,
                "insert_after": "discount_amount"
            }
        ]
    }
    
    # Custom fields for Supplier
    supplier_fields = {
        "Supplier": [
            {
                "fieldname": "default_invoice_discount",
                "label": "Default Invoice Discount %",
                "fieldtype": "Percent",
                "default": 0,
                "insert_after": "default_price_list"
            },
            {
                "fieldname": "credit_limit",
                "label": "Credit Limit",
                "fieldtype": "Currency",
                "insert_after": "default_invoice_discount"
            },
            {
                "fieldname": "payment_terms_template",
                "label": "Default Payment Terms",
                "fieldtype": "Link",
                "options": "Payment Terms Template",
                "insert_after": "credit_limit"
            }
        ]
    }
    
    # Custom fields for Item
    item_fields = {
        "Item": [
            {
                "fieldname": "allow_seasonal_discount",
                "label": "Allow Seasonal Discount",
                "fieldtype": "Check",
                "default": 1,
                "insert_after": "standard_rate"
            },
            {
                "fieldname": "max_discount_percentage",
                "label": "Maximum Discount %",
                "fieldtype": "Percent",
                "default": 100,
                "insert_after": "allow_seasonal_discount"
            }
        ]
    }
    
    # Combine all custom fields
    all_custom_fields = {}
    all_custom_fields.update(purchase_invoice_fields)
    all_custom_fields.update(purchase_invoice_item_fields)
    all_custom_fields.update(supplier_fields)
    all_custom_fields.update(item_fields)
    
    # Create the custom fields
    create_custom_fields(all_custom_fields, update=True)
    
    print("Custom fields created successfully for purchase customizations")


if __name__ == "__main__":
    execute()