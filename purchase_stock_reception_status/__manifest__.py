# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Reception Status",
    "version": "17.0.1.0.0",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Glue module to integrate OCA reception status with purchase_stock",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_reception_status", "purchase_stock"],
    "data": ["views/purchase_order.xml"],
    "auto_install": True,
    "installable": True,
}
