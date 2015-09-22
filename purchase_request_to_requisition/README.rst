.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License AGPL-3

Purchase Request to Call for Bids
=================================
This module introduces the following features:
* The possibility to create new Call for Bids or update existing Bids from
Purchase Request Lines.
* The possibility to create Purchase Requests on the basis of Procurement
Orders.

Installation
============

No specific instructions required.


Configuration
=============

No specific instructions requied.

Usage
=====
Create Purchase Requests from Procurement Orders
------------------------------------------------
Go to the product form, in tab 'Procurement' and choose 'Purchase Request'.
When a procurement order is created and the supply method is 'Make to Order'
the application will now create a Purchase Request.


Create Bids from Purchase Requests
----------------------------------
Go to the Purchase Request Lines from the menu entry 'Purchase Requests',
and also from the 'Purchase' menu.

Select the lines that you wish to initiate the RFQ for, then go to 'More'
and press 'Create Purchase Bid'.

You can choose to select an existing Draft Bid or create a new one.

In case that you chose to select an existing Bid, the application will search
for existing lines matching the request line, and will add the extra
quantity to them.

In case that you create a new RFQ, the request lines will also be
consolidated into as few as possible lines in the RFQ.


For further information, please visit:

* https://www.odoo.com/forum/help-1


Known issues / Roadmap
======================

No issues have been identified


Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.