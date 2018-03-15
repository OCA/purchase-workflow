# -*- coding: utf-8 -*-
# Copyright 2017 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Line Product Image",
    "summary": "Show Product Image at Purchase Order Line.",
    "version": "10.0.1.0.0",
    "author": "Lucky Kurniawan, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchases",
    "depends": ['purchase', 'web_tree_image'],
    "data": [
        'views/purchase_order_views.xml',
    ],
    'qweb': ['static/src/xml/widget.xml', ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
