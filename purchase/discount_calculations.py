"""
ERPNext v15 Purchase Customizations - Discount Calculation Engine
This module handles advanced discount calculations for purchase transactions.
"""

import frappe
from frappe import _
from frappe.utils import flt, nowdate, add_days, getdate
from datetime import datetime


class DiscountCalculator:
    """Main class for handling all discount calculations"""
    
    def __init__(self, doc):
        self.doc = doc
        self.total_discount = 0
        self.item_wise_discounts = {}
    
    def apply_all_discounts(self):
        """Apply all applicable discounts to the purchase document"""
        try:
            if not self.doc.get("apply_discount"):
                return
            
            # Apply item-wise discounts
            if self.doc.get("discount_type") == "Item-wise":
                self.apply_item_wise_discounts()
            
            # Apply invoice-wise discounts
            elif self.doc.get("discount_type") == "Invoice-wise":
                self.apply_invoice_wise_discount()
            
            # Apply seasonal promotions
            self.apply_seasonal_promotions()
            
            # Apply turnover incentives
            self.apply_turnover_incentives()
            
            # Update totals
            self.update_document_totals()
            
        except Exception as e:
            frappe.throw(_("Error in discount calculation: {0}").format(str(e)))
    
    def apply_item_wise_discounts(self):
        """Apply discounts at item level"""
        for item in self.doc.get("items", []):
            discount_rate = 0
            
            # Get supplier-specific discount
            supplier_discount = self.get_supplier_discount(item.item_code, self.doc.supplier)
            if supplier_discount:
                discount_rate += flt(supplier_discount)
            
            # Apply discount
            if discount_rate > 0:
                discount_amount = flt(item.amount) * flt(discount_rate) / 100
                item.discount_percentage = discount_rate
                item.discount_amount = discount_amount
                item.rate = flt(item.rate) - (flt(item.rate) * flt(discount_rate) / 100)
                
                self.item_wise_discounts[item.item_code] = discount_amount
                self.total_discount += discount_amount
    
    def apply_invoice_wise_discount(self):
        """Apply discount at invoice level"""
        if not self.doc.supplier:
            return
        
        # Get supplier default discount
        supplier_doc = frappe.get_doc("Supplier", self.doc.supplier)
        default_discount = flt(supplier_doc.get("default_invoice_discount", 0))
        
        if default_discount > 0:
            total_amount = flt(self.doc.total)
            discount_amount = total_amount * default_discount / 100
            
            self.doc.discount_amount = discount_amount
            self.doc.additional_discount_percentage = default_discount
            self.total_discount += discount_amount
    
    def apply_seasonal_promotions(self):
        """Apply active seasonal promotions"""
        current_date = nowdate()
        
        # Get active promotions
        promotions = frappe.get_all(
            "Seasonal Promotion",
            filters={
                "is_active": 1,
                "start_date": ["<=", current_date],
                "end_date": [">=", current_date]
            },
            fields=["name", "promotion_name", "discount_percentage", "applicable_items"]
        )
        
        for promotion in promotions:
            promotion_doc = frappe.get_doc("Seasonal Promotion", promotion.name)
            
            # Check if promotion applies to current items
            applicable_items = [item.item_code for item in promotion_doc.get("applicable_items", [])]
            
            for item in self.doc.get("items", []):
                if not applicable_items or item.item_code in applicable_items:
                    # Apply promotion discount
                    promo_discount = flt(item.amount) * flt(promotion_doc.discount_percentage) / 100
                    
                    # Update item
                    current_discount = flt(item.get("discount_amount", 0))
                    item.discount_amount = current_discount + promo_discount
                    item.promotion_applied = promotion_doc.promotion_name
                    
                    self.total_discount += promo_discount
    
    def apply_turnover_incentives(self):
        """Apply turnover-based incentives"""
        if not self.doc.supplier:
            return
        
        # Get supplier's yearly purchase amount
        yearly_purchase = self.get_yearly_purchase_amount(self.doc.supplier)
        
        # Get applicable incentive schemes
        incentives = frappe.get_all(
            "Turnover Incentive",
            filters={
                "is_active": 1,
                "min_turnover": ["<=", yearly_purchase]
            },
            fields=["name", "incentive_percentage", "max_incentive_amount"],
            order_by="min_turnover desc",
            limit=1
        )
        
        if incentives:
            incentive = incentives[0]
            incentive_rate = flt(incentive.incentive_percentage)
            max_incentive = flt(incentive.max_incentive_amount)
            
            if incentive_rate > 0:
                incentive_amount = flt(self.doc.total) * incentive_rate / 100
                
                # Apply maximum cap if specified
                if max_incentive > 0 and incentive_amount > max_incentive:
                    incentive_amount = max_incentive
                
                self.doc.turnover_incentive = incentive_amount
                self.total_discount += incentive_amount
    
    def update_document_totals(self):
        """Update document totals after discount calculations"""
        if self.total_discount > 0:
            self.doc.total_discount_amount = self.total_discount
            
            # Calculate effective discount percentage
            if flt(self.doc.total) > 0:
                effective_discount_pct = (self.total_discount / flt(self.doc.total)) * 100
                self.doc.effective_discount_percentage = effective_discount_pct
            
            # Update grand total
            self.doc.grand_total = flt(self.doc.total) - self.total_discount
    
    def get_supplier_discount(self, item_code, supplier):
        """Get supplier-specific discount for an item"""
        try:
            # Check for supplier-item specific discount
            discount_data = frappe.db.get_value(
                "Purchase Discount Agreement",
                {
                    "supplier": supplier,
                    "item_code": item_code,
                    "is_active": 1
                },
                "discount_percentage"
            )
            return flt(discount_data) if discount_data else 0
        except:
            return 0
    
    def get_yearly_purchase_amount(self, supplier):
        """Get yearly purchase amount for supplier"""
        try:
            from_date = add_days(nowdate(), -365)
            to_date = nowdate()
            
            result = frappe.db.sql("""
                SELECT SUM(grand_total) as total
                FROM `tabPurchase Invoice`
                WHERE supplier = %s
                AND posting_date BETWEEN %s AND %s
                AND docstatus = 1
            """, (supplier, from_date, to_date), as_dict=True)
            
            return flt(result[0].total) if result and result[0].total else 0
        except:
            return 0


def apply_discounts(doc, method):
    """Hook function to apply discounts on purchase documents"""
    if doc.doctype in ["Purchase Invoice", "Purchase Estimate"]:
        calculator = DiscountCalculator(doc)
        calculator.apply_all_discounts()


def validate_purchase_estimate(doc, method):
    """Validation function for Purchase Estimate"""
    if doc.doctype == "Purchase Estimate":
        # Validate conversion limits
        if flt(doc.total) > 100000:  # Example threshold
            if not frappe.has_permission("Purchase Estimate", "approve"):
                frappe.throw(_("Purchase Estimate above ₹1,00,000 requires manager approval"))


def convert_estimate_to_invoice(estimate_name):
    """Convert Purchase Estimate to Purchase Invoice"""
    try:
        estimate_doc = frappe.get_doc("Purchase Estimate", estimate_name)
        
        # Create new Purchase Invoice
        invoice_doc = frappe.new_doc("Purchase Invoice")
        
        # Copy relevant fields
        invoice_doc.supplier = estimate_doc.supplier
        invoice_doc.posting_date = nowdate()
        invoice_doc.purchase_estimate_ref = estimate_name
        
        # Copy items
        for item in estimate_doc.get("items", []):
            invoice_item = invoice_doc.append("items", {})
            invoice_item.item_code = item.item_code
            invoice_item.qty = item.qty
            invoice_item.rate = item.rate
            invoice_item.amount = item.amount
            invoice_item.discount_percentage = item.get("discount_percentage", 0)
            invoice_item.discount_amount = item.get("discount_amount", 0)
        
        # Copy discount information
        invoice_doc.apply_discount = estimate_doc.get("apply_discount", 0)
        invoice_doc.discount_type = estimate_doc.get("discount_type")
        invoice_doc.total_discount_amount = estimate_doc.get("total_discount_amount", 0)
        
        # Save and return
        invoice_doc.save()
        
        # Update estimate status
        estimate_doc.status = "Converted"
        estimate_doc.converted_invoice = invoice_doc.name
        estimate_doc.save()
        
        return invoice_doc.name
        
    except Exception as e:
        frappe.throw(_("Error converting estimate to invoice: {0}").format(str(e)))


@frappe.whitelist()
def get_supplier_discounts(supplier):
    """Get all applicable discounts for a supplier"""
    try:
        discounts = frappe.get_all(
            "Purchase Discount Agreement",
            filters={"supplier": supplier, "is_active": 1},
            fields=["item_code", "discount_percentage", "valid_from", "valid_to"]
        )
        return discounts
    except Exception as e:
        frappe.log_error(f"Error fetching supplier discounts: {str(e)}")
        return []


@frappe.whitelist()
def get_active_promotions():
    """Get all active seasonal promotions"""
    try:
        current_date = nowdate()
        promotions = frappe.get_all(
            "Seasonal Promotion",
            filters={
                "is_active": 1,
                "start_date": ["<=", current_date],
                "end_date": [">=", current_date]
            },
            fields=["name", "promotion_name", "discount_percentage", "start_date", "end_date"]
        )
        return promotions
    except Exception as e:
        frappe.log_error(f"Error fetching active promotions: {str(e)}")
        return []