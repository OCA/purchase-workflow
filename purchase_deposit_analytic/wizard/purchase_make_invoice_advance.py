# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env["decimal.precision"].precision_get(
            "Percentage Analytic"
        ),
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        active_ids = self.env.context.get("active_ids", [])
        purchases = self.env["purchase.order"].browse(active_ids)

        val_default = {}
        if purchases:
            val_default["company_id"] = purchases.company_id.id
            analytic_account_ids = set()
            for analytics in purchases.order_line.mapped("analytic_distribution"):
                if analytics:
                    analytic_account_ids.update(int(aa) for aa in analytics.keys())
            if len(analytic_account_ids) == 1:
                val_default["analytic_distribution"] = {
                    str(list(analytic_account_ids)[0]): 100
                }
        res.update(val_default)
        return res

    def _prepare_advance_purchase_line(self, order, product, tax_ids, amount):
        res = super()._prepare_advance_purchase_line(order, product, tax_ids, amount)
        if self.analytic_distribution:
            res["analytic_distribution"] = self.analytic_distribution
        return res
