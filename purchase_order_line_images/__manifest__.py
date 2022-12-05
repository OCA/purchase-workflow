# Copyright 2022 Ooops - Ashish Hirpara <ashish.hirapara1995@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Images",
    "version": "14.0.1.0.0",
    "author": "ooops404, Ashish Hirapara, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "summary": """Order Line Product Images In Purchase Order.""",
    "data": [
        "reports/purchase_order_report.xml",
        "views/res_config_settings.xml",
        "views/purchase_order_view.xml",
    ],
    "depends": ["purchase"],
    "installable": True,
}
