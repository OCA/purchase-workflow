# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "purchase_free_shipping",
    'summary': """
        Purchase Free Shipping """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Purchases Management',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/res_partner_view.xml',
    ],
}
