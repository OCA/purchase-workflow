# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'qty_invoiced',
                 'invoice_lines.invoice_id.state',
                 'order_id.state', 'move_ids.state', 'qty_received')
    def _compute_qty_to_invoice(self):
        for line in self:
            if line.product_id.purchase_method == 'receive':
                qty = line.qty_received - line.qty_invoiced
                if qty >= 0.0:
                    line.qty_to_invoice = qty
                else:
                    line.qty_to_invoice = 0.0
            else:
                line.qty_to_invoice = line.product_qty - line.qty_invoiced

    @api.depends('order_id.state', 'move_ids.state', 'product_qty')
    def _compute_qty_to_receive(self):
        for line in self:
            total = 0.0
            for move in line.move_ids.filtered(
                    lambda m: m.state not in ('cancel', 'done')):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom)
                else:
                    total += move.product_uom_qty
            line.qty_to_receive = total

    qty_to_invoice = fields.Float(compute='_compute_qty_to_invoice',
                                  digits=dp.get_precision(
                                      'Product Unit of Measure'),
                                  copy=False,
                                  string="Qty to Bill", store=True)
    qty_to_receive = fields.Float(compute='_compute_qty_to_receive',
                                  digits=dp.get_precision(
                                      'Product Unit of Measure'),
                                  copy=False,
                                  string="Qty to Receive", store=True)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _compute_qty_to_invoice(self):
        for po in self:
            po.qty_to_invoice = sum(po.mapped('order_line.qty_to_invoice'))

    def _compute_qty_to_receive(self):
        for po in self:
            po.qty_to_receive = sum(po.mapped('order_line.qty_to_receive'))

    @api.model
    def _search_qty_to_invoice(self, operator, value):
        po_line_obj = self.env['purchase.order.line']
        res = []
        po_lines = po_line_obj.search(
            [('qty_to_invoice', operator, value)])
        order_ids = po_lines.mapped('order_id')
        res.append(('id', 'in', order_ids.ids))
        return res

    @api.model
    def _search_qty_to_receive(self, operator, value):
        po_line_obj = self.env['purchase.order.line']
        res = []
        po_lines = po_line_obj.search(
            [('qty_to_receive', operator, value)])
        order_ids = po_lines.mapped('order_id')
        res.append(('id', 'in', order_ids.ids))
        return res

    qty_to_invoice = fields.Float(compute='_compute_qty_to_invoice',
                                  search='_search_qty_to_invoice',
                                  string="Qty to Bill",
                                  default=0.0)
    qty_to_receive = fields.Float(compute='_compute_qty_to_receive',
                                  search='_search_qty_to_receive',
                                  string="Qty to Receive",
                                  default=0.0)
