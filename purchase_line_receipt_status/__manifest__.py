# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Line Receipt Status",
    "summary": """Track receipt status on purchase order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order_line.xml",
        "views/purchase_order.xml",
    ],
    "maintainers": ["lmignon"],
    "demo": [],
    "additional_dependencies": {
        "python": ["odoo-upgrade"],
    },
    "pre_init_hook": "pre_init_hook",
}
