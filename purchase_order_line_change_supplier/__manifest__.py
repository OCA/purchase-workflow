# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Order Line Change Supplier',
    'version': '10.0.1.0.0',
    'author': "PlanetaTIC, Odoo Community Association (OCA)",
    'category': 'Purchase',
    'description': '''This module permits to change supplier of purchase order
 line, moving selected lines of a purchase order to a new purchase order
 of selected supplier.''',
    'depends': [
        'purchase',
    ],
    'website': 'https://github.com/OCA/purchase-workflow',
    'data': [
        'views/purchase_view.xml',
        'wizard/change_purchase_line_supplier_view.xml',
    ],
    'test': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
