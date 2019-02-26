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

    @api.model
    def _check_exchausted_blanket_order_line(self):
        return any(line.blanket_order_line.remaining_qty < 0.0 for
                   line in self.order_line)

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order._check_exchausted_blanket_order_line():
                raise ValidationError(
                    _('Cannot confirm order %s as one of the lines refers '
                      'to a blanket order that has no remaining quantity.')
                    % order.name)
        return res

    @api.constrains('partner_id')
    def check_partner_id(self):
        for line in self.order_line:
            if line.blanket_order_line:
                if line.blanket_order_line.partner_id != \
                        self.partner_id:
                    raise ValidationError(_(
                        'The vendor must be equal to the blanket order'
                        ' lines vendor'))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    blanket_order_line = fields.Many2one(
        'purchase.blanket.order.line',
        'Blanket Order Line',
        copy=False)

    @api.multi
    def _get_assigned_bo_line(self):
        self.ensure_one()
        eligible_bo_lines = self.get_eligible_bo_lines()
        if eligible_bo_lines:
            if not self.blanket_order_line or self.blanket_order_line \
                    not in eligible_bo_lines or \
                    self.blanket_order_line.product_id != self.product_id:
                self.blanket_order_line = \
                    self.get_assigned_bo_line(eligible_bo_lines)
                if self.blanket_order_line.date_schedule:
                    self.date_planned = self.blanket_order_line.date_schedule
        else:
            self.blanket_order_line = False
        return {'domain': {'blanket_order_line': [
            ('id', 'in', eligible_bo_lines.ids)]}}

    @api.onchange('product_id', 'partner_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        # If product has changed remove the relation with blanket order line
        if self.product_id:
            return self._get_assigned_bo_line()
        return res

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if self.product_id:
            return self._get_assigned_bo_line()
        return res

    @api.onchange('blanket_order_line')
    def onchange_blanket_order_line(self):
        if self.blanket_order_line:
            self.product_id = self.blanket_order_line.product_id
            self.order_id.partner_id = self.blanket_order_line.partner_id
            if self.blanket_order_line.date_schedule:
                self.date_schedule = self.blanket_order_line.date_schedule

    def get_assigned_bo_line(self, bo_lines):
        # We get the blanket order line with enough quantity and closest
        # scheduled date
        assigned_bo_line = False
        today = date.today()
        date_delta = timedelta(days=365)
        for line in bo_lines:
            date_schedule = fields.Date.from_string(line.date_schedule)
            if date_schedule and date_schedule - today < date_delta:
                assigned_bo_line = line
                date_delta = date_schedule - today
        return assigned_bo_line

    def get_eligible_bo_lines(self):
        base_qty = self.product_uom._compute_quantity(
            self.product_qty, self.product_id.uom_id)
        filters = [
            ('product_id', '=', self.product_id.id),
            ('remaining_qty', '>=', base_qty),
            ('order_id.state', '=', 'open')]
        if self.order_id.partner_id:
            filters.append(
                ('partner_id', '=', self.order_id.partner_id.id))
        return self.env['purchase.blanket.order.line'].search(filters)
