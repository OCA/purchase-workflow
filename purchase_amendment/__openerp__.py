# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier, Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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
#


{
    "name": "Purchase Amendment",
    # description is in README.rst
    "version": "0.2",
    "depends": ["purchase",
                "stock_split_picking",
                ],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase Management",
    "installable": True,
    "data": ["view/purchase_order.xml",
             "view/purchase_order_amendment_view.xml",
             "data/purchase_workflow.xml",
             ],
    "test": [],
}
