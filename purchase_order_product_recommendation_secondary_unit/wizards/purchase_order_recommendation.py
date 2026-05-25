# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import ceil

from odoo import api, fields, models


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
    _inherit = ["purchase.order.recommendation.line", "product.secondary.unit.mixin"]
    _name = "purchase.order.recommendation.line"
    _secondary_unit_fields = {
        "qty_field": "units_included",
        "uom_field": "product_uom_id",
    }
    _product_uom_field = "uom_po_id"

    units_included = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_units_included",
        copy=True,
        precompute=True,
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_units_included(self):
        self._compute_helper_target_field_qty()

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
