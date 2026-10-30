# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase Order Stage",
    "summary": "Adds the concept of customizable stages to purchase orders",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC," "Odoo Community Association (OCA)",
    "maintainers": ["MiguelPoyatos"],
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": [
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_stage_views.xml",
        "views/purchase_order_views.xml",
    ],
}
