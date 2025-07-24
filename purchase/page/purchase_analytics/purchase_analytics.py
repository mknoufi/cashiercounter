# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_analytics_data():
    """Get analytics data for purchase dashboard"""
    
    # This would typically fetch data from the database
    # For now, returning sample data structure
    # Fetch monthly purchase data
    monthly_purchase = frappe.db.sql("""
        SELECT SUM(total_amount) AS total_amount, COUNT(name) AS invoice_count, AVG(total_amount) AS avg_amount
        FROM `tabPurchase Invoice`
        WHERE MONTH(posting_date) = MONTH(CURDATE()) AND YEAR(posting_date) = YEAR(CURDATE())
    """, as_dict=True)[0]

    # Fetch active promotions count
    active_promotions = frappe.db.count("Promotion", filters={"status": "Active"})

    # Fetch top suppliers
    top_suppliers = frappe.db.sql("""
        SELECT supplier, SUM(total_amount) AS total_amount, COUNT(name) AS invoice_count
        FROM `tabPurchase Invoice`
        GROUP BY supplier
        ORDER BY total_amount DESC
        LIMIT 3
    """, as_dict=True)

    return {
        "monthly_purchase": monthly_purchase,
        "active_promotions": active_promotions,
        "top_suppliers": top_suppliers
    }