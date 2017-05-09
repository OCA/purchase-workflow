# coding: utf-8
# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Quick Purchase order',
    'version': '8.0.1.0.0',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Purchase',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
}
