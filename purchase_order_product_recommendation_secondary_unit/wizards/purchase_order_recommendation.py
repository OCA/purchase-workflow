# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import ceil

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    @api.model
    def _prepare_wizard_line(self, vals, order_line=False):
        res = super()._prepare_wizard_line(vals, order_line)
        secondary_uom_id = (
            order_line
            and order_line.secondary_uom_id
            or vals.get("product_id")
            and vals["product_id"].purchase_secondary_uom_id
        )
        secondary_uom_qty = False
        if not order_line and secondary_uom_id:
            secondary_uom_qty = ceil(
                res.get("units_included", 0) / secondary_uom_id.factor
            )
            res["units_included"] = secondary_uom_qty * secondary_uom_id.factor
        res.update(
            {
                "secondary_uom_id": secondary_uom_id and secondary_uom_id.id,
                "secondary_uom_qty": (
                    order_line and order_line.secondary_uom_qty or secondary_uom_qty
                ),
            }
        )
        return res


class PurchaseOrderRecommendationLine(models.TransientModel):
    _inherit = "purchase.order.recommendation.line"

    secondary_uom_id = fields.Many2one(
        comodel_name="product.secondary.unit",
        related="product_id.purchase_secondary_uom_id",
        readonly=True,
    )
    secondary_uom_qty = fields.Float(
        string="Secondary Qty",
        digits="Product Unit of Measure",
    )

    @api.onchange("secondary_uom_id", "secondary_uom_qty")
    def _onchange_secondary_uom(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_id.uom_id.factor
        qty = float_round(
            self.secondary_uom_qty * factor,
            precision_rounding=self.product_id.uom_id.rounding,
        )
        if (
            float_compare(
                self.units_included,
                qty,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            != 0
        ):
            self.units_included = qty

    @api.onchange("units_included")
    def _onchange_units_included_purchase_order_secondary_unit(self):
        if not self.secondary_uom_id:
            return
        factor = self.secondary_uom_id.factor * self.product_id.uom_id.factor
        qty = float_round(
            self.units_included / (factor or 1.0),
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

    def _prepare_update_po_line(self):
        res = super()._prepare_update_po_line()
        if self.secondary_uom_id and self.secondary_uom_qty:
            res.update(
                {
                    "secondary_uom_id": self.secondary_uom_id.id,
                    "secondary_uom_qty": self.secondary_uom_qty,
                }
            )
        return res

    def _prepare_new_po_line(self, sequence):
        res = super()._prepare_new_po_line(sequence)
        if self.secondary_uom_id and self.secondary_uom_qty:
            res.update(
                {
                    "secondary_uom_id": self.secondary_uom_id.id,
                    "secondary_uom_qty": self.secondary_uom_qty,
                }
            )
        return res
