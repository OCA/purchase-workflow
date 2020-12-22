# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Account Journal Modification",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": "Remove default expense account for vendor bills journal",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["account"],
    "category": "Accounting/Accounting",
    "data": [
        "views/account_journal_views.xml",
    ],
    "installable": True,
}
