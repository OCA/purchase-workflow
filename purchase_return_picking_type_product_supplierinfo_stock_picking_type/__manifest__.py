# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Purchase Return Picking Type Product Supplierinfo Stock Picking Type",
    "summary": "Glue module from purchase_return_picking_type "
    "and product_supplierinfo_stock_picking_type",
    "version": "16.0.1.0.0",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "autoinstall": True,
    "depends": [
        "product_supplierinfo_stock_picking_type",
        "purchase_return_picking_type",
    ],
    "development_status": "Alpha",
}
