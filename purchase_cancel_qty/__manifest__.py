# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Cancel Quantity',
    'summary': """
        Allow purchase users to define cancelled quantity on
        purchase order lines""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order.xml',
        'views/purchase_order_line.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
