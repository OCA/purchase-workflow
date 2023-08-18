# Copyright 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    line_weight = fields.Float(
        "Weight", compute="_compute_line_physical_properties", digits="Stock Weight"
    )
    line_volume = fields.Float(
        "Volume", compute="_compute_line_physical_properties", digits="Volume"
    )

    @api.depends("product_uom_qty", "product_id")
    def _compute_line_physical_properties(self):
        for line in self:
            line.line_weight = line.product_id.weight * line.product_uom_qty
            line.line_volume = line.product_id.volume * line.product_uom_qty


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_weight = fields.Float(
        compute="_compute_total_physical_properties",
        digits="Stock Weight",
    )
    total_volume = fields.Float(
        compute="_compute_total_physical_properties", digits="Volume"
    )
    weight_uom_name = fields.Char(compute="_compute_total_physical_properties")
    volume_uom_name = fields.Char(compute="_compute_total_physical_properties")
    display_total_weight_in_report = fields.Boolean(
        "Display Weight in Report", default=True
    )
    display_total_volume_in_report = fields.Boolean(
        "Display Volume in Report", default=True
    )

    @api.depends("order_line.product_uom_qty", "order_line.product_id")
    def _compute_total_physical_properties(self):
        for po in self:
            po.total_weight = 0
            po.total_volume = 0
            po.weight_uom_name = ""
            po.volume_uom_name = ""

            if po.company_id.display_order_weight_in_po:
                weight_uoms = po.mapped("order_line.product_id.weight_uom_name")
                # values are computed only if all products in PO have same UOMs.
                if len(weight_uoms) > 0:
                    same_weight_uom = all(el == weight_uoms[0] for el in weight_uoms)
                    if same_weight_uom:
                        po.total_weight = sum(po.mapped("order_line.line_weight"))
                        po.weight_uom_name = weight_uoms[0]

            if po.company_id.display_order_volume_in_po:
                volume_uoms = po.mapped("order_line.product_id.volume_uom_name")
                if len(volume_uoms) > 0:
                    same_volume_uom = all(el == volume_uoms[0] for el in volume_uoms)
                    if same_volume_uom:
                        po.total_volume = sum(po.mapped("order_line.line_volume"))
                        po.volume_uom_name = volume_uoms[0]
