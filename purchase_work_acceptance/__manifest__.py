# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance",
    "version": "14.0.1.1.1",
    "category": "Purchase Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "data": [
        "data/work_acceptance_sequence.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_move_views.xml",
        "views/purchase_views.xml",
        "views/res_config_settings_views.xml",
        "views/stock_picking_views.xml",
        "views/work_acceptance_views.xml",
        "wizard/select_work_acceptance_wizard_views.xml",
    ],
    "maintainer": ["ps-tubtim"],
    "installable": True,
    "development_status": "Alpha",
}
