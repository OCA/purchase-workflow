# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Purchase Secondary Unit",
    "summary": "Propagate sale secondary uom to purchase orders",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "stock",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase_stock",
        "purchase_order_secondary_unit",
        "sale_stock_secondary_unit",
    ],
    "auto_install": True,
}
