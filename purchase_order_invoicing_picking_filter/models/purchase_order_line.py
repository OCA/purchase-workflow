from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_invoice_line(self, move, **optional_values):
        self.ensure_one()
        qty = move.product_uom._compute_quantity(move.quantity_done, self.product_uom)
        res = {
            "display_type": "product",
            "sequence": self.sequence,
            "name": self.name,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": qty,
            "discount": self.discount,
            "price_unit": self.price_unit,
            "purchase_line_id": self.id,
            "move_line_ids": [move.id],
        }
        if optional_values:
            res.update(optional_values)
        return res
