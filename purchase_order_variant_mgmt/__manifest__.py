# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Handle easily multiple variants on Purchase Orders',
    'summary': 'Handle the addition/removal of multiple variants from '
               'product template into the purchase order',
    'version': '11.0.1.0.0',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'category': 'Purchases',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/purchase-workflow',
    'depends': [
        'purchase',
        'web_widget_x2many_2d_matrix',
    ],
    'data': [
        'wizard/purchase_manage_variant_view.xml',
        'views/purchase_order_view.xml',
    ],
}
