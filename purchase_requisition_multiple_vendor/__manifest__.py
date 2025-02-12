# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Requisition Multiple Vendor",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Sygel, Odoo Community Association (OCA)",
    "category": "Purchase",
    "summary": """
        Create multiple purchase alternatives for different vendors
        using the same wizard.""",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_requisition",
    ],
    "data": [
        "wizard/purchase_requisition_create_alternative.xml",
    ],
}
