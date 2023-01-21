from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _write(self, vals):
        result = super()._write(vals)
        if "qty_received" in vals:
            # Update Total Quantity
            for rec in self.filtered(lambda l: l.qty_received and l._has_components()):
                rec.component_ids._update_qty(rec.qty_received - rec.last_qty_invoiced)
        return result
