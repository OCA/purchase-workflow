# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_by_product_category_id = fields.Many2one(
        "purchase.order.qty.by.product.category",
        compute="_compute_qty_by_product_category_id",
        store=True,
        string="Order Line Qty By Category",
    )

    def unlink(self):
        recs = self.qty_by_product_category_id
        res = super().unlink()
        recs.filtered(lambda r: not r.purchase_line_ids).unlink()
        return res

    @api.depends(
        "order_id.category_qty_split_by_uom",
        "order_id.category_qty_split_by_uom_reference",
        "product_id",
        "product_uom",
        "product_qty",
        "qty_received",
    )
    def _compute_qty_by_product_category_id(self):
        old_recs = self.qty_by_product_category_id
        data = defaultdict(lambda: self.browse())
        uom_reference_ids = {
            u.category_id.id: u.id
            for u in self.env["uom.uom"].search([("uom_type", "=", "reference")])
        }
        for line in self:
            if isinstance(line.id, models.NewId) or not (
                line.order_id._origin and line.product_id
            ):
                # Skip lines while creating or updating them, recompute field only after saving
                line.qty_by_product_category_id = False
                continue
            uom_id = False
            if line.product_uom and line.order_id.category_qty_split_by_uom:
                if line.order_id.category_qty_split_by_uom_reference:
                    uom_id = uom_reference_ids[line.product_uom.category_id.id]
                else:
                    uom_id = line.product_uom.id
            data[
                (line.order_id._origin.id, line.product_id.categ_id.id, uom_id)
            ] += line
        rec_obj = self.env["purchase.order.qty.by.product.category"]
        for (order_id, categ_id, uom_id), lines in data.items():
            rec = rec_obj.search(
                [
                    ("purchase_order_id", "=", order_id),
                    ("category_id", "=", categ_id),
                    ("qty_uom_id", "=", uom_id),
                ],
                limit=1,
            )
            if not rec:
                rec = rec_obj.create(
                    {
                        "purchase_order_id": order_id,
                        "category_id": categ_id,
                        "qty_uom_id": uom_id,
                    }
                )
            lines.qty_by_product_category_id = rec
        old_recs.filtered(lambda r: not r.purchase_line_ids).unlink()
