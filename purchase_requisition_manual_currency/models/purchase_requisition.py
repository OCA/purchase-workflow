# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    manual_currency = fields.Boolean(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    type_currency = fields.Selection(
        selection=lambda self: self._get_label_currency_name(),
        default=lambda self: self._get_label_currency_name()[0][0],
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    custom_rate = fields.Float(
        digits="Purchase Currency",
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase order and last currency",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
    )
    currency_diff = fields.Boolean(
        compute="_compute_currency_diff",
        store=True,
    )

    @api.depends("currency_id")
    def _compute_currency_diff(self):
        for rec in self:
            rec.currency_diff = rec.company_currency_id != rec.currency_id

    def _get_label_currency_name(self):
        """Get label related currency"""
        names = {
            "company_currency_name": (
                self.env["res.company"].browse(self._context.get("company_id"))
                or self.env.company
            ).currency_id.name,
            "rate_currency_name": "Unit",
        }
        return [
            [
                "company_rate",
                _("%(rate_currency_name)s per %(company_currency_name)s", **names),
            ],
            [
                "inverse_company_rate",
                _("%(company_currency_name)s per %(rate_currency_name)s", **names),
            ],
        ]

    @api.onchange("manual_currency", "type_currency", "currency_id", "ordering_date")
    def _onchange_currency_change_rate(self):
        today = fields.Date.today()
        company_currency = self.env.company.currency_id
        amount_currency = company_currency._get_conversion_rate(
            company_currency,
            self.currency_id,
            self.company_id,
            self.ordering_date or today,
        )
        if self.type_currency == "inverse_company_rate":
            amount_currency = 1.0 / amount_currency
        self.custom_rate = amount_currency

    def action_refresh_currency(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Rate currency can refresh state draft only."))
        self._onchange_currency_change_rate()
        return True

    @api.model
    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """Change string name to company currency"""
        result = super()._fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            company_currency_name = (
                self.env["res.company"].browse(self._context.get("company_id"))
                or self.env.company
            ).currency_id.name
            doc = etree.XML(result["arch"])
            # Subtotal company currency
            node = doc.xpath("//field[@name='subtotal_company_currency']")
            if node:
                node[0].set("string", "Subtotal ({})".format(company_currency_name))
            result["arch"] = etree.tostring(doc, encoding="unicode")
        return result


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="requisition_id.company_currency_id",
        string="Company Currency",
    )
    subtotal_company_currency = fields.Monetary(
        string="Subtotal (Company Currency)",
        compute="_compute_amount_company_currency",
        store=True,
        currency_field="company_currency_id",
    )

    @api.depends(
        "price_unit",
        "product_qty",
        "requisition_id.custom_rate",
        "requisition_id.type_currency",
        "requisition_id.manual_currency",
    )
    def _compute_amount_company_currency(self):
        for rec in self:
            rec.subtotal_company_currency = rec.price_unit * rec.product_qty
            # check multi-currency
            if not rec.requisition_id.currency_diff:
                continue

            # check manual currency
            if rec.requisition_id.manual_currency:
                rate = (
                    rec.requisition_id.custom_rate
                    if rec.requisition_id.type_currency == "inverse_company_rate"
                    else (1.0 / rec.requisition_id.custom_rate)
                )
                rec.subtotal_company_currency = rec.subtotal_company_currency * rate
            # default rate currency
            else:
                rec.subtotal_company_currency = rec.requisition_id.currency_id._convert(
                    rec.subtotal_company_currency,
                    rec.company_currency_id,
                    rec.company_id,
                    fields.Date.today(),
                )
