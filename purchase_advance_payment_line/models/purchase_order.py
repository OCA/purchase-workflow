# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    payment_order_ok = fields.Boolean(
        related="payment_mode_id.payment_order_ok",
        store=True,
    )
    account_payment_line_count = fields.Integer(
        compute="_compute_account_payment_line_count",
        string="Payment Line Count",
        store=True,
    )
    account_payment_line_ids = fields.One2many(
        "account.payment.line",
        "purchase_id",
        string="Payment Lines",
        readonly=True,
    )
    ongoing_account_payment_line_count = fields.Integer(
        compute="_compute_account_payment_line_count",
        string="Ongoing Payment Line Count",
        store=True,
    )
    ongoing_account_payment_line_ids = fields.One2many(
        "account.payment.line",
        "purchase_id",
        domain=[("state", "not in", ["uploaded", "cancel"])],
        string="Ongoing Payment Lines",
    )

    @api.depends("account_payment_line_ids", "ongoing_account_payment_line_ids")
    def _compute_account_payment_line_count(self):
        for order in self:
            order.account_payment_line_count = len(order.account_payment_line_ids)
            order.ongoing_account_payment_line_count = len(
                order.ongoing_account_payment_line_ids
            )

    def action_view_ongoing_payment_lines(self):
        self.ensure_one()
        act = {
            "type": "ir.actions.act_window",
            "res_model": "account.payment.line",
            "context": dict(
                self.env.context or [],
                default_purchase_id=self.id,
            ),
        }
        if self.ongoing_account_payment_line_count == 1:
            act.update(
                {
                    "name": _("Payment Line"),
                    "view_mode": "form",
                    "res_id": self.account_payment_line_ids.id,
                }
            )
        else:
            act.update(
                {
                    "name": _("Payment Lines"),
                    "view_mode": "list",
                    # Use inverse field in domain to filter records
                    "domain": [("purchase_id", "=", self.id)],
                }
            )
        return act

    def action_create_account_payment_line(self):
        self.ensure_one()
        view = self.env.ref("account_payment_order.account_payment_line_form")
        return {
            "name": _("Create Payment Line"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.payment.line",
            "view_id": view.id,
            "target": "new",
            "type": "ir.actions.act_window",
            "context": dict(
                self.env.context,
                bypass_move_line_id_change=True,
                default_purchase_id=self.id,
                default_partner_id=self.partner_id.id,
                default_company_id=self.company_id.id,
                default_payment_mode_id=self.payment_mode_id.id,
            ),
        }
