# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation",
    "summary": "Recommend products to buy to supplier based on history",
    "version": "16.0.1.1.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/purchase_order_recommendation_view.xml",
        "views/purchase_order_view.xml",
    ],
}
