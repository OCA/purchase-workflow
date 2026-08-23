# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Supplier Info — Active Products Performance Filter",
    "summary": (
        "Denormalizes product.active onto product.supplierinfo so the "
        "'Active Products' search filter runs without any JOIN."
    ),
    "version": "18.0.1.0.0",
    "author": "Odoo Community Association (OCA), ACSONE SA/NV",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": [
        "product",
    ],
    "data": ["views/product_supplierinfo_views.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
