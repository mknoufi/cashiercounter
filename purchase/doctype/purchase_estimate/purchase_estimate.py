# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PurchaseEstimate(Document):
    def validate(self):
        self.calculate_totals()
        self.set_title()
        
    def calculate_totals(self):
        """Calculate totals for the estimate"""
        total_qty = 0
        total_amount = 0
        
        for item in self.get("items", []):
            item.amount = flt(item.qty) * flt(item.rate)
            total_qty += flt(item.qty)
            total_amount += flt(item.amount)
        
        self.total_qty = total_qty
        self.total = total_amount
        
        # Calculate grand total after discounts
        discount_amount = flt(self.total_discount_amount)
        self.grand_total = total_amount - discount_amount
    
    def set_title(self):
        """Set document title"""
        if self.supplier_name:
            self.title = f"PE from {self.supplier_name}"
    
    def on_submit(self):
        """Actions on submit"""
        self.status = "Submitted"
    
    def on_cancel(self):
        """Actions on cancel"""
        self.status = "Cancelled"
    
    @frappe.whitelist()
    def convert_to_invoice(self):
        """Convert estimate to purchase invoice"""
        from cashiercounter.purchase.discount_calculations import convert_estimate_to_invoice
        
        if self.status == "Converted":
            frappe.throw("This estimate has already been converted to an invoice")
        
        if self.docstatus != 1:
            frappe.throw("Please submit the estimate before converting")
        
        # Convert to invoice
        invoice_name = convert_estimate_to_invoice(self.name)
        
        # Update status
        self.status = "Converted"
        self.converted_invoice = invoice_name
        self.save()
        
        frappe.msgprint(f"Purchase Invoice {invoice_name} has been created successfully")
        
        return invoice_name