# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Savoir-faire Linux (<http://savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    "name": "Internal Validation for Purchase",
    "version": "7.0.1.0.0",
    "category": 'Purchases',
    "depends": [
        "purchase",
    ],
    "author": 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    "description": """
============================
Purchase Internal Validation
============================

This module modifies the purchase workflow in order to validate 
purchases that exceeds the amount set in the Purchase configuration panel.
It differs from the purchase_double_validation module by inserting the validation
step in the purchase order workflow before the confirmation, not after.

Configuration
=============

* Set the limit in the Purchase configuration panel
* Add some users to the Purchase / Validator and Purchase / User groups
* Make sure those users have correct email addresses to receive notifications

Usage
=====

* As a Purchase user, go to Purchase > Purchases > Quotations
* Create a quotation exceeding the limit and try to confirm it
* As a Purchase validator, validate or refuse the quotation
* As the user, you can now confirm the PO

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* ..

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/OCA/purchase-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/OCA/purchase-workflow/issues/new>`_.


Credits
=======

Contributors
------------

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Vincent Vinet <vincent.vinet@savoirfairelinux.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
    """,
    'data': [
        'security/groups.xml',
        'views/res_config_view.xml',
        'views/purchase_view.xml',
        'workflow/purchase_internal_validation_workflow.xml',
    ],
    'installable': True,
}
