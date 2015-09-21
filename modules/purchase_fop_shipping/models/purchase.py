# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
#    Copyright (C) 2015-TODAY Akretion <http://www.akretion.com>.
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
__author__ = 'mourad.elhadj.mimoune'

from openerp.exceptions import Warning as UserError 
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):

	_inherit = "purchase.order"
	fop_reached = fields.Boolean(string='FOP reached', help= 'Free-Of-Paiment shipping reached' , compute='_fop_shipping_reached')
	force_order_under_fop = fields.Boolean(string='Confirm under FOP',help='Force confirm order under Free-Of-Paiment shipping',)
	fop_shipping = fields.Float('FOP shipping', help='Min order amount for Free-Of-Paiment shipping',)
	@api.multi
	@api.depends('amount_total', 'partner_id.fop_shipping')
	def _fop_shipping_reached(self):
		for record in self:
			record.fop_reached = record.amount_total >  record.partner_id.fop_shipping
	@api.multi
	def wkf_confirm_order(self):
		todo = self.env['purchase.order.line'].browse([])
		for po in self:
			if not po.force_order_under_fop and not po.fop_reached :
				raise UserError(_('You cannot confirm a purchase order with amount under FOP shipping.'))
			if not any(line.state != 'cancel' for line in po.order_line):
				raise UserError(_('You cannot confirm a purchase order without any purchase order line.'))
			if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
				raise UserError(
					_("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
			
			for line in po.order_line:
				if line.state=='draft':
					todo += line
		todo.action_confirm()
		self.write({'state' : 'confirmed', 'validator' : self._uid})
		return True
	@api.v7
	def onchange_partner_id(self, cr, uid, ids, part, context=None):
		result = super(PurchaseOrder, self).onchange_partner_id(cr, uid, ids, part)
		if part:
			part_record = self.pool.get('res.partner').browse(cr, uid, part, context=context)
			result['value']['fop_shipping'] = part_record.fop_shipping
		return result