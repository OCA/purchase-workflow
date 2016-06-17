# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Variant Supplierinfo By Supplier',
    'summary': 'Replaces the product template by the product variant '
               'in the views of product supplierinfo',
    'version': '8.0.1.0.0',
    'category': 'Purchase',
    'website': 'http://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
    'depends': [
        'product_by_supplier',
        'product_variant_supplierinfo',
    ],
    'data': [
        'views/product_supplierinfo_view.xml',
    ]
}
