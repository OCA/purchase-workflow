# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models

from .res_company import SORTING_DIRECTION


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    line_order = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'purchase.order.line')]",
        default=lambda self: self.env.user.company_id.default_po_line_order,
    )
    line_order_2 = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sort Lines By",
        domain="[('model', '=', 'purchase.order.line')]",
        default=lambda self: self.env.user.company_id.default_po_line_order_2,
    )
    line_direction = fields.Selection(
        selection=SORTING_DIRECTION,
        string="Sort Direction",
        default=lambda self: self.env.user.company_id.default_po_line_direction,
    )

    @api.onchange("line_order", "line_order_2")
    def onchange_line_order(self):
        if not self.line_order and not self.line_order_2:
            self.line_direction = False

    def _sort_purchase_line(self):
        def resolve_subfields(obj, line_order):
            if not line_order:
                return None
            val = getattr(obj, line_order.name)
            # Odoo object
            if isinstance(val, models.BaseModel):
                if hasattr(val[0], "name"):
                    val = ",".join(val.mapped("name"))
                else:
                    val = ",".join([str(id) for id in val.mapped("id")])
            return val

        if not self.line_order and not self.line_order_2 and not self.line_direction:
            return
        reverse = self.line_direction == "desc"
        sequence = 0
        sorted_lines = self.order_line.sorted(
            key=lambda p: (
                resolve_subfields(p, self.line_order),
                resolve_subfields(p, self.line_order_2),
            ),
            reverse=reverse,
        )
        for line in sorted_lines:
            sequence += 10
            if line.sequence == sequence:
                continue
            line.sequence = sequence

    def write(self, values):
        res = super().write(values)
        if (
            "order_line" in values
            or "line_order" in values
            or "line_order_2" in values
            or "line_direction" in values
        ):
            self._sort_purchase_line()
        return res

    @api.model
    def create(self, values):
        purchase = super().create(values)
        purchase._sort_purchase_line()
        return purchase


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line.order_id._sort_purchase_line()
        return line
