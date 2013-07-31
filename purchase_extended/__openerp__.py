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

{"name": "IFRC Purchase",
 "version": "0.1",
 "author": "Camptocamp",
 "category": "Purchase Management",
 "license": "AGPL-3",
 'complexity': "normal",
 "images": [],
 "description": """
This module improves the standard Purchase module.
==================================================
In standard, RFQs, Bids and PO are all the same object.  The purchase workflow
has been improved with a new 'Draft PO' state to clearly differentiate the
RFQ->Bid workflow and the PO workflow. A type field has also been added to
identify if a document is of type 'rfq' or 'purchase'. This is particularly
usefull for cancelled state and for datawarehouse.

The 'Requests for Quotation' menu entry shows only documents of type 'rfq' and
the new documents are created in state 'Draft RFQ'. Those documents have lines
with a price, by default, set to 0; it will have to be encoded when the bid is
received. The state 'Bid Received' has been renamed 'Bid Encoded'. This clearly
indicates that the price has been filled in. The bid received date will be
requested when moving to that state.

The 'Purchase Orders' menu entry shows only documents of type 'purchase' and
the new documents are created in state 'Draft PO'.

The logged messages have been improved to notify users at the state changes and
with the right naming.


In the scope of internation transactions, some fields have been added:
 - Consignee: the person to whom the shipment is to be delivered
 - Incoterms Place: the standard incoterms field specifies the incoterms rule
   that applies. This field allows to name the place where the goods will be
   available

TODO: describe onchange warehouse
""",
 "depends": ["purchase",
             ],
    "demo": [],
    "data": ["view/purchase_order.xml",
             "view/purchase_cancel.xml",
             "data/purchase_order.xml",
             "data/purchase.cancelreason.csv",
             "workflow/purchase_order.xml",
             "wizard/modal.xml",
             "wizard/action_cancel_reason.xml",
             "security/ir.model.access.csv",
             ],
    "auto_install": False,
    "test": [],
    "installable": True,
    "certificate": "",
 }
