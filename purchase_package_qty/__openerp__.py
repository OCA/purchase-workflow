# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
    'name': 'Purchase - Package Quantity',
    'version': '9.1.3.0.0',
    'category': 'Purchase',
    'description': """
Allow user to define the package of products the supplier sells
===============================================================

Functionnality:
---------------
In product_supplierinfo, add a "Qty per Package" field to register how many
purchase UoM of the product there are in the package the supplier uses.
All purchase lines for this product+supplier must have a quantity that is a
multiple of that package_quantity.

For example:
I purchase beer bootles.
The supplier sells them with a price per unit, thus the purchase UoM is PCE.
But the supplier put them in 6pcs boxes, and I have to buy a multiple of 6.

Technical:
----------
An init function will initialize this field by copying the values in the
min_qty field as this one might have been used to figure the package qty.

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2014, Groupement Régional Alimentaire de Proximité;
    * Author :
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'base',
        'product',
        'purchase_discount',
    ],
    'data': [
        'views/product_supplierinfo_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'views/account_invoice_view.xml',
        'views/report_stockinventory.xml',
        'views/stock_inventory_view.xml',
        'data/function.xml',
    ],
}
