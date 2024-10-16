# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Subcontracted service for a Product",
    "summary": "Subcontracted service for a Product",
    "version": "15.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Camptocamp, ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["AaronHForgeFlow"],
    "application": False,
    "installable": True,
    "depends": [
        "subcontracted_service",
    ],
    "data": ["views/product_template.xml", "views/warehouse.xml"],
    "post_init_hook": "post_init_hook",
}
