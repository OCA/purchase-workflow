# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Invoice Plan - Deposit on 1st invoice",
    "summary": "Add to purchase invoice plan, the deposit invoice",
    "version": "14.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "depends": ["purchase_invoice_plan", "purchase_deposit"],
    "data": [
        "wizard/purchase_create_invoice_plan_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
    "auto_install": True,
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
}
