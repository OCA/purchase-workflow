# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Receipt Expectation - Manual",
    "version": "15.0.1.0.1",
    "category": "Purchase Management",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
        "wizards/purchase_order_manual_receipt.xml",
    ],
    "depends": [
        "purchase_receipt_expectation",
    ],
    "installable": True,
}
