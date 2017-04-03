.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Purchase Date Planned Manual
============================

This module makes the system to always respect the planned (or scheduled)
date set by the user when creating a Purchase order or the day set in the
procurement order if the line is created from there.

Additionally, this module modifies the PO views and sets in red the lines
that are predicted to arrive late compared to the scheduled date and vendor
lead time.

Usage
=====

To use this module you could follow any of the two options below:

#. Go to 'Purchase' and create a purchase order.
#. Manually set the scheduled date in the PO lines.
#. This date will never be modified by the system and the lines that are
   expected to be late are highlighted in red.

Or:

#. Create a procurement order for a product that can be bought and have the
   route 'buy' activated.
#. Run the procurement.
#. Now the scheduled date in the procurement is respected even if the line is
   added to a previously existing PO.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>

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
