# Copyright 2015 FactorLibre - Hugo Santos
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from math import ceil

from odoo import _, api, models
from openerp.tools import frozendict


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_product_id(self):
        # Change context in a compatible way with onchange usage
        # See : https://github.com/odoo/odoo/issues/7472#issuecomment-119503916
        self.env.context = frozendict(self.env.context, multiplier_qty_message=False)
        res = super().onchange_product_id()
        self.env.context = frozendict(self.env.context, multiplier_qty_message=True)
        return res

    @api.onchange("product_qty")
    def _onchange_quantity(self):
        if not self.product_id:
            return super()._onchange_quantity()
        params = {"order_id": self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params,
        )
        qty = self.product_qty
        if seller and seller.multiplier_qty and qty % seller.multiplier_qty:
            self.product_qty = ceil(qty / seller.multiplier_qty) * seller.multiplier_qty
            if self.env.context.get("multiplier_qty_message", True):
                warn_msg = _(
                    "The selected supplier only sells this product by %s %s.\n"
                    "The quantity has been automatically changed to %s %s"
                ) % (
                    seller.multiplier_qty,
                    seller.product_uom.name,
                    self.product_qty,
                    seller.product_uom.name,
                )
                self.env.user.notify_warning(title=_("Warning"), message=warn_msg)
        return super()._onchange_quantity()
