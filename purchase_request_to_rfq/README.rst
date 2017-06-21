.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Purchase Request to RFQ
=======================

This module adds the possibility to create or update Requests for
Quotation (RFQ) from Purchase Request Lines.

Usage
=====

To use this module you need to:

#. Go to the Purchase Request Lines either from the *Purchase Requests*
   or *Purchase* menus.
#. Select the lines that you wish to initiate the RFQ for, then go to *More*
   and press *Create RFQ*.
#. In the wizard that raises you can choose to select an existing RFQ or
   create a new one. In the second case, you additionally have to choose a
   supplier.

Consolidation logic for RFQ
---------------------------

In case that you chose to select an existing RFQ, the application will search
for existing lines matching the request line, and will add the extra
quantity to them, recalculating the minimum order quantity,
if it exists for the supplier of that RFQ.

In case that you create a new RFQ, the request lines will also be
consolidated into as few as possible lines in the RFQ.

Cancel Logic
------------

Note the following behaviors:

* When you cancel a PO related to a purchase request, only incoming shipments
  will be cancelled.
* If you are using this module in conjunction with
  `purchase_request_procurement` and the purchase request was originated
  after a chain of moves/procurements, they will be all respected when
  cancelling a PO. Cancel de purchase request if you want to totally cancel
  this chain.

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

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Aaron Henriquez <ahenriquez@eficent.com>
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Lois Rilo <lois.rilo@eficent.com>


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
