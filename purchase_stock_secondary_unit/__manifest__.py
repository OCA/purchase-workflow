# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Stock Secondary Unit",
    "summary": "Populate product quantities in a secondary unit to stock moves",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_order_secondary_unit", "stock_secondary_unit"],
    "auto_install": True,
}
