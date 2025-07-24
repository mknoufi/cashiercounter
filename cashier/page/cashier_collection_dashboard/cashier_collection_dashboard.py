import frappe

@frappe.whitelist()
def get_summary(from_date, to_date, cashier=None):
    filters = {
        "posting_date": ["between", [from_date, to_date]]
    }
    if cashier:
        filters["owner"] = cashier

    data = frappe.get_all(
        "Cashier Collection",
        filters=filters,
        fields=["discount_amount", "total_amount"]
    )

    total = sum(d.total_amount or 0 for d in data)
    discount = sum(d.discount_amount or 0 for d in data)

    return {
        "total": total,
        "discount": discount,
        "count": len(data)
    }