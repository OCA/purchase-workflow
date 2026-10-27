# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Transit Receipt",
    "summary": "Receive purchases through a valued incoming transit location",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
