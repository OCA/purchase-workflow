# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _compute_qty_to_invoice(self):
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for po in self:
            qty_to_invoice = sum(po.mapped("order_line.qty_to_invoice"))
            po.pending_qty_to_invoice = not float_is_zero(
                qty_to_invoice, precision_digits=dp
            )
            po.qty_to_invoice = qty_to_invoice

    def _compute_qty_to_receive(self):
        for po in self:
            qty_to_receive = sum(po.mapped("order_line.qty_to_receive"))
            po.pending_qty_to_receive = qty_to_receive > 0.0
            po.qty_to_receive = qty_to_receive

    @api.model
    def _search_pending_qty_to_receive(self, operator, value):
        if operator != "=" or not isinstance(value, bool):
            raise ValueError(_("Unsupported search operator"))
        po_line_obj = self.env["purchase.order.line"]
        po_lines = po_line_obj.search([("qty_to_receive", ">", 0.0)])
        orders = po_lines.mapped("order_id")
        if value:
            return [("id", "in", orders.ids)]
        else:
            return [("id", "not in", orders.ids)]

    @api.model
    def _search_pending_qty_to_invoice(self, operator, value):
        if operator != "=" or not isinstance(value, bool):
            raise ValueError(_("Unsupported search operator"))
        po_line_obj = self.env["purchase.order.line"]
        po_lines = po_line_obj.search([("qty_to_invoice", ">", 0.0)])
        orders = po_lines.mapped("order_id")
        if value:
            return [("id", "in", orders.ids)]
        else:
            return [("id", "not in", orders.ids)]

    qty_to_invoice = fields.Float(
        compute="_compute_qty_to_invoice",
        string="Qty to Bill",
        default=0.0,
    )
    pending_qty_to_invoice = fields.Boolean(
        compute="_compute_qty_to_invoice",
        search="_search_pending_qty_to_invoice",
        string="Pending Qty to Bill",
    )
    qty_to_receive = fields.Float(
        compute="_compute_qty_to_receive",
        string="Qty to Receive",
        default=0.0,
    )
    pending_qty_to_receive = fields.Boolean(
        compute="_compute_qty_to_receive",
        search="_search_pending_qty_to_receive",
        string="Pending Qty to Receive",
    )
