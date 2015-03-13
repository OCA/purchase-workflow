Purchase Requisition Bid Selection
==================================

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
occurred but without having to generate the POs yet (Bids selected). Then an
approval of the selection is required and POs can be created at a new later
state called 'Selection closed'.

When generating POs, they are created in the state 'Draft PO' introduced by the
module purchase_rfq_bid_workflow.

Some fields have been added to specify with more details the call for bids and
prefill fields of the generated RFQs.

A link has been added between a call for bids line and the corresponding line
of each generated RFQ. This is used for the bids comparison in order to compare
bid lines and group then properly.

For running the tests the nose python package is required.

.. warning::
   Version prior to 0.4 was defining a `dest_address_id` field on Purchase
   Requisition. This field has been extracted in module
   `purchase_requisition_delivery_address`
