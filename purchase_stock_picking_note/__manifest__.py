# Copyright 2023 ArcheTI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Stock Picking Note",
    "summary": "Add picking note in purchase order",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ArcheTI, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
