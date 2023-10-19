# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Invoice Method",
    "summary": """
        Allow to force the invoice method of a purchase""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "views/purchase_order.xml",
    ],
    "demo": [],
}
