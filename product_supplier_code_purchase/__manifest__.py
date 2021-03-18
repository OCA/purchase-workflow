# Copyright 2015-20 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Supplier Code in Purchase",
    "summary": """This module adds to the purchase order line the supplier
                code defined in the product.""",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
