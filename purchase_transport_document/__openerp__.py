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

{"name": "Purchase Transport Document",
 "summary": "Add a new Transport Document object in the Purchase Order",
 "version": "0.1",
 "author": "Camptocamp",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "easy",
 "description": """
Purchase Transport Document
===========================
This module adds a new object "Transport Document" and allows to select
Documents in Purchase Orders. Other modules can depend on this simple one to
use the same documents.

This way it is possible to specify which documents have to be supplied with the
purchase. Possible examples (CMR, Bill of Langand and others) are provided as
demo data.
""",
 "depends": ["purchase",
             ],
 "data": ["view/purchase_order.xml",
          "view/transport_document.xml",
          "security/ir.model.access.csv",
          "data/transport_document.xml",
          ],
 "installable": True,
 }
