# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class PurchaseDiscountAgreement(Document):
    def validate(self):
        self.validate_dates()
        self.validate_discount()
        self.check_duplicate()
        
    def validate_dates(self):
        """Validate valid from and to dates"""
        if self.valid_to and getdate(self.valid_from) > getdate(self.valid_to):
            frappe.throw("Valid To date cannot be earlier than Valid From date")
    
    def validate_discount(self):
        """Validate discount percentage"""
        if self.discount_percentage <= 0 or self.discount_percentage > 100:
            frappe.throw("Discount percentage must be between 0.01 and 100")
    
    def check_duplicate(self):
        """Check for duplicate agreements"""
        existing = frappe.db.exists(
            "Purchase Discount Agreement",
            {
                "supplier": self.supplier,
                "item_code": self.item_code,
                "is_active": 1,
                "name": ["!=", self.name]
            }
        )
        
        if existing:
            frappe.throw(f"Active discount agreement already exists for {self.supplier} - {self.item_code}")
    
    def on_update(self):
        """Clear cache when agreement is updated"""
        frappe.cache().delete_value(f"supplier_discounts_{self.supplier}")