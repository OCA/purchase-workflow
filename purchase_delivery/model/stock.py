# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _prepare_shipping_invoice_line(self, cr, uid, picking, invoice, context=None):
        """Prepare the invoice line to add to the shipping costs to the shipping's
           invoice.

            :param browse_record picking: the stock picking being invoiced
            :param browse_record invoice: the stock picking's invoice
            :return: dict containing the values to create the invoice line,
                     or None to create nothing
        """
        if invoice.type in ['out_invoice', 'out_refund']:
            return super(stock_picking, self)._prepare_shipping_invoice_line(
                cr, uid, picking, invoice, context=context)
        else:
            carrier_obj = self.pool.get('delivery.carrier')
            grid_obj = self.pool.get('delivery.grid')
            if not picking.carrier_id or \
                any(inv_line.product_id.id == picking.carrier_id.product_id.id
                    for inv_line in invoice.invoice_line):
                return None
            total_price = 0.0
            total_qty = 0.0
            for move in picking.move_lines:
                grid_id = carrier_obj.grid_src_dest_get(
                    cr, uid, [picking.carrier_id.id], picking.partner_id.id,
                    move.partner_id.id, context=context)
                if not grid_id:
                    raise orm.except_orm(_('Warning!'),
                                         _('The carrier %s (id: %d) has no '
                                           'delivery grid!')
                                         % (picking.carrier_id.name,
                                            picking.carrier_id.id))
                price = grid_obj.get_cost_from_picking(cr, uid, grid_id,
                                                       invoice.amount_untaxed,
                                                       move.product_id.weight,
                                                       move.product_id.volume,
                                                       context=context)
                total_price += price
                total_qty += move.product_qty
            price = total_price / total_qty
            account_id = picking.carrier_id.product_id.\
                property_account_expense.id
            if not account_id:
                account_id = picking.carrier_id.product_id.categ_id.\
                    property_account_expense_categ.id

            taxes = picking.carrier_id.product_id.taxes_id
            partner = picking.partner_id
            fpos_obj = self.pool.get('account.fiscal.position')
            if partner:
                account_id = fpos_obj.map_account(
                    cr, uid, partner.property_account_position, account_id)
                taxes_ids = fpos_obj.map_tax(
                    cr, uid, partner.property_account_position, taxes)
            else:
                taxes_ids = [x.id for x in taxes]

            return {
                'name': picking.carrier_id.name,
                'invoice_id': invoice.id,
                'uom_id': picking.carrier_id.product_id.uos_id.id,
                'product_id': picking.carrier_id.product_id.id,
                'account_id': account_id,
                'price_unit': price,
                'quantity': 1,
                'invoice_line_tax_id': [(6, 0, taxes_ids)],
            }