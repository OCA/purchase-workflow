# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request Group by Date",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "summary": "Use this module to group request for same product by date",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase_request", "stock", "product", "purchase_stock"],
    "data": [
        "views/res_config_settings.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
