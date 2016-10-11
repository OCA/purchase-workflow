# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2014-2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Purchase order lines with discounts",
    "author": "Tiny, "
              "Acysos S.L., "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "AvanzOSC, S.L., "
              "Odoo Community Association (OCA)",
    "version": "8.0.1.1.0",
    "contributors": [
        'Pedro M. Baeza',
        'Ainara Galdona'
    ],
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
    "installable": True
}
