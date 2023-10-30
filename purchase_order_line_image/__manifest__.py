# Copyright 2022 Ooops - Ashish Hirpara <ashish.hirapara1995@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Image",
    "summary": """Order Line Product Image In Purchase Order.""",
    "author": "ooops404, Ashish Hirapara, Odoo Community Association (OCA), Cetmix",
    "version": "14.0.1.0.1",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "data": [
        "reports/purchase_order_report.xml",
        "views/res_config_settings.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
