# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order"

    has_qty_to_schedule = fields.Boolean(compute="_compute_has_qty_to_schedule")

    @api.depends("order_line", "order_line.qty_to_schedule")
    def _compute_has_qty_to_schedule(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if any(
                not float_is_zero(ol.qty_to_schedule, precision_digits=precision)
                for ol in order.order_line
            ):
                order.has_qty_to_schedule = True
            else:
                order.has_qty_to_schedule = False

    def button_confirm(self):
        for order in self:
            if order.has_qty_to_schedule:
                raise UserError(
                    _(
                        "You cannot approve a purchase order with pending or "
                        "negative quantity to schedule."
                    )
                )
        return super(PurchaseOrderLine, self).button_confirm()
