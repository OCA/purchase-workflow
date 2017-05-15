.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Purchase Isolated Quotation
===========================

In some countries/companies, it is already common to separate these two documents.
For filing purposes, the document sequence of quotation and purchase order
has to be separated. In practice, there could be multiple request for quotations
open to a supplier, yet only one quotation get converted to the purchase order.

This module separate request for quotation and purchase order by adding is_order
flag in purchase.order model.

Each type of document will have separated sequence numbering.
Quotation will have only 2 state, Draft and Done. Sales Order work as normal.

Usage
=====

* Create Quotation as normal
* As user click "Convert to Order", the isolated purchase order will be created

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Phongyanon Y. <phongyanony@ecosoft.co.th>

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
