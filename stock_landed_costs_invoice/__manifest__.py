# Copyright 2021 Lorenzo Battistini @ TAKOBI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Landed Costs: creation from invoice",
    "summary": "Allow to create landed costs from invoice line",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "TAKOBI, Odoo Community Association (OCA)",
    "maintainers": ["eLBati"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_landed_costs",
    ],
    "data": [
        "views/account_invoice_views.xml",
    ],
}
