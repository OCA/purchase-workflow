# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    manual_currency = fields.Boolean()
    is_manual = fields.Boolean(compute="_compute_currency")
    type_currency = fields.Selection(
        selection=lambda self: self._get_label_currency_name(),
        default=lambda self: self._get_label_currency_name()[0][0],
    )
    manual_currency_rate = fields.Float(
        digits="Manual Currency",
        tracking=True,
        help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase order and last currency",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
    )
    total_company_currency = fields.Monetary(
        compute="_compute_total_company_currency",
        store=True,
        currency_field="company_currency_id",
    )
    currency_diff = fields.Boolean(
        compute="_compute_currency_diff",
        store=True,
    )

    @api.depends("currency_id")
    def _compute_currency_diff(self):
        for rec in self:
            rec.currency_diff = rec.company_currency_id != rec.currency_id

    @api.depends("order_line.subtotal_company_currency")
    def _compute_total_company_currency(self):
        """Convert total currency to company currency"""
        for rec in self:
            # check manual currency
            if rec.manual_currency:
                rate = (
                    rec.manual_currency_rate
                    if rec.type_currency == "inverse_company_rate"
                    else (1.0 / rec.manual_currency_rate)
                )
                rec.total_company_currency = rec.amount_total * rate
            # default rate currency
            else:
                rec.total_company_currency = rec.currency_id._convert(
                    rec.amount_total,
                    rec.company_currency_id,
                    rec.company_id,
                    fields.Date.today(),
                )

    def _get_label_currency_name(self):
        """Get label related currency"""
        names = {
            "company_currency_name": (
                self.env["res.company"].browse(self._context.get("company_id"))
                or self.env.company
            ).currency_id.name,
            "rate_currency_name": "Currency",
        }
        return [
            [
                "company_rate",
                _("%(rate_currency_name)s per 1 %(company_currency_name)s", **names),
            ],
            [
                "inverse_company_rate",
                _("%(company_currency_name)s per 1 %(rate_currency_name)s", **names),
            ],
        ]

    @api.onchange("manual_currency", "type_currency", "currency_id", "date_order")
    def _onchange_currency_change_rate(self):
        today = fields.Date.today()
        company_currency = self.env.company.currency_id
        amount_currency = company_currency._get_conversion_rate(
            company_currency,
            self.currency_id,
            self.company_id,
            self.date_order or today,
        )
        if self.type_currency == "inverse_company_rate":
            amount_currency = 1.0 / amount_currency
        self.manual_currency_rate = amount_currency

    @api.depends("currency_id")
    def _compute_currency(self):
        for rec in self:
            rec.is_manual = rec.currency_id != rec.company_id.currency_id

    def action_refresh_currency(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("Rate currency can refresh state draft only."))
        self._onchange_currency_change_rate()
        return True

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Change string name to company currency"""
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form":
            company_currency_name = (
                self.env["res.company"].browse(self._context.get("company_id"))
                or self.env.company
            ).currency_id.name
            doc = etree.XML(result["arch"])
            # Total company currency
            node = doc.xpath("//field[@name='total_company_currency']")
            if node:
                node[0].set("string", f"Total ({company_currency_name})")
            # Subtotal company currency
            node = doc.xpath("//field[@name='subtotal_company_currency']")
            if node:
                node[0].set("string", f"Subtotal ({company_currency_name})")
            result["arch"] = etree.tostring(doc, encoding="unicode")
        return result

    def action_view_invoice(self, invoices=False):
        result = super().action_view_invoice(invoices)
        if not invoices:
            return result

        for inv in invoices:
            # Get all purchase from invoice
            purchases = inv.invoice_line_ids.mapped("purchase_order_id")
            if len(set(purchases.mapped("manual_currency"))) != 1:
                raise UserError(
                    _("In invoice cannot have a mixture of different manual currency.")
                )
            elif len(set(purchases.mapped("manual_currency_rate"))) != 1:
                raise UserError(
                    _(
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
                        "manual_currency_rate": purchases[0].manual_currency_rate,
                    }
                )
        return result
