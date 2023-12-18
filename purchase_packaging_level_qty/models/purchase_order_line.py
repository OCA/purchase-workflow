from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    transport_qty = fields.Float(
        compute="_compute_line_transport_qty",
        digits="Product Unit of Measure",
    )

    def _get_transport_packaging_qty(self):
        self.ensure_one()
        transport_packaging_level = self.order_id.transport_packaging_level_id
        product_packaging = self.product_id.packaging_ids.filtered(
            lambda self: self.packaging_level_id == transport_packaging_level
        )
        if product_packaging:
            return max(product_packaging.mapped("qty"))
        return 0.0

    @api.depends(
        "order_id.transport_packaging_level_id",
        "product_uom_qty",
    )
    def _compute_line_transport_qty(self):
        for line in self:
            line_packaging_qty = 0.0
            transport_packaging_qty = line._get_transport_packaging_qty()
            if (
                line.order_id.transport_packaging_level_id
                and transport_packaging_qty > 0
            ):
                line_packaging_qty = line.product_uom_qty / transport_packaging_qty
            line.transport_qty = line_packaging_qty
