# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Main Vendor",
    "summary": "Main Vendor for a product",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "author": "GRAP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["purchase"],
    "maintainers": ["legalsylvain", "quentinDupont"],
    "data": [
        "views/view_product_product.xml",
        "views/view_product_template.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
