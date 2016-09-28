# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Purchase order lines with sequence number',
    'version': '9.0.1.0.1',
    'category': 'Purchase Management',
    'author': "Camptocamp, "
              "Eficent, "
              "Serpent CS, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'depends': [
        'purchase',
        'stock_picking_line_sequence',
        'account_invoice_line_sequence',
    ],
    'data': ['views/purchase_view.xml',
             'views/report_purchaseorder.xml',
             'views/report_purchasequotation.xml'],
    'installable': True,
    'auto_install': False,
    'license': "AGPL-3",
}
