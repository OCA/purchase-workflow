# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Request To Procurement',
    'summary': """
        This module introduces the possiblity to
        create procurement order from purchase request""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu/',
    'depends': [
        # Odoo
        'procurement',
        'stock',
        # OCA purchase-workflow
        'purchase_request',
    ],
    'data': [
        'wizards/purchase_request_line_make_procurement_order.xml',
        'views/purchase_request.xml',
    ],
}
