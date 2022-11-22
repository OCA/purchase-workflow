# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class StockOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    lead_days_datetime = fields.Datetime(compute="_compute_lead_days_datetime")

    @api.depends(
        "rule_ids",
        "product_id.seller_ids",
        "product_id.seller_ids.delay",
        "product_id.seller_ids.delay_hour",
    )
    def _compute_lead_days_datetime(self):
        for orderpoint in self.with_context(bypass_delay_description=True):
            if not orderpoint.product_id or not orderpoint.location_id:
                orderpoint.lead_days_datetime = False
                continue
            rules = orderpoint.rule_ids
            buy_rule = rules.filtered(lambda r: r.action == "buy")
            seller = orderpoint.product_id.with_company(
                buy_rule.company_id
            )._select_seller(quantity=None)
            lead_days, __ = rules._get_lead_days(orderpoint.product_id)
            lead_days_td = relativedelta(days=lead_days)
            lead_days_datetime = seller._get_next_availability_date() + lead_days_td
            orderpoint.lead_days_datetime = lead_days_datetime

    def _get_procurement_datetime(self):
        self.ensure_one()
        return self.lead_days_datetime

    def _get_product_context(self):
        res = super()._get_product_context()
        if not self.product_id or not self.location_id:
            return res
        seller = self.product_id._select_seller(quantity=None)
        if seller:
            delivery_date = seller._get_next_delivery_date()
            res.update({"to_date": delivery_date})
        return res

    @api.depends("product_id.seller_ids.delay_hour")
    def _compute_lead_days(self):
        return super()._compute_lead_days()
