# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Product Recommendation XLSX",
    "summary": "Add a way to print recommended products for supplier",
    "version": "15.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_order_product_recommendation", "report_xlsx"],
    "data": [
        "wizards/purchase_order_recommendation_view.xml",
        "report/recommendation_xlsx.xml",
    ],
}
