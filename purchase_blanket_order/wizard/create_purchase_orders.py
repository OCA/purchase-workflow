# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class BlanketOrderWizard(models.TransientModel):
    _name = 'purchase.blanket.order.wizard'
    _description = 'Blanket Order Wizard'

    @api.model
    def _default_order(self):
        # in case the cron hasn't run
        self.env['purchase.blanket.order'].expire_orders()
        if not self.env.context.get('active_id'):
            return False
        blanket_order = self.env['purchase.blanket.order'].browse(
            self.env.context['active_id'])
        if blanket_order.state == 'expired':
            raise UserError(_('You can\'t create a purchase order from '
                              'an expired blanket order!'))
        return blanket_order

    @api.model
    def _default_lines(self):
        blanket_order = self._default_order()
        lines = [(0, 0, {
            'blanket_line_id': l.id,
            'product_id': l.product_id.id,
            'date_schedule': l.date_schedule,
            'remaining_qty': l.remaining_qty,
            'qty': l.remaining_qty,
        }) for l in blanket_order.lines_ids]
        return lines

    blanket_order_id = fields.Many2one(
        'purchase.blanket.order', default=_default_order, readonly=True)
    lines_ids = fields.One2many(
        'purchase.blanket.order.wizard.line', 'wizard_id',
        string='Lines', default=_default_lines)

    @api.multi
    def create_purchase_order(self):
        self.ensure_one()

        order_lines = []
        for line in self.lines_ids:
            if line.qty == 0.0:
                continue

            if line.qty > line.remaining_qty:
                raise UserError(
                    _('You can\'t order more than the remaining quantities'))

            date_planned = line.blanket_line_id.date_schedule

            vals = {'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'date_planned': date_planned if date_planned else
                    line.blanket_line_id.order_id.date_order,
                    'product_uom': line.blanket_line_id.product_uom.id,
                    'sequence': line.blanket_line_id.sequence,
                    'price_unit': line.blanket_line_id.price_unit,
                    'blanket_line_id': line.blanket_line_id.id,
                    'product_qty': line.qty}
            order_lines.append((0, 0, vals))

        if not order_lines:
            raise UserError(_('An order can\'t be empty'))

        order_vals = {
            'partner_id': self.blanket_order_id.partner_id.id,
        }
        order_vals.update(self.env['purchase.order'].onchange(
            order_vals, 'partner_id', {'partner_id': 'true'})['value'])
        order_vals.update({
            'origin': self.blanket_order_id.name,
            'currency_id': self.blanket_order_id.currency_id.id,
            'order_line': order_lines,
            'payment_term_id': (self.blanket_order_id.payment_term_id.id
                                if self.blanket_order_id.payment_term_id
                                else False),
        })

        purchase_order = self.env['purchase.order'].create(order_vals)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
        }


class BlanketOrderWizardLine(models.TransientModel):
    _name = 'purchase.blanket.order.wizard.line'

    wizard_id = fields.Many2one('purchase.blanket.order.wizard')
    blanket_line_id = fields.Many2one(
        'purchase.blanket.order.line')
    product_id = fields.Many2one(
        'product.product',
        related='blanket_line_id.product_id',
        string='Product', readonly=True)
    date_schedule = fields.Date(
        related='blanket_line_id.date_schedule', readonly=True)
    remaining_qty = fields.Float(
        related='blanket_line_id.remaining_qty', readonly=True)
    qty = fields.Float(string='Quantity to Order', required=True)
