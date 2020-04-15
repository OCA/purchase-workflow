# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Order Mass Cancel',
    'version': '10.0.1.0.0',
    'summary':
        'Permits users to cancel multiple purchase order in draft state',
    'category': 'Purchases',
    'author': 'PlanetaTIC, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/purchase-workflow',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
    ],
    'data': [
        'wizard/purchase_mass_cancel_view.xml',
    ],
    'demo': [],
    'installable': True,
}
