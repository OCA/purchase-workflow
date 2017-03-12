# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Request Procurement",
    "version": "8.0.1.0.0",
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
    "license": 'AGPL-3',
    "installable": True
}
