# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    promotion_period = fields.Char(
        string="Promotion", compute="_compute_promotion", store=True
    )
    promotion_date_start = fields.Date(compute="_compute_promotion", store=True)
    promotion_date_end = fields.Date(compute="_compute_promotion", store=True)

    @api.depends("supplier_id")
    def _compute_promotion(self):
        for orderpoint in self:
            if (
                orderpoint.supplier_id.is_promotion
                and orderpoint.supplier_id.date_start
                and orderpoint.supplier_id.date_end
            ):
                orderpoint.promotion_period = "{} - {}".format(
                    orderpoint.supplier_id.date_start, orderpoint.supplier_id.date_end
                )
                orderpoint.promotion_date_start = orderpoint.supplier_id.date_start
                orderpoint.promotion_date_end = orderpoint.supplier_id.date_end
            else:
                orderpoint.promotion_period = False
                orderpoint.promotion_date_start = False
                orderpoint.promotion_date_end = False
