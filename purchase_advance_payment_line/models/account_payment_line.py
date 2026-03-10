# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        check_company=True,
    )
    purchase_amount_residual = fields.Float(
        related="purchase_id.amount_residual",
        store=True,
    )
    payment_mode_id = fields.Many2one(
        related="order_id.payment_mode_id",
        store=True,
    )

    @api.onchange("move_line_id")
    def move_line_id_change(self):
        # if there is no `move_line_id`, super() sets the following fields' value:
        # - partner_id, partner_bank_id, communication: `False`
        # - amount_currency: `0.0`
        # - currency_id: `self.env.user.company_id.currency_id`
        if not self.env.context.get("bypass_move_line_id_change"):
            return super().move_line_id_change()

    @api.model
    def _search_or_create_payment_order_get_domain(self, vals):
        mode = vals.get("payment_mode_id") or self.env.context.get(
            "default_payment_mode_id"
        )
        mode_id = mode and int(mode) or False
        return [("state", "=", "draft"), ("payment_mode_id", "=", mode_id)]

    @api.model
    def _search_or_create_payment_order_get_values(self, vals):
        mode = vals.get("payment_mode_id") or self.env.context.get(
            "default_payment_mode_id"
        )
        mode_id = mode and int(mode) or False
        return {"payment_type": "outbound", "payment_mode_id": mode_id}

    @api.model
    def _search_or_create_payment_order(self, vals):
        domain = self._search_or_create_payment_order_get_domain(vals)
        values = self._search_or_create_payment_order_get_values(vals)
        order = self.env["account.payment.order"]
        return order.search(domain, limit=1) or order.create(values)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("order_id"):
                order = self._search_or_create_payment_order(vals)
                vals["order_id"] = order.id
        return super().create(vals_list)

    @api.constrains("currency_id", "amount_currency", "purchase_amount_residual")
    def _check_amount(self):
        for pline in self.filtered("purchase_id"):
            if pline.currency_id.compare_amounts(pline.amount_currency, 0.0) <= 0:
                raise exceptions.ValidationError(
                    _("Amount of advance must be positive.")
                )
            if (
                pline.currency_id.compare_amounts(
                    pline.amount_currency, pline.purchase_amount_residual
                )
                > 0
            ):
                raise exceptions.ValidationError(
                    _("Amount of advance is greater than residual amount on purchase")
                )

    def _prepare_account_payment_vals(self):
        # FIXME: currently works only when payment line
        #        has the same associated purchase order
        vals = super()._prepare_account_payment_vals()
        if self.purchase_id:
            vals["purchase_id"] = self.purchase_id[0].id
        return vals
