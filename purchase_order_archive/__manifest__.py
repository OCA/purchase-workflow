# Copyright 2017-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Order Archive',
    'summary': 'Archive Purchase Orders',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'category': 'Purchases',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True,
}
