# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Purchase Approved Suppliers",
    "version": "17.0.1.0.0",
    "category": "Purchase",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "LGPL-3",
    "depends": [
        "purchase",
        "product",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/purchase_supplier_approved_views.xml",
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "views/purchase_order_views.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/purchase_supplier_approved_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
