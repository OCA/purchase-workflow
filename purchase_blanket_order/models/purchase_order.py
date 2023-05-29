# Copyright (C) 2018 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    blanket_order_id = fields.Many2one(
        "purchase.blanket.order",
        string="Origin blanket order",
        related="order_line.blanket_order_line.order_id",
        readonly=True,
    )

    @api.model
    def _check_exchausted_blanket_order_line(self):
        return any(
            line.blanket_order_line.remaining_qty < 0.0 for line in self.order_line
        )

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order._check_exchausted_blanket_order_line():
                raise ValidationError(
                    _(
                        "Cannot confirm order %s as one of the lines refers "
                        "to a blanket order that has no remaining quantity."
                    )
                    % order.name
                )
        return res

    @api.constrains("partner_id")
    def check_partner_id(self):
        for line in self.order_line:
            if line.blanket_order_line:
                if line.blanket_order_line.partner_id != self.partner_id:
                    raise ValidationError(
                        _(
                            "The vendor must be equal to the blanket order"
                            " lines vendor"
                        )
                    )

    @api.constrains("currency_id")
    def check_currency(self):
        for rec in self:
            if any(
                line.blanket_order_line.order_id.currency_id != rec.currency_id
                for line in rec.order_line.filtered(lambda x: x.blanket_order_line)
            ):
                raise ValidationError(
                    _(
                        "The currency of the blanket order must match with that "
                        "of the purchase order."
                    )
                )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    blanket_order_line = fields.Many2one(
        comodel_name="purchase.blanket.order.line", copy=False
    )

    def _get_assigned_bo_line(self, bo_lines):
        # We get the blanket order line with enough quantity and closest
        # scheduled date
        assigned_bo_line = False
        date_planned = fields.Date.from_string(self.date_planned) or date.today()
        date_delta = timedelta(days=365)
        for line in bo_lines.filtered(lambda l: l.date_schedule):
            date_schedule = fields.Date.from_string(line.date_schedule)
            if date_schedule and abs(date_schedule - date_planned) < date_delta:
                assigned_bo_line = line
                date_delta = abs(date_schedule - date_planned)
        if assigned_bo_line:
            return assigned_bo_line
        non_date_bo_lines = bo_lines.filtered(lambda l: not l.date_schedule)
        if non_date_bo_lines:
            return non_date_bo_lines[0]

    def _get_eligible_bo_lines_domain(self, base_qty):
        filters = [
            ("product_id", "=", self.product_id.id),
            ("remaining_qty", ">=", base_qty),
            ("currency_id", "=", self.order_id.currency_id.id),
            ("order_id.state", "=", "open"),
        ]
        if self.order_id.partner_id:
            filters.append(("partner_id", "=", self.order_id.partner_id.id))
        return filters

    def _get_eligible_bo_lines(self):
        base_qty = self.product_uom._compute_quantity(
            self.product_qty, self.product_id.uom_id
        )
        filters = self._get_eligible_bo_lines_domain(base_qty)
        return self.env["purchase.blanket.order.line"].search(filters)

    def get_assigned_bo_line(self):
        self.ensure_one()
        eligible_bo_lines = self._get_eligible_bo_lines()
        if eligible_bo_lines:
            if (
                not self.blanket_order_line
                or self.blanket_order_line not in eligible_bo_lines
            ):
                self.blanket_order_line = self._get_assigned_bo_line(eligible_bo_lines)
        else:
            self.blanket_order_line = False
        self.onchange_blanket_order_line()
        return {"domain": {"blanket_order_line": [("id", "in", eligible_bo_lines.ids)]}}

    @api.onchange("product_id", "partner_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        # If product has changed remove the relation with blanket order line
        if self.product_id:
            return self.get_assigned_bo_line()
        return res

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        res = super()._onchange_quantity()
        if self.product_id and not self.env.context.get("skip_blanket_find", False):
            return self.get_assigned_bo_line()
        return res

    @api.onchange("blanket_order_line")
    def onchange_blanket_order_line(self):
        bol = self.blanket_order_line
        if bol:
            self.product_id = bol.product_id
            if bol.date_schedule:
                self.date_planned = bol.date_schedule
            if bol.product_uom != self.product_uom:
                price_unit = bol.product_uom._compute_price(
                    bol.price_unit, self.product_uom
                )
            else:
                price_unit = bol.price_unit
            self.price_unit = price_unit
            if bol.taxes_id:
                self.taxes_id = bol.taxes_id
        else:
            self._compute_tax_id()
            self.with_context(skip_blanket_find=True)._onchange_quantity()

    @api.constrains("date_planned")
    def check_date_planned(self):
        for line in self:
            date_planned = fields.Date.from_string(line.date_planned)
            if (
                line.blanket_order_line
                and line.blanket_order_line.date_schedule
                and line.blanket_order_line.date_schedule != date_planned
            ):
                raise ValidationError(
                    _(
                        "Schedule dates defined on the Purchase Order Line "
                        "and on the Blanket Order Line do not match."
                    )
                )

    @api.constrains("currency_id")
    def check_currency(self):
        for line in self:
            blanket_currency = line.blanket_order_line.order_id.currency_id
            if blanket_currency and line.order_id.currency_id != blanket_currency:
                raise ValidationError(
                    _(
                        "The currency of the blanket order must match with that "
                        "of the purchase order."
                    )
                )
