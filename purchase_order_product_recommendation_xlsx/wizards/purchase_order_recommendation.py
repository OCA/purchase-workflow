# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    def export_xlsx(self):
        self.ensure_one()
        return self.env.ref(
            "purchase_order_product_recommendation_xlsx.recommendation_xlsx"
        ).report_action(self)


class PurchaseOrderRecommendationLine(models.TransientModel):
    _inherit = "purchase.order.recommendation.line"

    price_unit = fields.Monetary(string="Price")
    units_received = fields.Float(string="Qty Received")
    units_delivered = fields.Float(string="Qty delivered")
    units_avg_delivered = fields.Float(string="Qty Dlvd./day")
    units_available = fields.Float(string="Qty On Hand")
    units_virtual_available = fields.Float(string="Forecasted Qty")
    units_included = fields.Float(string="Qty")
