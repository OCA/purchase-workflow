# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Purchase product on weight',
    'version': '10.0.1.0.5',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'author': 'Sergio Corato, Odoo Community Association (OCA)',
    'website': 'https://efatto.it',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase.xml',
        'views/product.xml',
        'views/product_supplierinfo.xml',
    ],
    'installable': True,
}
