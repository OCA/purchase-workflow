# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        res = super()._onchange_requisition_id()
        requisition = self.requisition_id
        if not requisition:
            return res
        self.write(
            {
                "manual_currency": requisition.manual_currency,
                "type_currency": requisition.type_currency,
            }
        )
        return res

    @api.onchange("manual_currency", "type_currency", "currency_id", "date_order")
    def _onchange_currency_change_rate(self):
        res = super()._onchange_currency_change_rate()
        if self.requisition_id:
            self.manual_currency_rate = self.requisition_id.manual_currency_rate
        return res
