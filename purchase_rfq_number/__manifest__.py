# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase For Quotation Numeration",
    "summary": "Different sequence for purchase for quotations",
    "version": "14.0.1.0.0",
    "author": "ProThai, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": ["purchase"],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "data/ir_sequence_data.xml",
        "reports/purchase_report_templates.xml",
        "views/res_config_settings_views.xml",
        "views/purchase_views.xml",
    ],
    "maintainer": ["prapassornS"],
    "installable": True,
    "auto_install": False,
}
