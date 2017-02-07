# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Free-Of-Paiment shipping",
    'version': '1.1',
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': 'Akretion',
    'license': 'AGPL-3',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': ['purchase'],
    'website': 'http://www.akretion.com/',
    'data': ['views/purchase_view.xml',
             'views/partner_view.xml',
             ],
    'tests': [],
    'installable': True,
    'auto_install': False,
}
