# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Secondary Unit",
    "summary": "Purchase product in a secondary unit",
    "version": "15.0.1.0.1",
    "development_status": "Beta",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["purchase", "product_secondary_unit"],
    "data": [
        "views/product_views.xml",
        "views/purchase_order_views.xml",
        "reports/purchase_order_templates.xml",
        "reports/purchase_quotation_templates.xml",
    ],
}
