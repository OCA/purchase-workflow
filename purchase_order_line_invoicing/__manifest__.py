# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Order Line Invoicing',
    'summary': """
        Invoice purchase order lines""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/res_partner_views.xml',
        'wizards/purchase_order_line_invoicing_wizard.xml',
    ],
}
