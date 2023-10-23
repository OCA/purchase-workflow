# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from collections import defaultdict

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_ordered_qty_json = fields.Char(
        string="Total Quantity Json",
        compute="_compute_total_ordered_qty_json",
        store=True,  # Used by ``total_ordered_qty_text``, store it for better performances
    )
    total_ordered_qty_text = fields.Text(
        string="Total Quantity Text",
        compute="_compute_total_ordered_qty_text",
        store=False,  # Depends on ctx/user lang
    )

    @api.depends("order_line.product_qty", "order_line.product_uom")
    def _compute_total_ordered_qty_json(self):
        # Map UoMs to their reference
        ref_uom = defaultdict(lambda: self.env["uom.uom"])
        with_lines = self.filtered("order_line")
        (self - with_lines).total_ordered_qty_json = json.dumps({})
        for order in with_lines:
            ordered_qty_by_uom = defaultdict(float)
            for line in order.order_line:
                qty = line.product_qty
                uom = line.product_uom
                if uom.uom_type == "reference":
                    ref = uom
                elif uom in ref_uom:
                    ref = ref_uom[uom]
                else:
                    ref = self.env["uom.uom"].search(
                        [
                            ("category_id", "=", uom.category_id.id),
                            ("uom_type", "=", "reference"),
                        ],
                        limit=1,
                    )
                    ref_uom[uom] = ref
                ordered_qty_by_uom[ref] += uom._compute_quantity(qty, ref, round=False)
            order.total_ordered_qty_json = json.dumps(
                {u.id: q for u, q in ordered_qty_by_uom.items()}
            )

    @api.depends("total_ordered_qty_json")
    @api.depends_context("lang")
    def _compute_total_ordered_qty_text(self):
        lang = self.env.context.get("lang") or self.env.user.lang
        uom_browse = self.env["uom.uom"].with_context(lang=lang).browse
        for order in self:
            ordered_qty_dict = {
                uom_browse(int(u_id)): qty
                for u_id, qty in json.loads(order.total_ordered_qty_json).items()
            }
            order.total_ordered_qty_text = "\n".join(
                "%s %s" % (u._compute_quantity(q, u, round=True), u.name)
                for u, q in sorted(ordered_qty_dict.items(), key=lambda x: x[0].name)
            )
