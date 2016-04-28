# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Camptocamp SA
#    Author: Leonardo Pistone
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

{"name": "Purchase Requisition Transport Document",
 "summary": "Add Transport Documents to Purchase Requisitions",
 "version": "8.0.0.1.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "easy",
 "description": """
Purchase Requisition Transport Document
=======================================
This module extends the purchase_transport_module allowing to add Transport
Documents to Purchase Requisitions as well. See the description of that module
for more information and demo data.
""",
 "depends": ["purchase_transport_document",
             "purchase_requisition",
             ],
 "data": ["view/purchase_requisition.xml",
          ],
 "installable": True,
 }
