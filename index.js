rappe.pages['cashier-collection-dashboard'] = {
    on_page_load: function(wrapper) {
        let page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'Cashier Collection Dashboard',
            single_column: true
        });

        page.add_field({
            label: 'From Date',
            fieldtype: 'Date',
            fieldname: 'from_date',
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
            change() { load_data(); }
        });

        page.add_field({
            label: 'To Date',
            fieldtype: 'Date',
            fieldname: 'to_date',
            default: frappe.datetime.get_today(),
            change() { load_data(); }
        });

        page.add_field({
            label: 'Cashier',
            fieldtype: 'Link',
            options: 'User',
            fieldname: 'cashier',
            change() { load_data(); }
        });

        let container = page.body;

        function load_data() {
            let from_date = page.fields_dict.from_date.get_value();
            let to_date = page.fields_dict.to_date.get_value();
            let cashier = page.fields_dict.cashier.get_value();

            frappe.call({
                method: 'cashiercounter.dashboard.cashier_collection_dashboard.get_summary',
                args: { from_date, to_date, cashier },
                callback(r) {
                    let html = `
                        <h3>Total Collected: ₹${r.message.total || 0}</h3>
                        <p>Discounts Given: ₹${r.message.discount || 0}</p>
                        <p>Entries: ${r.message.count}</p>
                    `;
                    container.innerHTML = html;
                }
            });
        }

        load_data();
    }
};
