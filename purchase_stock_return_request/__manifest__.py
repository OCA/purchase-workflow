# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Stock Return Request",
    "version": "11.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
        "stock_return_request",
    ],
    "data": [
        'views/purchase_return_request_views.xml',
        'report/stock_return_report.xml',
    ],
}
