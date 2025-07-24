import frappe
import os

def run():
    app_name = "cashiercounter"
    module_name = "Cashier"

    # Step 1: Ensure modules.txt includes 'cashier'
    app_path = frappe.get_app_path(app_name)
    modules_txt_path = os.path.join(app_path, "modules.txt")

    if not os.path.exists(modules_txt_path):
        with open(modules_txt_path, "w") as f:
            f.write("cashier\n")
        print("✅ Created modules.txt with 'cashier'")
    else:
        with open(modules_txt_path) as f:
            lines = f.read().splitlines()
        if "cashier" not in lines:
            with open(modules_txt_path, "a") as f:
                f.write("\ncashier\n")
            print("✅ Appended 'cashier' to modules.txt")
        else:
            print("✅ 'cashier' already in modules.txt")

    # Step 2: Ensure Package exists
    if not frappe.db.exists("Package", app_name):
        frappe.get_doc({
            "doctype": "Package",
            "name": app_name,
            "package_name": app_name,
            "app_name": app_name
        }).insert(ignore_permissions=True)
        print("✅ Package created")
    else:
        print("✅ Package already exists")

    # Step 3: Ensure Module Def
    if not frappe.db.exists("Module Def", module_name):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": module_name,
            "app_name": app_name,
            "package": app_name,
            "custom": 1
        }).insert(ignore_permissions=True)
        print("✅ Module Def created")
    else:
        frappe.db.set_value("Module Def", module_name, "package", app_name)
        print("✅ Module Def package updated")

    frappe.db.commit()

    # Step 4: Insert Page
    if not frappe.db.exists("Page", "cashier_collection_dashboard"):
        page = frappe.get_doc({
            "doctype": "Page",
            "title": "Cashier Collection Dashboard",
            "page_name": "cashier_collection_dashboard",
            "module": module_name,
            "custom": 1,
            "developer_mode": 1
        })
        page.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Page created successfully")
    else:
        print("✅ Page already exists")