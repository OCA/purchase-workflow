# Copyright 2020 - TODAY, Escodoo
# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Default Terms Conditions",
    "summary": """
        This module allows purchase default terms & conditions""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "images": ["static/description/banner.png"],
    "depends": [
        "purchase",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
    ],
}
