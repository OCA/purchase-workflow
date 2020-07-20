# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance Invoice Plan",
    "version": "13.0.1.0.0",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_work_acceptance", "purchase_invoice_plan"],
    "data": [
        "wizard/select_work_acceptance_invoice_plan_wizard_views.xml",
        "views/purchase_views.xml",
        "views/work_acceptance_view.xml",
    ],
    "maintainer": ["Niaisoh"],
    "installable": True,
    "auto_install": True,
    "development_status": "Alpha",
}
