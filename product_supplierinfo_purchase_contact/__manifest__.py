# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Supplier Purchase Contact",
    "version": "16.0.1.0.0",
    "category": "Purchase Management",
    "author": "Tecnativa,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "summary": "Add Purchase Contact in product supplier info",
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "views/product_supplierinfo_view.xml",
    ],
    "installable": True,
}
