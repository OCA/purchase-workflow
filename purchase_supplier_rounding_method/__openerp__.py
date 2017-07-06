# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Supplier Rounding Method',
    'version': '8.0.1.0.0',
    'category': 'Purchase Management',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'purchase_discount',
    ],
    'data': [
        'views/view_res_partner.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/account_invoice.xml',
        'demo/purchase_order.xml',
    ],
    'installable': True,
}
