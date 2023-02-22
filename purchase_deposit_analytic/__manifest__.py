# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Deposit - Analytic",
    "summary": "Add analytic on wizard register deposit",
    "version": "15.0.1.0.0",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_deposit"],
    "data": [
        "wizard/purchase_make_invoice_advance_views.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
