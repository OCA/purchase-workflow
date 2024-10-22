# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_request_line(self, request_id, procurement):
        res = super()._prepare_purchase_request_line(request_id, procurement)
        sale_note = procurement.values.get("sale_note")
        if sale_note:
            res["specifications"] = sale_note
        return res
