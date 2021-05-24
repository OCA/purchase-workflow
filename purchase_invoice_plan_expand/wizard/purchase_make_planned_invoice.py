# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.make.planned.invoice"

    def create_invoices_by_plan(self):
        purchase = self.env["purchase.order"].browse(self._context.get("active_id"))
        purchase.ensure_one()
        group_percent = purchase.invoice_plan_ids._get_percent_by_expand_group()
        self = self.with_context(expand=purchase.expand, group_percent=group_percent)
        return super().create_invoices_by_plan()
