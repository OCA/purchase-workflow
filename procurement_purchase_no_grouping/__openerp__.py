# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza (http://www.serviciosbaeza.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Procurement Purchase No Grouping',
    'version': '8.0.1.0.1',
    'license': 'AGPL-3',
    'author':
        'Odoo Community Association (OCA), '
        'OdooMRP team,'
        'AvanzOSC,'
        'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    'website': 'http://github.com/oca/purchase-workflow',
    'category': 'Procurements',
    'depends': [
        'purchase',
        'procurement',
    ],
    'data': [
        'views/product_category_view.xml',
    ],
    'installable': True
}
