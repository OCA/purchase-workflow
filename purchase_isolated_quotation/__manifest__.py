# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase - Separate Quote and Order',
    'version': '10.0.1.0.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Purchase',
    'website': 'http://ecosoft.co.th',
    'depends': ['purchase', ],
    'license': 'AGPL-3',
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
