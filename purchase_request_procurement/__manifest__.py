# -*- coding: utf-8 -*-
# Copyright 2016-2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    'name': "Purchase Request Procurement",
    'version': "10.0.1.0.1",
    'author': "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/purchase-workflow",
    'category': "Purchase Management",
    'depends': [
        "purchase_request",
        "procurement",
    ],
    'data': [
        "views/product_template.xml",
        "views/procurement_order.xml",
    ],
    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
}
