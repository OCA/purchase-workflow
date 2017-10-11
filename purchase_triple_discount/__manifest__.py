# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Invoice Triple Discount',
    'version': '10.0.1.1.0',
    'category': 'Purchase Management',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://tecnativa.com',
    'license': 'AGPL-3',
    'summary': 'Manage triple discount on purchase order lines',
    'depends': [
        'purchase_discount',
        'account_invoice_triple_discount',
    ],
    'data': [
        'views/purchase_view.xml',
    ],
    'installable': True,
}
