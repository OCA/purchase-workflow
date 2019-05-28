# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Packaging",
    "version": "12.0.1.0.0",
    "author": 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    "category": "Purchases",
    "development_status": "Production/Stable",
    "maintainers": ["rousseldenis"],
    "website": "http://github.com/OCA/purchase-workflow",
    "summary": "In purchases, use product packages",

    "depends": [
        "uom",
        "product",
        "purchase",
        "packaging_uom",
    ],
    "data": [
        "views/product_supplier_info_view.xml",
        "views/purchase_order_view.xml",
        "views/purchase_order_line_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "installable": True,
}
