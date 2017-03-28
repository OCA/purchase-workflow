# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Invoice Allowed Product',
    'summary': 'This module allows to select only products that can be '
               'supplied by the supplier',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'website': 'https://akretion.com',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'purchase',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/purchase_order_view.xml',
    ]
}
