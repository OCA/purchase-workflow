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

    @api.multi
    def action_picking_create(self):
        for purchase in self:
            # since we added a transition from picking_except to
            # picking, we prevent the picking to be created again
            if purchase.picking_ids:
                # change from picking_except to confirmed
                purchase.state = 'approved'
                continue
            super(PurchaseOrder, self).action_picking_create()

    @api.multi
    def canceled_picking_not_canceled_line(self):
        self.ensure_one()
        for line in self.order_line:
            if line.state == 'cancel':
                continue
            for move in line.move_ids:
                if move.state == 'cancel':
                    return True
        return False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    amend_id = fields.Many2one(comodel_name='purchase.order.line',
                               string='Amend Line')
    amended_by_ids = fields.One2many(comodel_name='purchase.order.line',
                                     inverse_name='amend_id',
                                     string='Amended by lines')
