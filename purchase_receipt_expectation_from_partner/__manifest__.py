# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Receipt Expectation From Partner",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "data": [
        "views/res_partner.xml",
    ],
    "depends": [
        "purchase_receipt_expectation",
    ],
    "installable": True,
    # High sequence to make sure other ``purchase_receipt_expectation*`` are
    # already properly installed/upgraded before this module
    "sequence": 9999,
}
