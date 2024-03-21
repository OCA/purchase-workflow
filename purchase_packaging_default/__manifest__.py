# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Packaging Default",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchase Management",
    "summary": "Set default packaging in purchase",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
