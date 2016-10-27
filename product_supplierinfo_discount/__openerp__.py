# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Discounts in product supplier info",
    "version": "9.0.1.0.0",
    "author": "Tecnativa - Pedro M. Baeza, "
              "Akretion - Julien Weste, "
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "www.serviciosbaeza.com",
    "license": "AGPL-3",
    "depends": [
        'product',
        'purchase_discount',
    ],
    "data": [
        'views/product_supplierinfo_view.xml',
    ],
    'installable': True,
}
