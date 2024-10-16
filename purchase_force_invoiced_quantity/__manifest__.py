# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Force Invoiced Quantity",
    "summary": "Add manual invoice quantity in purchase order lines",
    "version": "16.0.1.0.0",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_force_invoiced"],
    "data": [
        "views/purchase_order.xml",
    ],
    "demo": [
        "demo/demo_product.xml",
        "demo/demo_purchase_order.xml",
    ],
    "installable": True,
}
