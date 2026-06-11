# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Stock Line Sequence",
    "summary": "Propagates the purchase order line sequence to stock moves",
    "version": "18.0.2.0.0",
    "category": "Purchase Management",
    "author": "Camptocamp, "
    "ForgeFlow, "
    "Serpent CS, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": [
        "purchase_order_line_sequence",
        "stock_picking_line_sequence",
    ],
    "installable": True,
    "auto_install": True,
    "license": "AGPL-3",
}
