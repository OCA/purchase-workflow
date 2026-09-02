# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    manual_currency = fields.Boolean()
    type_currency = fields.Selection(
        selection=lambda self: self._get_label_currency_name(),
        default=lambda self: self._get_label_currency_name()[0][0],
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
    )

    def _get_label_currency_name(self):
        """Get label related currency"""
        names = {
            "company_currency_name": (
                self.env["res.company"].browse(self.env.context.get("company_id"))
                or self.env.company
            ).currency_id.name,
            "rate_currency_name": "Currency",
        }
        return [
            [
                "company_rate",
                self.env._(
                    "%(rate_currency_name)s per 1 %(company_currency_name)s", **names
                ),
            ],
            [
                "inverse_company_rate",
                self.env._(
                    "%(company_currency_name)s per 1 %(rate_currency_name)s", **names
                ),
            ],
        ]

    @api.depends(
        "order_line.price_subtotal", "company_id", "currency_id", "currency_rate"
    )
    def _amount_all(self):
        """Add currency_rate dependency to trigger recompute"""
        return super()._amount_all()

    @api.depends(
        "currency_id", "date_order", "company_id", "manual_currency", "type_currency"
    )
    def _compute_currency_rate(self):
        res = super()._compute_currency_rate()
        for order in self:
            if order.manual_currency and order.type_currency == "inverse_company_rate":
                order.currency_rate = 1.0 / order.currency_rate
        return res

    def action_refresh_currency(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(
                self.env._("Rate currency can refresh state draft only.")
            )
        return self._compute_currency_rate()

    def action_view_invoice(self, invoices=False):
        result = super().action_view_invoice(invoices)
        if not invoices:
            return result

        for inv in invoices:
            # Get all purchase from invoice
            purchases = inv.invoice_line_ids.mapped("purchase_order_id")
            if len(set(purchases.mapped("manual_currency"))) != 1:
                raise UserError(
                    self.env._(
                        "In invoice cannot have a mixture of different manual currency."
                    )
                )
            elif len(set(purchases.mapped("currency_rate"))) != 1:
                raise UserError(
                    self.env._(
                        "In invoice cannot have a mixture of different "
                        "manual currency rates in purchases."
                    )
                )
            # Update manual currency from purchase to invoice
            if (
                self.env.company.manual_currency_po_inv == "currency_po"
                and purchases[0].manual_currency
            ):
                inv.write(
                    {
                        "manual_currency": purchases[0].manual_currency,
                        "type_currency": purchases[0].type_currency,
                        "manual_currency_rate": purchases[0].currency_rate,
                    }
                )
        return result
