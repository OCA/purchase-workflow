# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Partner Conditions",
    "summary": "Adds a new terms and condition field on partner for purchases",
    "version": "17.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "maintainers": ["tisho99"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/res_config_settings.xml",
    ],
}
