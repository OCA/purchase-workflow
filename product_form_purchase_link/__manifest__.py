# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Form Purchase Link",
    "summary": """
        Add an option to display the purchases lines from product""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "views/purchase_order_line.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
    "installable": True,
}
