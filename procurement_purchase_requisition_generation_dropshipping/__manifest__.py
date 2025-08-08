# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Procurement purchase requisition dropshipping",
    "version": "17.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["stock_dropshipping", "procurement_purchase_requisition_generation"],
    "data": [
        "views/purchase_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "maintainers": ["carlos-lopez-tecnativa"],
}
