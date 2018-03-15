# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Purchase Picking address',
    'summary': 'Allows to create and address on pickings that will be used on '
               'Purchases',
    'version': '11.0.1.0.0',
    'license': 'LGPL-3',
    'website': 'https://github.com/purchase-workflow',
    'author': 'Creu Blanca, '
              'Odoo Community Association (OCA)',
    'category': 'Purchase Management',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
}
