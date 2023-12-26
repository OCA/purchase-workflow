# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Reception Status",
    "summary": "Manage customizations on purchase order line",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Italo Lopes, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": [
        # Core
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order_line.xml",
    ],
    "website": "https://github.com/OCA/purchase-workflow",
    "installable": True,
}
