# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Lot",
    "version": "17.0.1.0.1",
    "category": "Purchase",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["florian-dacosta"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock", "stock_restrict_lot"],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
