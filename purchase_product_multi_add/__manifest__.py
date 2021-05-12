# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Product Multi Add",
    "summary": """
        This module extends the functionality of purchase module and allow you
        to import multiple products into your current purchase order.""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": ["wizards/purchase_import_products_views.xml", "views/purchase_view.xml"],
}
