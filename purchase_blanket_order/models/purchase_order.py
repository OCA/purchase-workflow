# Copyright (C) 2018 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

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
        comodel_name="purchase.blanket.order.line",
        compute="_compute_blanket_order_line",
        store=True,
        copy=False,
        domain="[('product_id', '=', product_id)]",
    )

    @api.depends("blanket_order_line")
    def _compute_date_planned(self):
        res = super()._compute_date_planned()
        for item in self.filtered("blanket_order_line"):
            item.date_planned = item.blanket_order_line.date_schedule
        return res

    @api.depends("product_id", "product_qty", "product_uom", "date_planned")
    def _compute_blanket_order_line(self):
        for item in self.filtered(lambda x: x.product_id):
            eligible_bo_lines = item._get_eligible_bo_lines()
            item.blanket_order_line = (
                item._get_assigned_bo_line(eligible_bo_lines)
                if eligible_bo_lines
                else item.blanket_order_line
            )

    def _get_assigned_bo_line(self, bo_lines):
        # We get the blanket order line with enough quantity and closest
        # scheduled date
        dates_list = self.order_id.order_line.filtered(
            lambda x: not x.display_type and x.date_planned
        ).mapped("date_planned")
        min_date = min(dates_list).date() if dates_list else date.today()
        max_date = max(dates_list).date() if dates_list else date.today()
        items = bo_lines.filtered(
            lambda x: x.date_schedule
            and x.date_schedule >= min_date
            and x.date_schedule <= max_date
        )
        assigned_bo_lines = items or bo_lines.filtered(lambda x: not x.date_schedule)
        return fields.first(assigned_bo_lines)

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
        domain = self._get_eligible_bo_lines_domain(base_qty)
        return self.env["purchase.blanket.order.line"].search(domain)

    @api.onchange("blanket_order_line")
    def onchange_blanket_order_line(self):
        if self.blanket_order_line and self.blanket_order_line.taxes_id:
            self.taxes_id = self.blanket_order_line.taxes_id

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
