# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request Procurement",
    "version": "9.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com/",
    "category": "Purchase Management",
    "depends": ["purchase_request", "procurement"],
    "data": [
        "views/product_view.xml",
        "views/procurement_view.xml",
    ],
    'demo': [],
    'test': [
        "test/purchase_request_from_procurement.yml",
    ],
    "license": 'LGPL-3',
    "installable": True
}
