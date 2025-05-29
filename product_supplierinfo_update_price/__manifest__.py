# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Supplierinfo Update Price",
    "summary": """Updates the product's vendor price with the price
    set in a purchase order.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
        "product",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "demo": [],
}
