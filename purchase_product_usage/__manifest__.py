# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

{
    "name": "Purchase Product Usage",
    "version": "14.0.1.1.0",
    "category": "Purchase Management",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/purchase_product_usage.xml",
        "security/ir.model.access.csv",
        "views/purchase_order_line_view.xml",
        "views/purchase_product_usage_view.xml",
    ],
    "installable": True,
}
