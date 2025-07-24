import frappe
from frappe.model.document import Document
from frappe import _
class CashierCollection(Document):
    def validate(self):
        self.calculate_totals()
        self.prevent_duplicate_invoices()
        self.ensure_ledgers_selected()
    def calculate_totals(self):
        total = sum(row.received or 0 for row in self.collection_table)
        if self.discount and self.discount > total:
            frappe.throw(_("Discount cannot exceed total amount."))
        self.amount = total
        self.payable_amount = total - (self.discount or 0)
    def prevent_duplicate_invoices(self):
        seen = set()
        for row in self.collection_table:
            if row.invoice in seen:
                frappe.throw(_("Duplicate Sales Invoice: {0}").format(row.invoice))
            seen.add(row.invoice)
    def ensure_ledgers_selected(self):
        if not self.paid_from or not self.paid_to:
            frappe.throw(_("Please select both 'Paid From' and 'Paid To' accounts before
        submitting."))
    def on_submit(self):
        self.create_payment_entries()
    def create_payment_entries(self):
        for row in self.collection_table:
            if row.received > 0:
                self.create_payment_entry(row)
    def create_payment_entry(self, row):
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "company": frappe.defaults.get_user_default("Company"),
            "posting_date": self.posting_date,
            "mode_of_payment": self.payment_mode,
            "party_type": "Customer",
            "party": self.customer,
            "paid_from": self.paid_from,
            "paid_to": self.paid_to,
            "paid_amount": row.received,
            "received_amount": row.received,
            "references": [{
                "reference_doctype": "Sales Invoice",
                "reference_name": row.invoice,
                "allocated_amount": row.received
            }],
            "custom_cashier_collection": self.name
        })
        pe.insert(ignore_permissions=True)
        pe.submit()