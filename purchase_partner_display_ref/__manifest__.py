# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Partner Display Reference",
    "summary": "Wire the supplier reference prefix into Purchase views.",
    "version": "19.0.1.0.0",
    "category": "Purchases",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["partner_display_ref", "partner_supplier_ref", "purchase"],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
}
