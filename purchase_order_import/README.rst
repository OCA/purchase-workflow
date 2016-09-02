.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Purchase Order Import
=====================

This module adds support for the import of electronic quotations. This module provides the base methods to import electronic quotations ; it requires additionnal modules to support specific order formats:

* module *purchase_order_import_ubl*: adds support for `Universal Business Language (UBL) <http://ubl.xml.org/>`_ quotations as:

  - XML file,
  - PDF file with an embedded XML file.

Configuration
=============

No configuration is needed.

Usage
=====

This module adds a button *Import Quotation File* on Requests for Quotation. This button starts a wizard that will propose you to select the quotation file. The wizard will also propose you an update option:

* only update the prices of the draft purchase order from the quotation file (default option),
* update prices and quantities of the draft purchase order from the quotation file.

When you click on the button *Update RFQ*:

* if Odoo has a line in the quotation file that is not in the draft purchase order, it will create a new purchase order line,
* if Odoo has a line in the draft purchase order that is not in the quotation file, it will write a warning in the chatter of the purchase order (it will not delete the purchase order line),
* for all the lines that are both in the draft purchase order and in the quotation file, the purchase order line will be updated if needed.
* if the incoterm of the quotation file is not the same as the incoterm of the draft purchase order, Odoo will update the incoterm of the purchase order.
* the imported quotation file is attached to the purchase order.

Once the quotation file is imported, you should read the messages in the chatter of the purchase order because it may contain important information about the import.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/8.0

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

* Alexis de Lattre <alexis.delattre@akretion.com>

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
