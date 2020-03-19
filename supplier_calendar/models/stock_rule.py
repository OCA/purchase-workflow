# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_purchase_order_date(self, product_id, product_qty, product_uom,
                                 values, partner, schedule_date):
        res = super()._get_purchase_order_date(
            product_id,
            product_qty, product_uom,
            values, partner, schedule_date)
        seller = product_id.with_context(force_company=values[
            'company_id'].id)._select_seller(partner_id=partner,
                                             quantity=product_qty,
                                             date=schedule_date and
                                             schedule_date.date(),
                                             uom_id=product_uom)
        if seller:
            delay = -1 * seller.delay
            res = seller.name.supplier_plan_days(schedule_date, delay)
        return res
