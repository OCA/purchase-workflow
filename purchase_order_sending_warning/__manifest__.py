# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Sending Warning",
    "version": "14.0.1.0.0",
    "summary": "Adds a warning flag when sending purchase orders fails",
    "category": "Purchases",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase", "mail"],
    "data": [
        "views/purchase_order.xml",
    ],
    "installable": True,
}
