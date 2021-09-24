# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Return",
    "summary": "Manage return orders.",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "security/purchase_security.xml",
        "data/purchase_data.xml",
        "views/purchase_views.xml",
        "views/account_move_views.xml",
        "views/purchase_return_template.xml",
        "report/purchase_reports.xml",
        "report/purchase_return_order_templates.xml",
        "data/mail_template_data.xml",
    ],
}
