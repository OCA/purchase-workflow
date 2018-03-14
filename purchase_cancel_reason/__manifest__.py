# -*- coding: utf-8 -*-
# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Purchase Cancel Reason',
 'version': '10.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA), Okia SPRL",
 'category': 'Purchase',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'website': "https://github.com/OCA/purchase-workflow",
 'depends': [
     'purchase'],
 'data': ['wizard/purchase_cancel_reason_view.xml',
          'views/purchase_order.xml',
          'security/ir.model.access.csv',
          'data/purchase_order_cancel_reason.xml',
          ],
 'auto_install': False,
 'installable': True,
 }
