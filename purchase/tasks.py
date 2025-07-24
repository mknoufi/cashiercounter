"""
Scheduled Tasks for Purchase Management
Handles automated reminders, status updates, and incentive calculations
"""

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, today
from datetime import datetime


def send_credit_note_reminders():
    """Send reminders for pending credit notes"""
    try:
        # Get pending credit notes due for reminder
        pending_notes = frappe.get_all(
            "Supplier Credit Note Tracking",
            filters={
                "status": "Pending",
                "reminder_date": ["<=", today()]
            },
            fields=["name", "supplier", "credit_note_amount", "expected_settlement_date"]
        )
        
        for note in pending_notes:
            # Send email reminder to purchase team
            send_credit_note_reminder_email(note)
            
            # Update next reminder date
            next_reminder = add_days(today(), 3)  # Remind again in 3 days
            frappe.db.set_value(
                "Supplier Credit Note Tracking", 
                note.name, 
                "reminder_date", 
                next_reminder
            )
        
        if pending_notes:
            frappe.logger().info(f"Sent {len(pending_notes)} credit note reminders")
            
    except Exception as e:
        frappe.log_error(f"Error in send_credit_note_reminders: {str(e)}")


def update_promotion_status():
    """Update status of seasonal promotions based on dates"""
    try:
        current_date = nowdate()
        
        # Activate promotions that should start today
        starting_promotions = frappe.get_all(
            "Seasonal Promotion",
            filters={
                "start_date": current_date,
                "is_active": 0
            },
            fields=["name"]
        )
        
        for promo in starting_promotions:
            frappe.db.set_value("Seasonal Promotion", promo.name, "is_active", 1)
        
        # Deactivate expired promotions
        expired_promotions = frappe.get_all(
            "Seasonal Promotion",
            filters={
                "end_date": ["<", current_date],
                "is_active": 1
            },
            fields=["name"]
        )
        
        for promo in expired_promotions:
            frappe.db.set_value("Seasonal Promotion", promo.name, "is_active", 0)
        
        # Clear promotion cache
        frappe.cache().delete_value("active_promotions")
        
        if starting_promotions or expired_promotions:
            frappe.logger().info(
                f"Updated promotion status: {len(starting_promotions)} activated, "
                f"{len(expired_promotions)} deactivated"
            )
            
    except Exception as e:
        frappe.log_error(f"Error in update_promotion_status: {str(e)}")


def calculate_turnover_incentives():
    """Calculate and update turnover incentives for suppliers"""
    try:
        # Get all active suppliers
        suppliers = frappe.get_all("Supplier", filters={"disabled": 0}, fields=["name"])
        
        for supplier in suppliers:
            calculate_supplier_incentive(supplier.name)
        
        frappe.logger().info(f"Calculated turnover incentives for {len(suppliers)} suppliers")
        
    except Exception as e:
        frappe.log_error(f"Error in calculate_turnover_incentives: {str(e)}")


def calculate_supplier_incentive(supplier_name):
    """Calculate incentive for a specific supplier"""
    try:
        # Get yearly purchase amount
        from_date = add_days(nowdate(), -365)
        to_date = nowdate()
        
        result = frappe.db.sql("""
            SELECT SUM(grand_total) as total_purchase
            FROM `tabPurchase Invoice`
            WHERE supplier = %s
            AND posting_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (supplier_name, from_date, to_date), as_dict=True)
        
        total_purchase = result[0].total_purchase if result and result[0].total_purchase else 0
        
        if total_purchase <= 0:
            return
        
        # Get applicable incentive scheme
        incentive_schemes = frappe.get_all(
            "Turnover Incentive",
            filters={
                "is_active": 1,
                "min_turnover": ["<=", total_purchase]
            },
            fields=["name", "incentive_percentage", "max_incentive_amount", "min_turnover"],
            order_by="min_turnover desc",
            limit=1
        )
        
        if not incentive_schemes:
            return
        
        scheme = incentive_schemes[0]
        incentive_amount = total_purchase * scheme.incentive_percentage / 100
        
        # Apply maximum cap if specified
        if scheme.max_incentive_amount > 0:
            incentive_amount = min(incentive_amount, scheme.max_incentive_amount)
        
        # Create or update supplier incentive record
        create_supplier_incentive_record(supplier_name, total_purchase, incentive_amount, scheme.name)
        
    except Exception as e:
        frappe.log_error(f"Error calculating incentive for {supplier_name}: {str(e)}")


def create_supplier_incentive_record(supplier, turnover, incentive_amount, scheme):
    """Create or update supplier incentive record"""
    try:
        # Check if record exists for current period
        existing_record = frappe.db.get_value(
            "Supplier Turnover Incentive",
            {
                "supplier": supplier,
                "calculation_date": nowdate()
            },
            "name"
        )
        
        if existing_record:
            # Update existing record
            doc = frappe.get_doc("Supplier Turnover Incentive", existing_record)
            doc.yearly_turnover = turnover
            doc.incentive_amount = incentive_amount
            doc.incentive_scheme = scheme
            doc.save()
        else:
            # Create new record
            doc = frappe.new_doc("Supplier Turnover Incentive")
            doc.supplier = supplier
            doc.calculation_date = nowdate()
            doc.yearly_turnover = turnover
            doc.incentive_amount = incentive_amount
            doc.incentive_scheme = scheme
            doc.save()
        
    except Exception as e:
        frappe.log_error(f"Error creating incentive record for {supplier}: {str(e)}")


def send_credit_note_reminder_email(credit_note):
    """Send email reminder for pending credit note"""
    try:
        # Get purchase team email addresses
        purchase_users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "name": ["in", get_users_with_role("Purchase Manager")]
            },
            fields=["email", "full_name"]
        )
        
        if not purchase_users:
            return
        
        recipients = [user.email for user in purchase_users if user.email]
        
        if not recipients:
            return
        
        # Prepare email content
        subject = f"Credit Note Reminder - {credit_note.supplier}"
        
        message = f"""
        <p>Dear Purchase Team,</p>
        
        <p>This is a reminder for a pending credit note:</p>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <td><strong>Credit Note</strong></td>
                <td>{credit_note.name}</td>
            </tr>
            <tr>
                <td><strong>Supplier</strong></td>
                <td>{credit_note.supplier}</td>
            </tr>
            <tr>
                <td><strong>Amount</strong></td>
                <td>{frappe.format(credit_note.credit_note_amount, {"fieldtype": "Currency"})}</td>
            </tr>
            <tr>
                <td><strong>Expected Settlement</strong></td>
                <td>{credit_note.expected_settlement_date}</td>
            </tr>
        </table>
        
        <p>Please follow up with the supplier for settlement.</p>
        
        <p>Best regards,<br>Purchase Management System</p>
        """
        
        # Send email
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            now=True
        )
        
    except Exception as e:
        frappe.log_error(f"Error sending credit note reminder email: {str(e)}")


def get_users_with_role(role):
    """Get list of users with specific role"""
    try:
        users = frappe.get_all(
            "Has Role",
            filters={"role": role},
            fields=["parent"]
        )
        return [user.parent for user in users]
    except:
        return []


@frappe.whitelist()
def manual_promotion_update():
    """Manual trigger for promotion status update"""
    update_promotion_status()
    frappe.msgprint(_("Promotion status updated successfully"))


@frappe.whitelist()
def manual_incentive_calculation():
    """Manual trigger for incentive calculation"""
    calculate_turnover_incentives()
    frappe.msgprint(_("Turnover incentives calculated successfully"))


def cleanup_old_records():
    """Clean up old promotional and incentive records"""
    try:
        # Delete promotional records older than 2 years
        old_date = add_days(nowdate(), -730)
        
        frappe.db.sql("""
            DELETE FROM `tabSeasonal Promotion`
            WHERE end_date < %s
            AND is_active = 0
        """, (old_date,))
        
        # Archive old incentive records
        frappe.db.sql("""
            UPDATE `tabSupplier Turnover Incentive`
            SET status = 'Archived'
            WHERE calculation_date < %s
            AND status != 'Archived'
        """, (old_date,))
        
        frappe.logger().info("Cleaned up old promotional and incentive records")
        
    except Exception as e:
        frappe.log_error(f"Error in cleanup_old_records: {str(e)}")


# Additional utility functions for purchase management
def get_purchase_analytics():
    """Get purchase analytics data"""
    try:
        analytics = {}
        
        # Total purchase amount this month
        current_month_start = nowdate().replace(day=1)
        
        monthly_purchase = frappe.db.sql("""
            SELECT 
                COUNT(*) as invoice_count,
                SUM(grand_total) as total_amount,
                AVG(grand_total) as avg_amount
            FROM `tabPurchase Invoice`
            WHERE posting_date >= %s
            AND docstatus = 1
        """, (current_month_start,), as_dict=True)
        
        analytics["monthly_purchase"] = monthly_purchase[0] if monthly_purchase else {}
        
        # Top suppliers by volume
        top_suppliers = frappe.db.sql("""
            SELECT 
                supplier,
                COUNT(*) as invoice_count,
                SUM(grand_total) as total_amount
            FROM `tabPurchase Invoice`
            WHERE posting_date >= %s
            AND docstatus = 1
            GROUP BY supplier
            ORDER BY total_amount DESC
            LIMIT 10
        """, (current_month_start,), as_dict=True)
        
        analytics["top_suppliers"] = top_suppliers
        
        # Active promotions count
        active_promotions = frappe.db.count(
            "Seasonal Promotion",
            {
                "is_active": 1,
                "start_date": ["<=", nowdate()],
                "end_date": [">=", nowdate()]
            }
        )
        
        analytics["active_promotions"] = active_promotions
        
        return analytics
        
    except Exception as e:
        frappe.log_error(f"Error in get_purchase_analytics: {str(e)}")
        return {}