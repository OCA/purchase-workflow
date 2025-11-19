# Copyright 2025 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Invoice Status Line",
    "version": "18.0.1.0.1",
    "category": "Purchases",
    "license": "AGPL-3",
    "summary": "Add invoice status on purchase order lines",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["JoanSForgeFlow"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_force_invoiced",
        "purchase_order_line_menu",
    ],
    "post_init_hook": "post_init_hook",
    "data": [
        "views/purchase_order_line_views.xml",
    ],
    "installable": True,
}
