# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Add Product Supplierinfo',
    'summary': 'In the purchase order, '
    'allow automatically complete with partner, '
    'the supplierinfo list for all products '
    'which are not related to this supplier',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    'website': 'http://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'purchase',
        'product_variant_supplierinfo'
    ],
    'data': [
        'purchase_view.xml',
        'wizard/purchase_add_supplierinfo.xml'
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/purchase_order_demo.xml',
    ],
}
