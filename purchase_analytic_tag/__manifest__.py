# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Analytic Tag",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase", "account_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/purchase_oder_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
