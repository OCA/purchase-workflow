# -*- coding: utf-8 -*-
# © # © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

{
    'name': 'Purchase Delivery',
    'version': '1.0',
    'category': 'Purchase Management',
    'sequence': 10,
    'summary': 'Add delivery to purchase order and purchase invoice.',
    'author': 'ClearCorp, Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'depends': ['purchase', 'delivery'],
    'data': ['purchase_delivery_view.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
