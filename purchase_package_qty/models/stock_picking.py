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

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        backorders = super()._create_backorder(backorder_moves=backorder_moves)
        if backorders.move_line_ids:
            diff_pack_op = backorders.move_line_ids
            for pack in diff_pack_op:
                if pack.product_qty > 0:
                    # Create po line that is matched with pack
                    # which was added manually
                    po_line = backorders.prepare_vals_order_line(pack)
                    if po_line:
                        moves = po_line._create_stock_moves(backorders)
                        move_ids = moves._action_confirm()
                        moves = self.env['stock.move'].browse(move_ids)
                        seq = 0
                        for move in sorted(
                                moves, key=lambda move: move.date_expected):
                            seq += 5
                            move.sequence = seq
                        moves._action_assign()
                else:
                    pack.unlink()
        return backorders

    @api.multi
    def prepare_vals_order_line(self, diff_pack_op):
        '''
            This method prepares vals to build order line when user add
            more pack operation to stock picking manually.
            To make the stock match with PO to create right invoice
        '''
        self.ensure_one()
        po_line_env = self.env['purchase.order.line']
        order = self.env['purchase.order'].search([
            ('name', '=', self.origin)
        ], limit=1)
        if order:
            procurement_uom_po_qty = diff_pack_op.product_id.uom_po_id.\
                _compute_quantity(
                    diff_pack_op.package_qty,
                    diff_pack_op.product_id.uom_po_id
                )
            seller = diff_pack_op.product_id._select_seller(
                partner_id=self.partner_id,
                quantity=procurement_uom_po_qty,
                date=order.date_order,
                uom_id=self.product_id.uom_po_id)
            product_name = seller and seller[0].product_name or\
                diff_pack_op.product_id.name
            product_code = seller and seller[0].product_code or\
                diff_pack_op.product_id.default_code
            name = "%s%s" % (product_code and '[' + product_code + '] ' or '',
                             product_name)
            price_unit = seller and seller[0].base_price or\
                diff_pack_op.product_id.standard_price
            # Prepare value to create the purchase order line that is matched
            vals = {}
            # Add operation_extra_id field to specify this line was build from
            # a pack operation to create right invoice
            vals.update({
                'name': name,
                'product_id': diff_pack_op.product_id.id,
                'product_qty': diff_pack_op.product_qty,
                'product_qty_package': diff_pack_op.product_qty_package,
                'package_qty': diff_pack_op.package_qty,
                'order_id': order.id,
                'product_uom': diff_pack_op.product_uom_id.id,
                'price_unit': price_unit,
                'date_planned': order.date_planned,
                'taxes_id': [(
                        6, 0, [x.id for x in
                               diff_pack_op.product_id.supplier_taxes_id])],
                'operation_extra_id': diff_pack_op.id
            })
            po_line = po_line_env.create(vals)
            return po_line
