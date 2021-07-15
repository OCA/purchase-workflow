# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vendor Evaluation Report",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_work_acceptance_evaluation"],
    "data": [
        "security/ir.model.access.csv",
        "report/vendor_evaluation_report.xml",
    ],
    "maintainers": ["newtratip"],
    "installable": True,
    "development_status": "Alpha",
}
