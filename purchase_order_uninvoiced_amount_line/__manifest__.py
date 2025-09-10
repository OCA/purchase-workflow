# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Order Line Uninvoiced Amount",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase", "purchase_order_line_menu"],
    "data": ["views/purchase_order_line_views.xml"],
}
