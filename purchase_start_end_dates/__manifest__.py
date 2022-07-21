# Copyright 2022 elego Software Solutions, Germany (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Start End Dates",
    "version": "12.0.1.0.0",
    "category": "Purchase",
    "license": "AGPL-3",
    "summary": "Adds start date and end date on purchase order lines",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
        "account_invoice_start_end_dates"
        ],
    "data": [
        "views/purchase_order.xml",
    ],
    "installable": True,
}
