# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product supplierinfo qty multiplier",
    "version": "16.0.1.0.0",
    "category": "Inventory/Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Tecnativa,GRAP, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["purchase", "web_notify"],
    "maintainers": ["victoralmau", "legalsylvain"],
    "data": ["views/product_supplierinfo_view.xml"],
    "demo": [
        "demo/res_partner_demo.xml",
        "demo/product_product_demo.xml",
        "demo/product_supplierinfo_demo.xml",
    ],
}
