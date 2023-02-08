# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "product_qty", "qty_invoiced", "product_id.purchase_method", "qty_received"
    )
    def _compute_qty_to_invoice(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self:
            if line.product_id.purchase_method == "receive":
                qty = line.qty_received - line.qty_invoiced
                # Check if the result is zero with the correct precision to avoid
                # floats like 0.000001 that don't match the filter qty_to_invoice != 0
                if float_is_zero(qty, precision_digits=precision):
                    qty = 0.0
                line.qty_to_invoice = qty
            else:
                qty = line.product_qty - line.qty_invoiced
                # Check if the result is zero with the correct precision to avoid
                # floats like 0.000001 that don't match the filter qty_to_invoice != 0
                if float_is_zero(qty, precision_digits=precision):
                    qty = 0.0
                line.qty_to_invoice = qty

    @api.depends(
        "move_ids.state",
        "move_ids.product_uom",
        "move_ids.product_uom_qty",
        "product_qty",
        "qty_received",
    )
    def _compute_qty_to_receive(self):
        service_lines = self.filtered(lambda l: l.product_id.type == "service")
        for line in self - service_lines:
            total = 0.0
            for move in line.move_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            ):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom
                    )
                else:
                    total += move.product_uom_qty
            line.qty_to_receive = total
        for line in service_lines:
            line.qty_to_receive = line.product_qty - line.qty_received

    qty_to_invoice = fields.Float(
        compute="_compute_qty_to_invoice",
        digits="Product Unit of Measure",
        copy=False,
        string="Qty to Bill",
        store=True,
    )
    qty_to_receive = fields.Float(
        compute="_compute_qty_to_receive",
        digits="Product Unit of Measure",
        copy=False,
        string="Qty to Receive",
        store=True,
    )


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
        search="_search_qty_to_invoice",
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
        search="_search_qty_to_receive",
        string="Qty to Receive",
        default=0.0,
    )
    pending_qty_to_receive = fields.Boolean(
        compute="_compute_qty_to_receive",
        search="_search_pending_qty_to_receive",
        string="Pending Qty to Receive",
    )
