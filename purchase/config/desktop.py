"""
Purchase Module Configuration
Desktop and navigation setup for purchase customizations
"""

from frappe import _


def get_data():
    return [
        {
            "module_name": "Purchase",
            "color": "#2ecc71",
            "icon": "fa fa-shopping-cart",
            "type": "module",
            "description": "Advanced Purchase Management with Discounts and Promotions",
            "label": _("Purchase Management")
        }
    ]


def get_purchase_dashboard_data():
    """Get dashboard data for purchase module"""
    return {
        "fieldname": "supplier",
        "transactions": [
            {
                "label": _("Estimates & Invoices"),
                "items": ["Purchase Estimate", "Purchase Invoice", "Purchase Receipt"]
            },
            {
                "label": _("Promotions & Discounts"),
                "items": ["Seasonal Promotion", "Turnover Incentive", "Purchase Discount Agreement"]
            },
            {
                "label": _("Credit Management"),
                "items": ["Supplier Credit Note Tracking", "Debit Note", "Payment Entry"]
            }
        ]
    }


def get_purchase_workspace():
    """Configure purchase workspace"""
    return {
        "name": "Purchase Management",
        "charts": [
            {
                "chart_name": "Purchase Trends",
                "label": "Monthly Purchase Trends"
            },
            {
                "chart_name": "Supplier Performance",
                "label": "Top Suppliers by Volume"
            }
        ],
        "shortcuts": [
            {
                "type": "DocType",
                "name": "Purchase Estimate",
                "label": "New Estimate"
            },
            {
                "type": "DocType", 
                "name": "Purchase Invoice",
                "label": "New Invoice"
            },
            {
                "type": "DocType",
                "name": "Seasonal Promotion",
                "label": "New Promotion"
            },
            {
                "type": "Page",
                "name": "purchase-analytics",
                "label": "Purchase Analytics"
            }
        ]
    }