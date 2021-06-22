# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SelectWorkAcceptanceWizard(models.TransientModel):
    _inherit = "select.work.acceptance.wizard"

    def _get_purchase_order_with_context(self, order_id):
        order = super()._get_purchase_order_with_context(order_id)
        return order.with_context(invoice_plan_id=self.wa_id.installment_id.id)
