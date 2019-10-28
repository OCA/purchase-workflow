# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Agreement from RFQs",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "summary": "Create Purchase Agreement from RFQs",
    "depends": [
        "purchase_requisition",
    ],
    "data": [
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
    ],
    "installable": True,
    "maintainers": ["ps-tubtim"],
    "development_status": "Alpha",
}
