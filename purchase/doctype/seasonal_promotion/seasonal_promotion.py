# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class SeasonalPromotion(Document):
    def validate(self):
        self.validate_dates()
        
    def validate_dates(self):
        """Validate start and end dates"""
        if getdate(self.start_date) > getdate(self.end_date):
            frappe.throw("End date cannot be earlier than start date")
    
    def on_update(self):
        """Clear cache when promotion is updated"""
        frappe.cache().delete_value("active_promotions")
    
    def on_trash(self):
        """Clear cache when promotion is deleted"""
        frappe.cache().delete_value("active_promotions")