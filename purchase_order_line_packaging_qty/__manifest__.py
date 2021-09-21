# Copyright 2020 Camptocamp SA
# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Purchase Order Line Packaging Quantity",
    "summary": "Define quantities according to product packaging"
    " on purchase order lines",
    "version": "12.0.1.1.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_stock", "stock_move_packaging_qty"],
    "data": ["views/purchase_order.xml", "views/product_product.xml"],
}
