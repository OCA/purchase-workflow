# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Invoice Plan",
    "summary": "Add to purchases order, ability to manage future invoice plan",
    "version": "16.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "depends": ["purchase_open_qty", "purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/purchase_data.xml",
        "wizard/purchase_create_invoice_plan_view.xml",
        "wizard/purchase_make_planned_invoice_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
}
