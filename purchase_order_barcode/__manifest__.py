# -*- coding: utf-8 -*-
# © 2017
#   @Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Barcode",
    "summary": "Add Product With Barcode at Purchase Order",
    "version": "10.0.1.0.0",
    "author": "Lucky Kurniawan ",
    "website": "https://github.com/kurniawanlucky/Odoo10.0",
    "category": "Purchase",
    "depends": ['purchase', 'barcodes'],
    "data": [
        'views/purchase_order_views.xml',
        'views/template.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
