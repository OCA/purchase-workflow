# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation",
    "summary": "Recommend products to buy to supplier based on history",
    "version": "11.0.3.0.1",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "wizards/purchase_order_recommendation_view.xml",
        "views/purchase_order_view.xml",
    ],
}
