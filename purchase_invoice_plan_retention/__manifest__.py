# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Invoice Plan - Retention",
    "summary": "Add to purchase invoice plan, the retention on each invoice",
    "version": "14.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "depends": ["purchase_invoice_plan", "account_invoice_payment_retention"],
    "data": [
        "views/purchase_view.xml",
    ],
    "installable": True,
    "auto_install": True,
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
}
