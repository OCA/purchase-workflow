# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Schedule Manual Delivery",
    "summary": """
        Allows to create manual deliveries based on a predefined delivery
        schedule.
    """,
    "version": "13.0.1.0.0",
    "license": "LGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_manual_delivery", "purchase_order_line_schedule_stock"],
    "data": [
        "wizard/create_manual_stock_picking.xml",
        "views/purchase_order_line_schedule_views.xml",
    ],
}
