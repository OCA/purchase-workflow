# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order Type",
    "version": "13.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": ["purchase"],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "security/ir.model.access.csv",
        "views/view_purchase_order_type.xml",
        "views/view_purchase_order.xml",
        "views/res_partner_view.xml",
        "data/purchase_order_type.xml",
    ],
    "installable": True,
    "auto_install": False,
}
