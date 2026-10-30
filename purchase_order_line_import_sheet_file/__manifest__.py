# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Line Import",
    "summary": "Import purchase order lines from a spreadsheet",
    "version": "17.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase", "base_import"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/purchase_order_line_import_views.xml",
        "views/purchase_order_views.xml",
    ],
}
