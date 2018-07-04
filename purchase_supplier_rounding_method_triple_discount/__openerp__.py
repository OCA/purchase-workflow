# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Supplier Rounding Method - Triple Discount - Glue Module',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'purchase_supplier_rounding_method',
        'account_invoice_triple_discount',
    ],
    'installable': True,
    'auto_install': True,
}
