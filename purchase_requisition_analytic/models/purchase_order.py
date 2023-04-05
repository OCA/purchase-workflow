# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.account_analytic_id = (
            res.account_analytic_id or res.order_id.requisition_id.analytic_account_id
        )
        return res
