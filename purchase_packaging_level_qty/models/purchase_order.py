from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_transport_qty = fields.Float(
        compute="_compute_total_transport_packaging_qty",
        store=True,
    )

    transport_packaging_level_id = fields.Many2one(
        "product.packaging.level",
        compute="_compute_purchase_transport_packaging_level",
    )

    transport_packaging_level_total_qty = fields.Char(
        compute="_compute_transport_packaging_level_total_qty",
    )

    def _compute_purchase_transport_packaging_level(self):
        for purchase in self:
            purchase.transport_packaging_level_id = (
                self.env.company.purchase_packaging_level_id
            )

    @api.depends(
        "order_line.transport_qty",
        "order_line.product_qty",
        "transport_packaging_level_id",
    )
    def _compute_total_transport_packaging_qty(self):
        for order in self:
            if order.transport_packaging_level_id:
                order.total_transport_qty = sum(
                    order.mapped("order_line.transport_qty")
                )
            else:
                order.total_transport_qty = False

    @api.depends("total_transport_qty", "transport_packaging_level_id")
    def _compute_transport_packaging_level_total_qty(self):
        for order in self:
            if order.transport_packaging_level_id:
                order.transport_packaging_level_total_qty = "{} {}".format(
                    order.total_transport_qty,
                    order.transport_packaging_level_id.name or "",
                ).strip()
            else:
                order.total_transport_qty = False
