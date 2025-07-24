app_name = "cashiercounter"
app_title = "Cashier Counter"
app_publisher = "Your Company or Name"
app_description = "Custom dashboard for cashier collection reporting and ERPNext v15 purchase customizations"
app_email = "your@email.com"
app_license = "MIT"

# Include JS files for purchase customizations
app_include_js = [
    "/assets/cashiercounter/js/purchase_invoice.js",
    "/assets/cashiercounter/js/purchase_estimate.js"
]

# Document Events - Purchase Customizations
doc_events = {
    "Purchase Invoice": {
        "validate": "cashiercounter.purchase.discount_calculations.apply_discounts",
        "before_save": "cashiercounter.purchase.discount_calculations.validate_purchase_estimate"
    },
    "Purchase Estimate": {
        "validate": "cashiercounter.purchase.discount_calculations.apply_discounts",
        "before_save": "cashiercounter.purchase.discount_calculations.validate_purchase_estimate"
    }
}

# Scheduled Tasks for Purchase Management
scheduler_events = {
    "daily": [
        "cashiercounter.purchase.tasks.send_credit_note_reminders",
        "cashiercounter.purchase.tasks.update_promotion_status"
    ],
    "weekly": [
        "cashiercounter.purchase.tasks.calculate_turnover_incentives"
    ]
}

# Override standard methods
override_doctype_dashboards = {
    "Purchase Invoice": "cashiercounter.purchase.dashboard.purchase_invoice_dashboard",
    "Supplier": "cashiercounter.purchase.dashboard.supplier_dashboard"
}

# Fixtures for purchase customizations
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "in", ["Purchase Invoice", "Purchase Invoice Item", "Supplier"]]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            ["doc_type", "in", ["Purchase Invoice", "Purchase Invoice Item", "Supplier"]]
        ]
    }
]

# Boot session - load initial data
boot_session = "cashiercounter.purchase.boot.boot_session"