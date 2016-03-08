# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Picking State',
    'summary': 'Add picking status in purchase order',
    'version': '8.0.0.1.0',
    'category': 'Purchase Management',
    'website': 'http://akretion.com',
    'author': 'Akretion',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'purchase',
    ],
    'data': [
        'purchase_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ]
}
