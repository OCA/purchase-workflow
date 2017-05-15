# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ecosoft (<http://www.ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase - Separate Quote and Order',
    'version': '10.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Purchase',
    'website': 'http://ecosoft.co.th',
    'depends': ['purchase', ],
    'images': [],
    'data': [
        'data/ir_sequence_data.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'post_init_hook': 'post_init_hook',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
