# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': "Group purchase orders from procurements",
    'version': '1.0',
    'category': 'Purchase Management',
    'description': """
Group purchase orders from procurements
=======================================

This module is a backport from version 8.0 to 7.0 of the purchase order
creation from procurement orders. At the time of running the scheduler the
application will search for an existing PO in draft state for the same
supplier and with the same destination location. If found, it will extend
the PO to include the new product and quantity to be procured.

The main difference with version 8.0 is that the application will not
attempt to increase the quantity of a line for an existing PO, because each
line in a PO is associated in 7.0 to the procurement's stock move.



Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

When the procurement scheduler is run the application creates or extends the
purchase orders.

Known issues / Roadmap
======================

No known issues have been identified.

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
""",
    'author': "Eficent,Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['purchase'],
    "data": [
        'view/procurement.xml',
    ],
    'test': [
        'test/run_scheduler.yml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
