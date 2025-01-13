# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase service picking",
    "version": "14.0.1.0.0",
    "category": "Purchase",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "maintainers": ["victoralmau"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence_data.xml",
        "views/purchase_order_views.xml",
        "wizards/service_picking_return_views.xml",
        "views/service_picking_views.xml",
        "wizards/service_immediate_transfer_views.xml",
        "wizards/service_backorder_confirmation_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
