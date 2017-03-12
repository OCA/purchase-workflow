# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Request to Call for Bids",
    "version": "8.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com/",
    "category": "Purchase Management",
    "depends": [
        "purchase_request_procurement",
        "purchase_requisition",
        "purchase_request_to_rfq",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
    ],
    "license": 'AGPL-3',
    "installable": True
}
