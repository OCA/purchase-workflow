# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2017-23 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Subcontracted service",
    "summary": "Subcontracted service",
    "version": "14.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Camptocamp, ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["LoisRForgeFlow"],
    "application": False,
    "installable": True,
    "depends": [
        "purchase_stock",
        "stock_procurement_group_hook",
    ],
    "data": [
        "views/product_template.xml",
        "views/warehouse.xml",
    ],
    "post_init_hook": "post_init_hook",
}
