# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_compare
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'qty_invoiced', 'product_id.purchase_method',
                 'qty_received')
    def _compute_qty_to_invoice(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            if line.product_id.purchase_method == 'receive':
                qty = line.qty_received - line.qty_invoiced
                if float_compare(qty, 0.0, precision_digits=precision):
                    line.qty_to_invoice = qty
                else:
                    line.qty_to_invoice = 0.0
            else:
                line.qty_to_invoice = line.product_qty - line.qty_invoiced

    @api.depends('move_ids.state', 'move_ids.product_uom',
                 'move_ids.product_uom_qty')
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
        res = []
        order_ids = []
        # To evaluate the operation 'is equal to', change the operator value
        if operator == '=':
            operator = '=='
        for po in self.search([]):
            qty_to_invoice = sum(po.mapped('order_line.qty_to_invoice'))
            flag = safe_eval(str(qty_to_invoice) + operator +
                             str(value))
            if flag:
                order_ids.append(po.id)
        res.append(('id', 'in', order_ids))
        return res

    @api.model
    def _search_qty_to_receive(self, operator, value):
        res = []
        order_ids = []
        # To evaluate the operation 'is equal to', change the operator value
        if operator == '=':
            operator = '=='
        for po in self.search([]):
            qty_to_receive = sum(po.mapped('order_line.qty_to_receive'))
            flag = safe_eval(str(qty_to_receive) + operator +
                             str(value))
            if flag:
                order_ids.append(po.id)
        res.append(('id', 'in', order_ids))
        return res

    qty_to_invoice = fields.Float(compute='_compute_qty_to_invoice',
                                  search='_search_qty_to_invoice',
                                  string="Qty to Bill")
    qty_to_receive = fields.Float(compute='_compute_qty_to_receive',
                                  search='_search_qty_to_receive',
                                  string="Qty to Receive")
