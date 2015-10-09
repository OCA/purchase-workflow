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

{"name": "Purchase Requisition Auto RFQ / Bid Selection bridge",
 "summary": "Bridge module for PR Auto RFQ / Bid Selection",
 "version": "8.0.0.1.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "normal",
 "images": [],
 "depends": ["purchase_requisition_auto_rfq",
             "purchase_requisition_bid_selection",
             ],
 "data": ['view/purchase_requisition.xml',
          ],
 "test": ['test/purchase_requisition.yml',
          ],
 "auto_install": True,
 "installable": True,
 "certificate": "",
 }
