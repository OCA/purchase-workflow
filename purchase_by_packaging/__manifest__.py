# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Purchase By Packaging",
    "summary": "Manage purchase of packaging",
    "version": "13.0.1.5.5",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Ametras, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_order_line_packaging_qty", "product_packaging_type"],
    "data": [
        "views/product_packaging.xml",
        "views/product_packaging_type.xml",
        "views/product_template.xml",
        "views/purchase_order_line.xml",
    ],
}
