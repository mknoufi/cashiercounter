# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, formatdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "name",
            "label": _("Invoice"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 150
        },
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150
        },
        {
            "fieldname": "total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "total_discount_amount",
            "label": _("Discount Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "effective_discount_percentage",
            "label": _("Discount %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "discount_type",
            "label": _("Discount Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "grand_total",
            "label": _("Grand Total"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "savings",
            "label": _("Savings"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT 
            pi.posting_date,
            pi.name,
            pi.supplier,
            pi.total,
            COALESCE(pi.total_discount_amount, 0) as total_discount_amount,
            COALESCE(pi.effective_discount_percentage, 0) as effective_discount_percentage,
            COALESCE(pi.discount_type, 'None') as discount_type,
            pi.grand_total,
            COALESCE(pi.total_discount_amount, 0) as savings
        FROM `tabPurchase Invoice` pi
        WHERE pi.docstatus = 1
        {conditions}
        ORDER BY pi.posting_date DESC, pi.name DESC
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    """Build SQL conditions based on filters"""
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
    
    if filters.get("supplier"):
        conditions.append("pi.supplier = %(supplier)s")
    
    if filters.get("discount_type"):
        conditions.append("pi.discount_type = %(discount_type)s")
    
    if filters.get("min_discount_amount"):
        conditions.append("COALESCE(pi.total_discount_amount, 0) >= %(min_discount_amount)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""