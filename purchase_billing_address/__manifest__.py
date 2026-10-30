# Copyright 2025 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase billing address",
    "summary": """Create a new partner type (purchase), to differentiate
                  the purchase order and invoice addresses.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
}
