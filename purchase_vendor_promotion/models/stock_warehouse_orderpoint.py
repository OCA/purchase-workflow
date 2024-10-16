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
    supplier_id = fields.Many2one(
        compute="_compute_supplier_id", readonly=False, store=True
    )

    @api.depends("route_id", "route_id.force_vendor_with_best_promotion")
    def _compute_supplier_id(self):
        for rec in self:
            if rec.route_id and rec.route_id.force_vendor_with_best_promotion:
                allowed_company_ids = rec.allowed_location_ids.company_id
                suppliers = rec.product_id._prepare_sellers(False).filtered(
                    lambda x: x.company_id in allowed_company_ids
                )
                promotion_suppliers = suppliers.filtered(
                    lambda x: x._is_promotion_active_or_upcoming()
                )
                if promotion_suppliers:
                    rec.supplier_id = promotion_suppliers[0].id
                elif suppliers:
                    rec.supplier_id = suppliers[0].id

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
