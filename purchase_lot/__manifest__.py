# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Lot",
    "version": "14.0.1.0.0",
    "category": "Purchase",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["florian-dacosta"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
        "sale_order_lot_selection",
    ],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
