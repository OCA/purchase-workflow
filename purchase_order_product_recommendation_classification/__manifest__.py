# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase recommendations according to sales classification",
    "summary": "Extends the purchase recomendator with classification filters",
    "version": "12.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "purchase_order_product_recommendation",
        "sale_product_classification",
    ],
    "data": [],
}
