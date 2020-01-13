# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    secondary_uom_qty = fields.Float(
        string="Secondary Qty", digits="Product Unit of Measure"
    )
    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        string="Secondary uom",
        ondelete="restrict",
    )

    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def _onchange_secondary_uom(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.product_qty, qty, precision_rounding=self.product_uom.rounding
            )
            != 0
        ):
            self.product_qty = qty

    @api.onchange("product_qty")
    def _onchange_product_qty_purchase_order_secondary_unit(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_uom.factor
        qty = float_round(
            self.product_qty / (factor or 1.0),
            precision_rounding=self.secondary_uom_id.uom_id.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.secondary_uom_id.uom_id.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty

    @api.onchange("product_uom")
    def _onchange_product_uom_purchase_order_secondary_unit(self):
        if not self.secondary_uom_id:
            return
        factor = self.product_uom.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.product_qty / (factor or 1.0),
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.product_uom.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty

    @api.onchange("product_id")
    def _onchange_product_id_purchase_order_secondary_unit(self):
        self.secondary_uom_id = self.product_id.purchase_secondary_uom_id
