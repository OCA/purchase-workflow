# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Order Line Original Date",
    "summary": "adds the Original Expected Arrival to PO lines.",
    "version": "18.0.1.0.0",
    "category": "Purchase Management",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["purchase"],
    "data": [
        "views/purchase_order_line_views.xml",
        "views/purchase_order_views.xml",
    ],
}
