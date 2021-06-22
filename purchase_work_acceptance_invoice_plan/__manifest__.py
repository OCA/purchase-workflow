# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance Invoice Plan",
    "version": "14.0.1.0.1",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_work_acceptance", "purchase_invoice_plan"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/select_work_acceptance_invoice_plan_wizard_views.xml",
        "views/purchase_views.xml",
        "views/work_acceptance_view.xml",
    ],
    "maintainers": ["kittiu"],
    "installable": True,
    "auto_install": True,
    "development_status": "Alpha",
}
