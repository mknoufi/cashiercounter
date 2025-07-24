# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_analytics_data():
    """Get analytics data for purchase dashboard"""
    
    # This would typically fetch data from the database
    # For now, returning sample data structure
    return {
        "monthly_purchase": {
            "total_amount": 150000,
            "invoice_count": 45,
            "avg_amount": 3333
        },
        "active_promotions": 3,
        "top_suppliers": [
            {"supplier": "ABC Suppliers", "total_amount": 50000, "invoice_count": 15},
            {"supplier": "XYZ Trading", "total_amount": 30000, "invoice_count": 8},
            {"supplier": "Global Mart", "total_amount": 25000, "invoice_count": 12}
        ]
    }