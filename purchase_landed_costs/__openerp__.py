# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Ferdinand Gasauer, Joel Grand-Guillaume
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
    'name': 'Purchase Landed Costs',
    'category': 'Warehouse Management',
    'version': '8.0.1.0.1',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'depends': ['purchase'],
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/landed_cost_security.xml',
        'views/purchase_view.xml',
        'data/purchase_landed_costs_data.yml',
    ],
    'test': [
        'test/landed_costs_based_on_quantity.yml',
        'test/landed_costs_based_on_value.yml',
        'test/landed_costs_on_qty_by_line_and_order.yml',
        'test/landed_costs_multicurrency_pricelist.yml',

        # those 2 tests here fails because of the bug regarding the price_type
        # (https://bugs.launchpad.net/ocb-addons/+bug/1238525)
        # and average price
        # computation in OpenERP. I'll keep them because
        # The bug is happening when the company has a different currency that
        # the price_type of the standard_price field
        # Unless you didn't have to do that, everything work fine.
        # they should be sovled by a way or another.
        'test/landed_costs_multicurrency_company.yml',
        'test/landed_costs_multicurrency_pricetype.yml',
    ],
    'demo': [],
    'installable': False,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
