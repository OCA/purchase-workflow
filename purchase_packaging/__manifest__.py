# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Packaging",
    "version": "14.0.1.0.0",
    "author": "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "website": "https://github.com/OCA/purchase-workflow",
    "summary": "In purchase, use package",
    "depends": ["product", "purchase", "packaging_uom", "stock", "purchase_stock"],
    "data": [
        "views/product_supplier_info_view.xml",
        "views/purchase_order_view.xml",
        "views/purchase_order_line_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "installable": True,
}
