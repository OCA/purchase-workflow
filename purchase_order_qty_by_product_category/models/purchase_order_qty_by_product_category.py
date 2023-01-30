# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderQtyByProductCategory(models.Model):
    _name = "purchase.order.qty.by.product.category"
    _description = "PO quantities split by product category"

    purchase_order_id = fields.Many2one(
        "purchase.order", required=True, ondelete="cascade"
    )
    purchase_line_ids = fields.One2many(
        "purchase.order.line", "qty_by_product_category_id"
    )
    category_id = fields.Many2one("product.category", required=True, ondelete="cascade")
    qty_ordered = fields.Float(
        digits="Product Unit of Measure", compute="_compute_quantities", store=True
    )
    qty_received = fields.Float(
        digits="Product Unit of Measure", compute="_compute_quantities", store=True
    )
    qty_to_receive = fields.Float(
        digits="Product Unit of Measure", compute="_compute_quantities", store=True
    )
    qty_uom_id = fields.Many2one("uom.uom")

    @api.constrains("purchase_order_id", "category_id", "qty_uom_id")
    def _check_unicity(self):
        for rec in self:
            if (
                self.search_count(
                    [
                        ("purchase_order_id", "=", rec.purchase_order_id.id),
                        ("category_id", "=", rec.category_id.id),
                        ("qty_uom_id", "=", rec.qty_uom_id.id),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    _(
                        "Qty group for order '%(order)s', category '%(categ)s'"
                        " and UoM '%(uom)s' already exists"
                    )
                    % {
                        "order": rec.purchase_order_id.name,
                        "categ": rec.category_id.name,
                        "uom": rec.qty_uom_id.name or _("undefined"),
                    }
                )

    @api.depends(
        "purchase_line_ids.product_qty",
        "purchase_line_ids.qty_received",
        "purchase_line_ids.product_uom",
    )
    def _compute_quantities(self):
        for rec in self:
            ordered, received = 0, 0
            for po_line in rec.purchase_line_ids:
                if isinstance(po_line.id, models.NewId):
                    continue  # Skip lines while creating them
                elif rec.qty_uom_id:
                    ordered += po_line.product_uom._compute_quantity(
                        po_line.product_qty, rec.qty_uom_id, round=False
                    )
                    received += po_line.product_uom._compute_quantity(
                        po_line.qty_received, rec.qty_uom_id, round=False
                    )
                else:
                    ordered += po_line.product_qty
                    received += po_line.qty_received
            rec.update(
                {
                    "qty_ordered": ordered,
                    "qty_received": received,
                    "qty_to_receive": ordered - received,
                }
            )
