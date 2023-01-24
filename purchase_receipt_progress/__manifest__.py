# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Receipt Progress",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "author": "Camptocamp SA, Odoo Community Association (OCA), Italo Lopes",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
    ],
    "depends": [
        "purchase_stock",
    ],
    "installable": True,
}
