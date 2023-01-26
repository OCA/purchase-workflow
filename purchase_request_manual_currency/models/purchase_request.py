# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    manual_currency = fields.Boolean(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    is_manual = fields.Boolean(compute="_compute_currency")
    type_currency = fields.Selection(
        selection=lambda self: self._get_label_currency_name(),
        default=lambda self: self._get_label_currency_name()[0][0],
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    manual_currency_rate = fields.Float(
        digits="Purchase Request Currency",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        help="Set new currency rate to apply on the purchase request\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase request and last currency",
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
    )
    total_company_currency = fields.Monetary(
        compute="_compute_total_company_currency",
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

    @api.depends("line_ids.estimated_cost_company_currency")
    def _compute_total_company_currency(self):
        """Convert total estimated cost to estimated cost company currency"""
        for rec in self:
            rec.total_company_currency = sum(
                rec.line_ids.mapped("estimated_cost_company_currency")
            )

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

    @api.onchange("manual_currency", "type_currency", "currency_id", "date_start")
    def _onchange_currency_change_rate(self):
        today = fields.Date.today()
        main_currency = self.env.company.currency_id
        amount_currency = main_currency._get_conversion_rate(
            main_currency, self.currency_id, self.company_id, self.date_start or today
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
            # Total company currency
            node = doc.xpath("//field[@name='total_company_currency']")
            if node:
                node[0].set(
                    "string", "Total Estimated Cost ({})".format(company_currency_name)
                )
            # Subtotal company currency
            node = doc.xpath("//field[@name='estimated_cost_company_currency']")
            if node:
                node[0].set(
                    "string", "Estimated Cost ({})".format(company_currency_name)
                )
            result["arch"] = etree.tostring(doc, encoding="unicode")
        return result
