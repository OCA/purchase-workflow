# Copyright 2026 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Auto Bill on Receipt",
    "summary": "Automatically create and post Vendor Bills when receipts are validated",
    "version": "19.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "depends": ["purchase_stock"],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/purchase_order_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
