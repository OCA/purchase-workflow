.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

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

To proceed and validate bid selection, you can print the "Comparative Bid Analysis".
This comparative report will only show eligible bids.

For running the tests the nose python package is required.


.. warning::
   Version prior to 0.4 was defining a `dest_address_id` field on Purchase
   Requisition. This field has been extracted in module
   `purchase_requisition_delivery_address`


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new?body=module:%20purchase_requisition_bid_selection%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

* Jacques-Etienne Baudoux <je@bcim.be>
* Joêl Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Romain Deheele <romain.deheele@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Pierre Verkest <pverkest@anybox.fr>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
