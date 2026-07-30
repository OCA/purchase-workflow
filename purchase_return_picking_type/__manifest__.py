# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Return Picking Type",
    "summary": "Manage return orders and operation types.",
    "version": "16.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_return", "purchase_stock"],
    "data": [
        "views/purchase_return_views.xml",
    ],
    "development_status": "Alpha",
}
