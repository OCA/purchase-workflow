# Copyright 2024 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Sign",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "Purchase",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "report/purchase_order_template.xml",
        "templates/purchase_portal_templates.xml",
        "views/purchase_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "purchase_sign/static/tests/tours/purchase_signature.esm.js"
        ],
    },
}
