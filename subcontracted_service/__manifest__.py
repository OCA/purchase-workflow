# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": 'Subcontracted service',
    "summary": 'Subcontracted service',
    "version": "11.0.1.0.1",
    "category": "Purchase",
    "website": "https://odoo-community.org/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        'views/product_template.xml',
        'views/warehouse.xml',
    ],
    "post_init_hook": "post_init_hook",
}
