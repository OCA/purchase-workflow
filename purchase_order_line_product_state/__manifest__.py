# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Product State",
    "summary": """
        Allows to display the product state on purchase order line level""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "product_state",
        "purchase",
    ],
    "data": [
        "views/purchase_order.xml",
    ],
}
