# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class PurchaseInvoicePlan(models.Model):
    _inherit = 'purchase.invoice.plan'

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = super()._get_plan_qty(order_line, percent)
        if order_line.is_deposit:
            plan_qty = -1 * (percent/100)
        return plan_qty
