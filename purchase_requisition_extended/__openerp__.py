# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013 Camptocamp SA
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

{"name": "IFRC Purchase Requisition",
 "version": "0.1",
 "author": "Camptocamp",
 "license": "AGPL-3",
 "category": "Purchase Management",
 "complexity": "normal",
 "images": [],
 "description": """
This module improves the Purchase Requisition.
==============================================

IFRC specific.

""",
 "depends": ["purchase_requisition",
             "stock",  # For incoterm
             "purchase_extended",  # for fields incoterm adress
             ],
 "demo": [],
 "data": ["view/purchase_requisition.xml",
          "view/purchase_order.xml",
          "workflow/purchase_requisition.xml",
          "wizard/modal.xml",
          ],
 "js": [
        "static/src/js/web_addons.js",
        ],
 "auto_install": False,
 "test": [],
 "installable": True,
 "certificate": "",
 }
