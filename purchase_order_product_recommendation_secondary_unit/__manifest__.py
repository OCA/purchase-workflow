# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation Secondary Unit",
    "summary": "Add secondary unit to recommend products wizard",
    "version": "11.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_order_product_recommendation",
        "purchase_order_secondary_unit",
    ],
    "data": [
        "wizards/purchase_order_recommendation_view.xml",
    ],
}
