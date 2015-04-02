# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_amend(self):
        self.ensure_one()
        amend_model = self.env['purchase.order.amendment'].with_context({
            'active_model': self._name,
            'active_ids': self.ids,
            'active_id': self.id,
        })

        amendment = amend_model.create({'purchase_id': self.id})
        return amendment.wizard_view()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    received_qty = fields.Float(
        string='Received Quantity',
        compute='_compute_received_qty',
        digits_compute=dp.get_precision('Product Unit of Measure'),
    )
    received = fields.Boolean(string='Received',
                              compute='_compute_received_qty')
    amend_id = fields.Many2one(comodel_name='purchase.order.line',
                               string='Amend Line')
    amended_by_ids = fields.One2many(comodel_name='purchase.order.line',
                                     inverse_name='amend_id',
                                     string='Amended by lines')

    @api.one
    @api.depends('product_qty',
                 'move_ids', 'move_ids.state', 'move_ids.product_qty')
    def _compute_received_qty(self):
        moves = self.move_ids
        if not moves:
            self.received = False
            self.received_qty = 0

        received_qty = sum(moves.mapped(
            lambda m: m.product_qty if m.state == 'done' else 0.)
        )
        rounding = self.product_id.uom_id.rounding
        self.received = bool(float_compare(self.product_qty, received_qty,
                                           precision_digits=rounding) <= 0)
        self.received_qty = received_qty
