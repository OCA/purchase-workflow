# Copyright 2020 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Request Secondary Unit',
    'summary': 'Create requests of product in a secondary unit',
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'website': 'https://github.com/OCA/purchase-workflow',
    'author': 'Jarsa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': [
        'purchase_order_secondary_unit',
        'purchase_request',
    ],
    'data': [
        'views/purchase_request_views.xml',
        'wizard/purchase_request_line_make_purchase_order_view.xml',
    ],
}
