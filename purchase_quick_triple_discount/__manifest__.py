# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Quick Triple Discount",
    "version": "16.0.1.0.0",
    "category": "Purchase",
    "summary": "Glue module to add discount fields for quick purchase",
    "author": "GRAP, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain", "quentinDupont"],
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": [
        # OCA
        "purchase_quick_discount",
        "purchase_triple_discount",
    ],
    "data": ["views/view_product_product.xml"],
    "installable": True,
}
