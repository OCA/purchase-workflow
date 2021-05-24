# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Invoice Plan - Expand Product Lines by Group",
    "summary": "Add ability to expand product line by group in invoice plan",
    "version": "14.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "depends": ["purchase_invoice_plan"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_view.xml",
    ],
    "installable": True,
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
}
