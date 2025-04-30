# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Sign",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Purchase",
    "author": "Onestein, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "views/purchase_view.xml",
        "views/res_config_settings_view.xml",
        "templates/purchase_portal_templates.xml",
        "report/purchase_order_template.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "purchase_sign/static/tests/tours/purchase_signature.esm.js"
        ],
    },
}
