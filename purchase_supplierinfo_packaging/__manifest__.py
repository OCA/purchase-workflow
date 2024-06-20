# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Supplierinfo Packaging",
    "summary": """
        Allow to use the supplier info packaging when creating a purchase order""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        # product-attribute
        "product_supplierinfo_packaging",
        # ODOO
        "purchase",
    ],
    "data": [],
    "demo": [],
}
