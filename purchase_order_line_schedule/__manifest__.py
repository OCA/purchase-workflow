# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Order Line Schedule",
    "summary": "Add shedule lines in purchase order lines",
    "version": "13.0.1.0.1",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/purchase_order_line_schedule.xml",
        "views/purchase_order_views.xml",
        "views/purchase_order_line_schedule_views.xml",
    ],
}
