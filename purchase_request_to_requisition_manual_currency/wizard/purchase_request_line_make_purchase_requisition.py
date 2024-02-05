# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _prepare_purchase_requisition(self, item, picking_type_id, company_id):
        data = super()._prepare_purchase_requisition(item, picking_type_id, company_id)
        model = self._context.get("active_model")
        if model == "purchase.request":
            active_ids = self._context.get("active_ids")
            pr = self.env[model].browse(active_ids)
            data.update(
                {
                    "manual_currency": pr.manual_currency,
                    "type_currency": pr.type_currency,
                    "manual_currency_rate": pr.manual_currency_rate,
                }
            )
        elif model == "purchase.request.line":
            active_id = self._context.get("active_id")
            pr_line = self.env[model].browse(active_id)
            data.update(
                {
                    "manual_currency": pr_line.request_id.manual_currency,
                    "type_currency": pr_line.request_id.type_currency,
                    "manual_currency_rate": pr_line.request_id.manual_currency_rate,
                }
            )
        return data
