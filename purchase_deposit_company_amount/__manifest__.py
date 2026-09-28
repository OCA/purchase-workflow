# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Deposit Company Amount",
    "summary": "Book purchase deposits at the company-currency amount actually paid",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "maintainers": ["kanda999", "Aungkokolin1997"],
    "depends": ["purchase_stock", "purchase_deposit"],
    "data": [
        "views/account_move_views.xml",
    ],
    "installable": True,
}
