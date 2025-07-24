import frappe
from frappe import _

@frappe.whitelist()
def get_summary(from_date=None, to_date=None, cashier=None):
    filters = {"docstatus": 1}
    if from_date and to_date:
        filters["posting_date"] = ["between", [from_date, to_date]]
    if cashier:
        filters["collected_by"] = cashier

    data = frappe.get_all(
        "Cashier Collection",
        filters=filters,
        fields=["amount", "discount"]
    )

    return {
        "total": sum([row.amount or 0 for row in data]),
        "discount": sum([row.discount or 0 for row in data]),
        "count": len(data)
    }