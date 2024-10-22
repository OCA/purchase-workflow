# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Line Stock Move Cancel",
    "summary": """
        Allows to cancel stock move lines from purchase lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_stock",
        "base_partition",
    ],
    "data": [
        "security/security.xml",
        "views/purchase_order_line.xml",
        "wizards/purchase_order_line_stock_move_cancel.xml",
    ],
}
