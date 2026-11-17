# Copyright 2025 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Invoice Status Partial",
    "summary": """
        Adds a 'Partially Invoiced' status to purchase orders for better invoice tracking.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": ["views/purchase_views.xml"],
}
