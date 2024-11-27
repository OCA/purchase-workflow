# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _prepare_purchase_requisition(self, item, picking_type_id, company_id):
        data = super()._prepare_purchase_requisition(item, picking_type_id, company_id)
        data.update(
            {
                "manual_currency": item.request_id.manual_currency,
                "type_currency": item.request_id.type_currency,
                "manual_currency_rate": item.request_id.manual_currency_rate,
            }
        )
        return data
