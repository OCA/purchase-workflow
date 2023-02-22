# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
    )

    @api.model
    def default_get(self, field_list):
        """Default analytic account, tags if there is 1 value in order line"""
        res = super().default_get(field_list)
        active_id = self._context.get("active_id")
        order = self.env["purchase.order"].browse(active_id)
        order_line = order.order_line
        account_analytics = order_line.mapped("account_analytic_id")
        analytic_tags = order_line.mapped("analytic_tag_ids")
        val_default = {}
        val_default["account_analytic_id"] = (
            account_analytics.id if len(account_analytics) == 1 else False
        )
        val_default["analytic_tag_ids"] = (
            analytic_tags.ids
            if analytic_tags == order_line[0].analytic_tag_ids
            else False
        )
        res.update(val_default)
        return res

    def _prepare_advance_purchase_line(self, order, product, tax_ids, amount):
        res = super()._prepare_advance_purchase_line(order, product, tax_ids, amount)
        res.update(
            {
                "account_analytic_id": self.account_analytic_id.id,
                "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
            }
        )
        return res
