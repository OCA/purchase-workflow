.. image:: https://img.shields.io/badge/license-LGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

==========================
Product Supplerinfo Tender
==========================

This module allows to manage Tenders and Bids associated to supplier pricelists.

Supplier Pricelist
------------------
Represents a contractual agreement that the company maintains with a supplier
on a specific product or service, by which the supplier will supply for a
certain period of of time, at an agreed price per unit of measure. Tiered
pricing agreements can be held, based on the quantity being procured.

The Supplier pricelist is used in this module as related to Pricelist Bids.


Supplier Pricelist Tender
-------------------------
In order to find the best possible deal the company can initiate a Tendering
process to request to various companies to provide bids for a number of
products or services. The person responsible defines in the Tender the
products to include, estimated quantities, and the tender closing date.

The Tender is used as the basis to create Supplier Pricelist Bids.


Supplier Pricelist Bid
----------------------
Represents the Bid provided from a supplier on a number of products or
services. A bid contains Supplier Pricelists.


Installation
============

No external library is used.

Configuration
=============

Two user groups are provided by default:
* `Pricelist Tenders / User`. Can create Tenders and Bids, but cannot approve
 them or set them back to draft once they are cancelled.
* `Pricelist Tenders / Manager`. Can completely manage Tenders and Bids.

None of the above roles can create or change standalone Supplier Pricelists,
or change them once the associated Bid has been closed.


Usage
=====

* Go to `Purchases / Pricelist Tenders` and create a new Tender. Indicate the
  products that you want to include, the person responsible for the Tender and
  a closing date. Once the Tender is defined, press `Confirm`.
* You can now request to  suppliers to provide their Bids. As they provide
  them, you can encode them from the Tender, pressing the button `Encode Bids`,
  or from the menu, in `Purchases / Pricelist Bids`. For each Bid, indicate
  the price that the supplier proposes, and the quantity associated with that
  price.
* Within the Tender, when the closing date is due, press `Select Bids`
  to close the process of accepting bids, and start the selection process.
  All the Supplier Pricelists for all Bids associated to the tender are
  listed. Press the button `Approve` in each line to decide what are the
  proposed prices that are approved.
* When the selection process has finished, press `Close Selection`. The
  Tender is now formally concluded.
* Go to the Bids and send them to the Suppliers, so that they know what items
  in their Bids have been finally approved.

Other remarks:

* A Supplier Pricelist can only be throughout the process if the associated Bid
  is open.
* Once a Bid is closed, if the Supplier Pricelist was not approved, it's
status will become `Closed`.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Eficent Business and IT Consulting Services S.L. <contact@eficent.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
