# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Line Vendor Comment",
    "summary": """Add the vendor comment field in purchase order lines""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_views.xml",
        "reports/purchase_order_templates.xml",
        "reports/purchase_quotation_templates.xml",
    ],
    "installable": True,
}
