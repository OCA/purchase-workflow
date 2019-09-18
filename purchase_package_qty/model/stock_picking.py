# -*- coding: utf-8 -*-
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

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        vals = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties)
        if picking.origin and picking.origin[0:2] == 'PO'\
                and picking.origin[0:3] != 'POS':
            order_id = self.env['purchase.order'].search(
                [('name', '=', picking.origin)])
            if order_id:
                for pack in vals:
                    line = order_id.order_line.filtered(
                        lambda l, p=pack['product_id'],
                        q=pack['product_qty']: l.product_id.id == p and
                        l.product_qty == q)
                    if line:
                        pack['package_qty'] = line[0].package_qty
                        pack['product_qty_package'] = line[0].\
                            product_qty_package
                return vals
        for pack in vals:
            product = self.env['product.product'].browse(
                pack['product_id'])
            uom = self.env['product.uom'].browse(pack['product_uom_id'])
            psi = self.env['product.product']._select_seller(
                product, picking.partner_id, pack['product_qty'],
                uom_id=uom)
            psi = psi and psi[0] or False
            if psi:
                pack['package_qty'] = psi.package_qty
                pack['product_qty_package'] = pack['product_qty'] /\
                    psi.package_qty
        return vals
