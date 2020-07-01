##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
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
    'name': 'Computed Purchase Order',
    'version': '12.0.1.0.2',
    'category': 'Purchase',
    'author': 'GRAP, Druidoo',
    'website': 'https://cooplalouve.fr/',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'product_average_consumption',
        'purchase_package_qty',
        'purchase_discount',
    ],
    'data': [
        'security/purchase_compute_order_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'wizard/update_product_wizard_view.xml',
        'views/computed_purchase_order_view.xml',
        'views/computed_purchase_order_line_view.xml',
        'views/res_config_view.xml',
        'views/purchase_order_line_view.xml',
        'views/res_partner_view.xml',
        'views/product_supplierinfo_view.xml',
    ],
}
