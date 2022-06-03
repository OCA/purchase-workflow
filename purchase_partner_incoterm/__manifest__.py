# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Default purchase incoterm per partner",
    "summary": "Add a an incoterm field for supplier and use it on purchase order",
    "version": "14.0.2.0.0",
    "category": "Purchase",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["TDu", "bealdav"],
    "depends": [
        "account",
        "purchase_stock",
    ],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "views/partner_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
}
