# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


{
    'name': 'purchase_quick_price_wizard',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': "Florent de Labarre",
    'summary': 'Purchase quick price wizard',
    'category': 'Purchase',
    'website': 'www.iguana-yachts.com',
    'depends': ['purchase', 'account'],
    'data': [
        'views/account_invoice.xml',
        'views/purchase_order.xml',
        'views/product_supplierinfo.xml',


    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
