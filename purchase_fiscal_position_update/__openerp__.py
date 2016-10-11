# -*- coding: utf-8 -*-
# Copyright 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2014 Akretion (http://www.akretion.com)
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Fiscal Position Update',
    'version': '9.0.1.0.0',
    'category': 'Purchase Management',
    'license': 'AGPL-3',
    'summary': 'Changing the fiscal position of a purchase order will '
    'auto-update purchase order lines',
    'description': """
Purchase Fiscal Position Update
===============================

With this module, when a user changes the fiscal position of a purchase order,
the taxes on all the purchase order lines which have a product are
automatically updated. The purchase order lines without a product are not
updated and a warning is displayed to the user in this case.
""",
    'author': "Julius Network Solutions,"
              "Akretion,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    'depends': ['purchase'],
    'data': [],
    'installable': True,
}
