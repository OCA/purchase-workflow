# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        res = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if not line.orderpoint_id:
            # if the po line is generated from a procurement (stock rule)
            # base the computation on what is really needed.
            # eg:
            # 1 product bought by package of 10 units
            # generate a procurement for 5 units
            # -> a po line for 1 pack of 10 units is created
            # generate a second procurement for 5 units
            # without the following code, the po line will be updated to
            # order 2 pack of 10 units which is wrong
            #
            # This code is not needed for orderpoint because in this case,
            # the real need is oncsidered thanks
            # to _quantity_in_progress() method
            product_qty_needed = line.product_qty_needed + product_qty
            res["product_qty_needed"] = product_qty_needed
            res["product_qty"] = product_qty_needed
        return res
