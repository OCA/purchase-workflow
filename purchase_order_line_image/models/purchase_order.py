from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def check_show_product_image_in_purchase_report(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "purchase_order_line_image.show_product_image_in_purchase_report", False
            )
        )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_image_1920 = fields.Binary("Product Image", related="product_id.image_1920")
