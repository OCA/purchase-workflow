# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    blanket_order_id = fields.Many2one(
        'purchase.blanket.order', string='Origin blanket order',
        related='order_line.blanket_order_line.order_id',
        readonly=True)

    @api.constrains('partner_id')
    def check_partner_id(self):
        if self.partner_id:
            if self.order_line:
                for line in self.order_line:
                    if line.blanket_order_line.partner_id != self.partner_id:
                        raise ValidationError(_(
                            'The vendor must be equal to the blanket order '
                            'lines vendor'))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    blanket_order_line = fields.Many2one(
        'purchase.blanket.order.line',
        'Blanket Order Line',
        copy=False)

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        # If product has changed remove the relation with blanket order line
        if self.product_id:
            eligible_bo_lines = self.get_eligible_bo_lines()
            if eligible_bo_lines:
                if not self.blanket_order_line or \
                        self.blanket_order_line.product_id != self.product_id:
                    self.blanket_order_line = \
                        self.get_assigned_bo_line(eligible_bo_lines)
            return {'domain': {'blanket_order_line': [
                ('id', 'in', eligible_bo_lines.ids)]}}

    @api.onchange('blanket_order_line')
    def onchange_blanket_order_line(self):
        if self.blanket_order_line:
            self.product_id = self.blanket_order_line.product_id
            self.order_id.partner_id = self.blanket_order_line.partner_id

    def get_assigned_bo_line(self, bo_lines):
        # We get the blanket order line with enough quantity and closest
        # scheduled date
        assigned_bo_line = False
        today = date.today()
        date_delta = timedelta(days=365)
        for line in bo_lines:
            date_schedule = fields.Date.from_string(line.date_schedule)
            if self.product_qty >= 0:
                if line.remaining_qty > self.product_qty:
                    if date_schedule and date_schedule - today < date_delta:
                        assigned_bo_line = line
                        date_delta = date_schedule - today
        if not assigned_bo_line:
            assigned_bo_line = bo_lines[0]
        return assigned_bo_line

    def get_eligible_bo_lines(self):
        filters = ['&', '&',
                   ('product_id', '=', self.product_id.id),
                   ('remaining_qty', '>', 0.0),
                   ('order_id.state', '=', 'open')]
        if self.product_qty:
            filters.append(('remaining_qty', '>', self.product_qty))
        if self.order_id.partner_id:
            filters.append(
                ('partner_id', '=', self.order_id.partner_id.id))
        return self.env['purchase.blanket.order.line'].search(filters)
