from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    price_unit_hide = fields.Float(
        string="U. Price", digits="Product Price", compute="_compute_hidden_prices"
    )
    price_subtotal_hide = fields.Monetary(
        compute="_compute_hidden_prices", string="Subtotal."
    )
    price_total_hide = fields.Monetary(
        compute="_compute_hidden_prices", string="Total."
    )

    def _compute_hidden_prices(self):
        for rec in self:
            if rec.order_id.hide_price:
                rec.price_unit_hide = 0.0
                rec.price_total_hide = 0.0
                rec.price_subtotal_hide = 0.0
            else:
                rec.price_unit_hide = rec.price_unit
                rec.price_total_hide = rec.price_total
                rec.price_subtotal_hide = rec.price_subtotal
