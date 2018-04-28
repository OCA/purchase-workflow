# Copyright 2016 Chafique DELLI @ Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Purchase Picking State',
    'version': '11.0.1.0.0',
    'author': 'Akretion, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Purchase Management',
    'website': 'https://github.com/OCA/purchase-workflow',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_view.xml',
    ],
    'installable': True,
}
