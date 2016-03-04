# -*- coding: utf-8 -*-
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (c) 2014-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase order lines with discounts",
    "author": "Tiny, "
              "Acysos S.L., "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "version": "9.0.1.0.0",
    "category": "Purchase Management",
    "depends": [
        "stock",
        "purchase",
    ],
    "data": [
        "views/purchase_discount_view.xml",
        "views/report_purchaseorder.xml",
    ],
    "license": 'AGPL-3',
    'installable': True
}
