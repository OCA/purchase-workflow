# Copyright 2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        # If the purchase order is in manual currency, we need to convert the
        # price unit to the company currency by using the manual rate, instead
        # of the default rate.
        self.ensure_one()
        base_price = super()._get_price_unit()
        if not isinstance(base_price, dict):
            base_price = {self.env["stock.lot"]: base_price}
        p_order = self.purchase_line_id.order_id
        if p_order and p_order.manual_currency:
            company_curr = p_order.company_id.currency_id
            po_curr = p_order.currency_id
            date = fields.Date.context_today(self)
            converted_dict = {}
            for lot, cost_val in base_price.items():
                # Convert from company currency to PO currency
                price_po_curr = company_curr._convert(
                    cost_val, po_curr, p_order.company_id, date, round=False
                )
                # Convert the price to the company currency, using the manual rate
                rate = (
                    p_order.manual_currency_rate
                    if p_order.type_currency == "inverse_company_rate"
                    else (1.0 / p_order.manual_currency_rate)
                )
                converted_dict[lot] = price_po_curr * rate
            return converted_dict
        return base_price
