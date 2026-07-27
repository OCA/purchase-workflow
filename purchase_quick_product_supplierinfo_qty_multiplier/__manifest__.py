# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Quick with Supplierinfo Multiplier",
    "version": "16.0.1.0.1",
    "category": "Purchase",
    "summary": "Glue module to add multiplier fields for quick purchase",
    "author": "GRAP, Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain", "quentinDupont"],
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": [
        # OCA
        "purchase_quick",
        "product_supplierinfo_qty_multiplier",
        "web_tree_dynamic_colored_field",
    ],
    "data": ["views/view_product_product.xml"],
    "installable": True,
}
