# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class StockOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_product_context(self):
        res = super()._get_product_context()
        if not self.product_id or not self.location_id:
            return res
        seller = self.product_id._select_seller(quantity=None)
        if seller:
            lead_days, __ = self.rule_ids._get_lead_days(self.product_id)
            availability_date = seller._get_next_availability_date()
            res.update({"to_date": availability_date + seller._get_delay_delta()})
        return res
