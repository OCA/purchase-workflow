# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request to RFQ",
    "author": "Eficent, "
              "Acsone SA/NV,"
              "Odoo Community Association (OCA)",
    "version": "9.0.1.0.0",
    "website": "http://www.eficent.com/",
    "category": "Purchase Management",
    "depends": [
        "purchase_request",
        "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_order_view.xml",
    ],
    "license": 'AGPL-3',
    "installable": True
}
