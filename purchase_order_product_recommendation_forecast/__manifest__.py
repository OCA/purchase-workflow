# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation Forecast",
    "summary": "Obtain linear progression forecast from reference years",
    "version": "15.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_order_product_recommendation"],
    "data": ["wizards/purchase_order_recommendation_view.xml"],
}
