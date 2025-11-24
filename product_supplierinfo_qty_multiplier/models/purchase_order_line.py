# Copyright 2015 FactorLibre - Hugo Santos
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from math import ceil

from odoo import _, api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_qty")
    def _onchange_product_qty_multiplier_qty(self):
        if not self.product_id:
            return
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params={"order_id": self.order_id},
        )
        qty = self.product_qty
        if seller and seller.multiplier_qty and qty % seller.multiplier_qty:
            # Change Ordered Quantity
            self.product_qty = ceil(qty / seller.multiplier_qty) * seller.multiplier_qty
            self.env.user.notify_warning(
                title=_("Warning"),
                message=_(
                    "The selected supplier only sells this product"
                    " by %(multiplier_qty)s %(uom_name)s.\n"
                    "The quantity has been automatically changed"
                    " to %(new_product_qty)s %(uom_name)s."
                )
                % (
                    {
                        "multiplier_qty": seller.multiplier_qty,
                        "uom_name": seller.product_uom.name,
                        "new_product_qty": self.product_qty,
                    }
                ),
            )
        return
