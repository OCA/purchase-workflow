# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    "name": "Purchase Request",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "version": "8.0.1.1.0",
    "contributors": [
        'Jordi Ballester Alomar',
    ],
    "category": "Purchase Management",
    "depends": [
        "purchase",
        "product"
    ],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "views/purchase_request_view.xml",
        "reports/report_purchaserequests.xml",
        "views/purchase_request_report.xml",
    ],
    'demo': [
        "demo/purchase_request_demo.xml",
    ],
    "license": 'AGPL-3',
    "installable": True
}
