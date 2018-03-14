.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

============================
Purchase Request Procurement
============================

This module introduces the following feature: The possibility to create
Purchase Requests on the basis of Procurement Orders.

Configuration
=============

To configure the product follow this steps:

#. Go to a product form.
#. Go to *Inventory* tab.
#. Check the box *Purchase Request* along with the route *Buy*.

With this configuration, whenever a procurement order is created and the supply
rule selected is 'Buy' the application will create a Purchase Request instead
of a Purchase Order.

**Recomendation**: if you want to enhance your flow, you should also install
`purchase_request_to_rfq` which allow you to create POs from purchase
requests.

Usage
=====

To use this module:

#. Create a procurement for a product configured as described above.
#. If the rule found for the procurement is buy, a purchase request is
   created for this procurement.

Cancel logic:
-------------

Note the following behaviors:

* If you Reject a purchase request all procurements related to its lines
  will be cancelled. And if your rules are set to propagate, all the
  cancellation will propagate through the chain of procurements/moves.
* If you cancel a procurement related to a purchase request, procurement will
  end cancelled and its link to the purchase request reset. While the related
  purchase request line will be cancelled but keeping the link to the
  procurement.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/10.0

For further information, please visit:

* http://www.eficent.com/blog_en/streamline-your-purchasing-process-in-odoo-using-purchase-requests/

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

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Aaron Henriquez <ahenriquez@eficent.com>
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Thomas Binsfeld <thomas.binsfeld@acsone.eu>
* Benjamin Willig <benjamin.willig@acsone.eu>
* Lois Rilo Antelo <lois.rilo@eficent.com>

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
