# -*- coding: utf-8 -*-
# © 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Purchase Fiscal Position Update',
    'version': '10.0.1.0.0',
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
              "Odoo Community Association (OCA)",
    'depends': ['purchase'],
    'installable': True,
}
