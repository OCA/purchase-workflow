# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Procurement Purchase Requisition Generation",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "version": "17.0.1.0.0",
    "depends": ["purchase_requisition_stock"],
    "license": "AGPL-3",
    "category": "Purchase Management",
    "installable": True,
    "maintainers": ["victoralmau"],
    "data": [
        "views/product_template_views.xml",
        "views/purchase_requisition_views.xml",
    ],
}
