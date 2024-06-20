# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Vendor Promotion",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Purchase Management",
    "summary": "Purchase Vendor Promotion",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase_stock"],
    "data": [
        "views/product_views.xml",
        "views/stock_orderpoint_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
