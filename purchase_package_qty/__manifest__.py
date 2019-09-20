##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
    'version': '12.0.1.0.0',
    'category': 'Purchase',
    'author': 'GRAP, Druidoo',
    'website': 'https://cooplalouve.fr',
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
        'views/report_invoice.xml',
        'data/function.xml',
    ],
}
