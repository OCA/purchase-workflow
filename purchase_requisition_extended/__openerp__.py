# -*- coding: utf-8 -*-
#
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
#

{"name": "Purchase Requisition Extended",
 "version": "0.1",
 "author": "Camptocamp",
 "license": "AGPL-3",
 "category": "Purchase Management",
 "complexity": "normal",
 "images": [],
 "description": """
Purchase Requisition improvements
=================================

This module allows to make calls for bids by generating an RFQ for selected
suppliers, encode the bids, compare and select bids, generate draft POs.

First, a list of products is established. The call for bid is then confirmed
and RFQs can be generated. They are in the state 'Draft RFQ' until sent to the
supplier and then marked as 'RFQ Sent'. The bids have to be encoded and moved
to state 'Bid Encoded'. When closing the call for bids, in order to start the
bids selection, all RFQ that have not been sent will be canceled. However, sent
RFQs can still be encoded. Bids that are not received will remain in state 'RFQ
Sent' and can be manually canceled.

Afterwards, the bids selection can be started by choosing product lines. The
workflow has been modified to allow to mark that the selection of bids has
occurred but without having to generate the POs yet. Those can be created at a
new later state called 'Bids Selected'.

When generating POs, they are created in the state 'Draft PO' introduced by the
module purchase_extended.

Some fields have been added to specify with more details the call for bids and
prefill fields of the generated RFQs.

A link has been added between a call for bids line and the corresponding line
of each generated RFQ. This is used for the bids comparison in order to compare
bid lines and group then properly.

For running the tests the nose python package is required.
""",
 "depends": ["purchase_requisition",
             "stock",  # For incoterms
             "purchase_extended",  # for field incoterms place
             ],
 "demo": [],
 "data": ["wizard/modal.xml",
          "wizard/purchase_requisition_partner_view.xml",
          "view/purchase_requisition.xml",
          "view/purchase_order.xml",
          "workflow/purchase_requisition.xml",
          "data/purchase.cancelreason.yml",
          ],
 "js": [
        "static/src/js/web_addons.js",
        ],
 "auto_install": False,
 "test": ["test/process/restricted.yml",
          ],
 "installable": True,
 "certificate": "",
 }
