# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier <guewen.baconnier@camptocamp.com>
# Copyright 2016 Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Order Type",
    "version": "9.0.1.1.0",
    "category": "Purchase Management",
    "website": "http://www.camptocamp.com",
    "author": "Camptocamp,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/view_purchase_order_type.xml",
        "views/view_purchase_order.xml",
        "views/res_partner_view.xml",
        "data/purchase_order_type.xml",
    ],
}
