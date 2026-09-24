# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Tag",
    "summary": """This module allows to put purchase tags on routes and
    reflect them on purchase order lines""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_tag",
        "purchase_stock",
    ],
    "data": ["views/stock_route.xml"],
}
