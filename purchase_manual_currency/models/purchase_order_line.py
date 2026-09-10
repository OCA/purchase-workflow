# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="order_id.company_currency_id",
        store=True,
        string="Company Currency",
    )
    subtotal_company_currency = fields.Monetary(
        string="Subtotal (Company Currency)",
        compute="_compute_amount_company_currency",
        store=True,
        currency_field="company_currency_id",
    )

    @api.depends(
        "price_subtotal",
        "order_id.currency_rate",
        "order_id.type_currency",
        "order_id.manual_currency",
    )
    def _compute_amount_company_currency(self):
        for line in self:
            line.subtotal_company_currency = line.price_subtotal
            if line.company_currency_id != line.currency_id:
                order = line.order_id
                rate = (
                    order.currency_rate
                    if order.type_currency == "inverse_company_rate"
                    else (1.0 / order.currency_rate)
                )
                line.subtotal_company_currency = line.price_subtotal * rate

    def _prepare_base_line_for_taxes_computation(self):
        self.ensure_one()
        order = self.order_id
        if order.manual_currency and order.type_currency == "inverse_company_rate":
            # Convert Rate back to company_rate
            rate = 1
            if order.currency_rate:
                rate = 1 / order.currency_rate
            return self.env["account.tax"]._prepare_base_line_for_taxes_computation(
                self,
                tax_ids=self.taxes_id,
                quantity=self.product_qty,
                partner_id=self.order_id.partner_id,
                currency_id=self.order_id.currency_id
                or self.order_id.company_id.currency_id,
                rate=rate,
            )
        return super()._prepare_base_line_for_taxes_computation()
