import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_summary(from_date=None, to_date=None, cashier=None):
    conditions = []
    if from_date:
        conditions.append(f"posting_date >= '{getdate(from_date)}'")
    if to_date:
        conditions.append(f"posting_date <= '{getdate(to_date)}'")
    if cashier:
        conditions.append(f"owner = '{cashier}'")

    where = " AND ".join(conditions)
    if where:
        where = f"WHERE {where}"

    data = frappe.db.sql(f"""
        SELECT
            SUM(amount) as total,
            SUM(discount) as discount,
            COUNT(*) as count
        FROM `tabCashier Collection`
        {where}
    """, as_dict=True)[0]

    return data
