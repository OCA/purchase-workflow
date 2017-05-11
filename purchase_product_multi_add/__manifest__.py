# -*- coding: utf-8 -*-
# © 2016 Denis Roussel, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Purchase Product Multi Add",
    'summary': """
        This module allows a shortcut to add purchase.order.line by selecting
        product into a wizard for the given suplier
    """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Purchase Management',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'wizard/purchase_import_products_view.xml',
        'views/purchase_view.xml',
    ],
}
