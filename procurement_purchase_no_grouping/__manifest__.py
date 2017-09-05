# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2017 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Procurement Purchase No Grouping",
    "version": "10.0.1.0.0",
    "author": "AvanzOSC,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Procurements",
    "depends": [
        'purchase',
        'procurement',
    ],
    "data": [
        'views/product_category_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
