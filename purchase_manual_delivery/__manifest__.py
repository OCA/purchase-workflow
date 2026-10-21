# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Manual Delivery",
    "summary": "Create purchase receipts manually instead of on confirmation",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock", "purchase_order_line_menu"],
    "data": [
        "security/ir.access.csv",
        "wizard/create_manual_stock_picking.xml",
        "views/purchase_order_line_views.xml",
        "views/purchase_order_views.xml",
        "views/res_config_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "purchase_manual_delivery/static/src/**/*",
        ]
    },
}
