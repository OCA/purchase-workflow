# Copyright 2025 Juan Alberto Raja<juan.raja@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product Supplierinfo Disable Autocreation",
    "version": "17.0.1.0.0",
    "category": "Purchase",
    "summary": "Add option to disable automatic creation of pricelists for suppliers",
    "author": "Sygel, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
