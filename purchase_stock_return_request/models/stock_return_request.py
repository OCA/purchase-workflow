# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockReturnRequest(models.Model):
    _inherit = 'stock.return.request'

    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Involved Purchases',
        readonly=True,
        copy=False,
    )

    def _prepare_move_default_values(self, line, qty, move):
        """Extend this method to add values to return move"""
        vals = super()._prepare_move_default_values(line, qty, move)
        vals.update({
            'purchase_line_id': move.purchase_line_id.id,
            'to_refund': line.request_id.to_refund,
        })
        return vals

    def _action_confirm(self):
        res = super()._action_confirm()
        if self.state == 'confirmed':
            self.purchase_order_ids = self.returned_picking_ids.mapped(
                'purchase_id')
        return res

    def action_view_purchases(self):
        """Display returned purchases"""
        action = action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]
        result['context'] = {}
        purchases = self.mapped('purchase_order_ids')
        if not purchases or len(purchases) > 1:
            result['domain'] = "[('id', 'in', %s)]" % (purchases.ids)
        elif len(purchases) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchases.id
        return result

    @api.model
    def _get_po_price_unit(self, move_line):
        """We take the price applied in the original """
        po_line = move_line.move_id and move_line.move_id.purchase_line_id
        return po_line and po_line._get_stock_move_price_unit() or 0.0

    @api.model
    def _get_po_line_amount(self, move_line, qty=0):
        """Computes amounts to be shown in the report"""
        po_line = move_line.move_id and move_line.move_id.purchase_line_id
        to_refund = move_line.move_id and move_line.move_id.to_refund
        if not po_line or not to_refund:
            return {
                'price_tax': 0,
                'price_total': 0,
                'price_subtotal': 0,
            }
        price_unit = self._get_po_price_unit(move_line)
        taxes = po_line.taxes_id.compute_all(
            price_unit, po_line.order_id.currency_id, qty,
            product=po_line.product_id, partner=po_line.order_id.partner_id)
        return {
            'price_tax': sum(
                t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            'price_total': taxes['total_included'],
            'price_subtotal': taxes['total_excluded'],
        }

    @api.model
    def _get_po_amount_all(self, move_lines, currency):
        amount_untaxed = amount_tax = 0.0
        for ml in move_lines.filtered('move_id.purchase_line_id'):
            line_amount = self._get_po_line_amount(ml, ml.qty_done)
            amount_untaxed += line_amount['price_subtotal']
            amount_tax += line_amount['price_tax']
        return {
            'amount_untaxed': currency.round(amount_untaxed),
            'amount_tax': currency.round(amount_tax),
            'amount_total': amount_untaxed + amount_tax,
        }
