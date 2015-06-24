# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
    "name": "Reset invoice method of confirmed purchase orders",
    "version": "0.1",
    "author": "Therp BV",
    "category": 'Purchase Management',
    'description': """
Description
===========
Allow the user to reset the invoice method of confirmed purchase orders.
By having this option, you don't have to know upfront how your supplier
is going to invoice you for the orders that you place with them.
Changing the invoice method will unlink any draft invoices for the order,
reset the invoice setting of associated stock pickings or order lines
and update the order workflow.

Known limitations
=================
There may not be any invoices for the order which have been confirmed. This
would normally include any invoices which have been reset to 'draft' state, as
such invoices cannot be deleted from OpenERP either.

Converting orders with invoicing method 'picking' only works for orders which
have been only been invoiced after installation of this module, as OpenERP
does not properly register which invoice line comes from which picking by
itself.
    """,
    'website': 'http://therp.nl',
    'depends': [
        'purchase'
        ],
    'data': [
        'view/purchase_reset_invoice_method.xml',
        'view/purchase_order.xml',
        'workflow/purchase.xml',
        ],
    'installable': True,
}
