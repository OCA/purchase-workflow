# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Camptocamp SA
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

{"name": "Purchase Requisition Auto RFQ",
 "summary": "Automatically create RFQ from a purchase requisition",
 "version": "8.0.0.2.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "normal",
 "images": [],
 "description": """
Purchase Requisition Auto RFQ
=============================

This module adds a button on the purchase requisition form to create a RFQ
using the suppliers from the products listed in the requisition.

Note: nose is required to run the tests. It is not listed as en external
dependency because it is not needed in production.

""",
 "depends": ["purchase_requisition",
             ],
    "demo": ['demo/product_and_supplier.yml',
             ],
    "data": ["view/purchase_requisition.xml",
             ],
    "auto_install": False,
    "test": ["test/purchase_requisition.yml",
             "test/purchase_requisition_no_supplier.yml",
             ],
    "installable": True,
    "certificate": "",
 }
