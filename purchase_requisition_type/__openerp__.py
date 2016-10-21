# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Requisition Type',
    'version': '8.0.1.0.0',
    'summary': 'Add order type to purchase requisition',
    'author': 'OpenSynergy Indonesia,Odoo Community Association (OCA)',
    'website': 'https://opensynergy-indonesia.com',
    'category': 'Purchase Management',
    'depends': [
        'purchase_requisition',
        'purchase_order_type'
    ],
    'data': ['views/view_purchase_requisition.xml'],
    'installable': True,
    'license': 'AGPL-3',
}
