# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    require_wa = fields.Boolean(
        compute='_compute_require_wa',
    )
    wa_id = fields.Many2one(
        comodel_name='work.acceptance',
        string='WA Reference',
        readonly=True,
        copy=False,
        domain=lambda self: [
            ('state', '=', 'accept'),
            ('purchase_id', '=', self._context.get('active_id'))],
        help='To control quantity and unit price of the vendor bill, to be '
             'according to the quantity and unit price of the work acceptance.'
    )

    @api.multi
    def _compute_require_wa(self):
        for rec in self:
            enforce_wa = self.env.user.has_group(
                "purchase_work_acceptance.group_enforce_wa_on_invoice"
            )
            rec.require_wa = self.wa_id and enforce_wa

    def _prepare_invoice_line_from_po_line(self, line):
        res = super()._prepare_invoice_line_from_po_line(line)
        wa_line = self.wa_id.wa_line_ids.filtered(
            lambda l: l.purchase_line_id == line)
        if wa_line:
            res['quantity'] = wa_line.product_qty
            res['uom_id'] = wa_line.product_uom
        return res

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super().purchase_order_change()
        if self.wa_id:
            self.reference = self.wa_id.invoice_ref
            self.currency_id = self.wa_id.currency_id
        return res

    @api.multi
    def action_invoice_open(self):
        for rec in self:
            if rec.wa_id:
                wa_line = {}
                for line in rec.wa_id.wa_line_ids:
                    qty = line.product_uom._compute_quantity(
                        line.product_qty, line.product_id.uom_id)
                    if qty > 0.0:
                        if line.product_id.id in wa_line.keys():
                            qty_old = wa_line[line.product_id.id]
                            wa_line[line.product_id.id] = qty_old + qty
                        else:
                            wa_line[line.product_id.id] = qty
                invoice_line = {}
                for line in rec.invoice_line_ids:
                    qty = line.uom_id._compute_quantity(
                        line.quantity, line.product_id.uom_id)
                    if qty > 0.0:
                        if line.product_id.id in invoice_line.keys():
                            qty_old = invoice_line[line.product_id.id]
                            invoice_line[line.product_id.id] = qty_old + qty
                        else:
                            invoice_line[line.product_id.id] = qty
                if wa_line != invoice_line:
                    raise ValidationError(_(
                        'You cannot validate a bill if '
                        'Quantity not equal accepted quantity'))
        return super().action_invoice_open()
