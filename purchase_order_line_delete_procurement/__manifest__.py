# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase order lines delete procurement',
    'summary': """
Delete procurement order type buy when purchase_order_line is removed.
Convert destination move from mto to mts.
    """,
    'version': '10.0.1.0.0',
    'category': 'Purchase Management',
    'author': 'PlanetaTIC, Odoo Community Association (OCA)',
    'website': 'https://www.planetatic.com',
    'depends': [
        'purchase',
    ],
    'data': [
        "views/sale_views.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': "AGPL-3",
}
