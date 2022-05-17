from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("move_ids.state", "move_ids.product_uom_qty", "move_ids.product_uom")
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self.filtered(lambda l: l.qty_received and l._has_components()):
            # update product components qty
            line.component_ids._update_qty(line.qty_received - line.last_qty_invoiced)
