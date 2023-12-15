# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """Get price unit from manual currency"""
        self.ensure_one()
        line = self.purchase_line_id
        order = line.order_id
        if (
            order.manual_currency
            and self.product_id.id == line.product_id.id
            and order.currency_id != order.company_id.currency_id
        ):
            rate = (
                order.manual_currency_rate
                if order.type_currency == "inverse_company_rate"
                else (1.0 / order.manual_currency_rate)
            )
            return line.price_unit * rate
        return super()._get_price_unit()
