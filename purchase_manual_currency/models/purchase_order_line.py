# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="order_id.company_currency_id",
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
        "order_id.manual_currency_rate",
        "order_id.type_currency",
        "order_id.manual_currency",
    )
    def _compute_amount_company_currency(self):
        for rec in self:
            rec.subtotal_company_currency = rec.price_subtotal
            # check multi-currency
            if rec.company_currency_id != rec.currency_id:
                # check manual currency
                if rec.order_id.manual_currency:
                    rate = (
                        rec.order_id.manual_currency_rate
                        if rec.order_id.type_currency == "inverse_company_rate"
                        else (1.0 / rec.order_id.manual_currency_rate)
                    )
                    rec.subtotal_company_currency = rec.price_subtotal * rate
                # default rate currency
                else:
                    rec.subtotal_company_currency = rec.currency_id._convert(
                        rec.price_subtotal,
                        rec.company_currency_id,
                        rec.company_id,
                        fields.Date.today(),
                    )
