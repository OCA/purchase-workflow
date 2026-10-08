# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Line Sale History",
    "summary": "Show the sales history of a product while filling a "
    "purchase order line",
    "version": "19.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["purchase"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/purchase_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "purchase_line_sale_history/static/src/js/purchase_order_sales_history_field.esm.js",
            "purchase_line_sale_history/static/src/xml/purchase_order_sales_history_field.xml",
            "purchase_line_sale_history/static/src/scss/purchase_order_sales_history.scss",
        ],
    },
    "installable": True,
}
