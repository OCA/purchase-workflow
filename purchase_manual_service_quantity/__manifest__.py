# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Manual Service Quantity',
    'summary': """
        Allow to Manually set received quantities for product service on
        purchase order""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/product_template.xml',
        'views/purchase_order.xml',
    ],
    'demo': [
    ],
}
