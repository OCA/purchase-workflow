# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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
    'name': 'Account Creditor Price Difference',
    'version': '1.0',
    'author': 'Eficent',
    'website': 'http://www.eficent.com',
    'description': """

Account Creditor Price Difference
==================================

When the supplier invoice is created from a purchase order, if the
destination of the product is a company location the application
will propose as debiting account the stock input account from the
product or product category, instead of the product, in order
to balance the credit that occurred when the product was received.

The stock input account is frequently called the Goods Received Not Invoiced
account (GRIN).

Furthermore, when the invoice is accepted, the application will identify
any differences between the invoice price and the product cost, and will
post the differences to a new Price Differences account defined in the
product or product category.

""",
    'images': [],
    'depends': ['product', 'purchase'],
    'category': 'Accounting & Finance',
    'demo': [],
    'data': ['product_view.xml',],
    'auto_install': False,
    'installable': True,
}
