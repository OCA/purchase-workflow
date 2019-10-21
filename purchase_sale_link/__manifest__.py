# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Purchase Sale Link',
    'version': '12.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Purchase Management',
    'depends': [
        'sale_purchase',
        'purchase_stock',
    ],
    'website': 'https://github.com/OCA/purchase-workflow',
    'data': [
        'views/purchase_order.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}
