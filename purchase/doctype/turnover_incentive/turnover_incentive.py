# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class TurnoverIncentive(Document):
    def validate(self):
        self.validate_dates()
        self.validate_amounts()
        
    def validate_dates(self):
        """Validate valid from and to dates"""
        if self.valid_from and self.valid_to:
            if getdate(self.valid_from) > getdate(self.valid_to):
                frappe.throw("Valid To date cannot be earlier than Valid From date")
    
    def validate_amounts(self):
        """Validate incentive amounts and percentages"""
        if self.min_turnover <= 0:
            frappe.throw("Minimum turnover must be greater than zero")
            
        if self.incentive_percentage <= 0 or self.incentive_percentage > 100:
            frappe.throw("Incentive percentage must be between 0.01 and 100")
    
    def on_update(self):
        """Clear cache when incentive scheme is updated"""
        frappe.cache().delete_value("active_incentive_schemes")