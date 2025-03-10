# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Advance Payment Line",
    "version": "17.0.1.0.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "summary": "Allow to add advance payment lines on purchase orders",
    "depends": [
        # odoo
        "purchase",
        # oca/purchase-workflow
        "purchase_advance_payment",
        # oca/bank-payment
        "account_payment_purchase",
        "account_banking_sepa_credit_transfer",
    ],
    "data": [
        # Views
        "views/account_payment.xml",
        "views/account_payment_line.xml",
        "views/purchase_order.xml",
    ],
    "installable": True,
}
