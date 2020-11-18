# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance - Late Delivery Fines",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_work_acceptance"],
    "data": [
        "security/security.xml",
        "views/res_config_settings_views.xml",
        "views/work_acceptance_views.xml",
        "views/account_move_views.xml",
    ],
    "maintainers": ["Saran440"],
    "installable": True,
    "development_status": "Alpha",
}
