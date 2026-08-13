# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Request Smart Button",
    "summary": "Reach the purchase requests behind an RFQ or a vendor bill",
    "version": "16.0.1.0.0",
    "category": "Purchase Management",
    "author": "PopSolutions, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase_request"],
    "data": [
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["marcos-mendez"],
}
