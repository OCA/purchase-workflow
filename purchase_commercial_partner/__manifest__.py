# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Commercial Partner',
    'version': '10.0.1.0.0',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': "Add stored related field 'Commercial Supplier' on POs",
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['purchase'],
    'data': [
        'views/purchase.xml',
    ],
    'installable': True,
}
