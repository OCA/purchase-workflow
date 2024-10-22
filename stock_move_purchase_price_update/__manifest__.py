# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Move Purchase Price Update",
    "summary": "Allow update purchase price from incoming picking operations",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "stock",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["carlosdauden"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/stock_move_views.xml",
    ],
}
