# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation Brand Filter",
    "summary": "Allow to filter recommendations by brand",
    "version": "12.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_order_product_recommendation",
        "product_brand",
    ],
    "data": [
        "wizards/purchase_order_recommendation_view.xml",
    ],
}
