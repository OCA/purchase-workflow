# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_promotion = fields.Boolean(
        string="Promotion",
        compute="_compute_is_promotion",
        store=True,
        readonly=False,
        help="Price was calculated based on a vendor promotion.",
    )

    @api.depends("product_id", "product_qty", "product_uom")
    def _compute_is_promotion(self):
        for line in self:
            if not line.product_id:
                line.is_promotion = False
                continue
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                and line.order_id.date_order.date()
                or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params={"order_id": line.order_id},
            )
            line.is_promotion = seller.is_promotion if seller else False

    @api.onchange("price_unit")
    def _set_is_promotion(self):
        """Reset the promotion flag when the price is manually set."""
        # Skip it on new lines (no _origin yet)
        if self._origin:
            self.is_promotion = False
