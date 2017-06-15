# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Vendor Consignment Stock',
 'summary': 'Manage stock in our warehouse that is owned by a vendor',
 'version': '10.0.0.1.0',
 'author': "Camptocamp, Odoo Community Association (OCA)",
 'category': 'Purchases',
 'license': 'AGPL-3',
 'depends': ['stock_ownership_availability_rules',
             'sale_owner_stock_sourcing',
             'sale_stock',
             'purchase',
             ],
 'data': [
     'data/route.xml',
     'view/warehouse.xml',
     'view/purchase_order.xml',
 ],
 "post_init_hook": 'workaround_create_initial_rules',
 'auto_install': False,
 'installable': True,
 }
