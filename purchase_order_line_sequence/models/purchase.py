# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in purchase order lines.
        Then we add 1 to this value for the next sequence which is given
        to the context of the o2m field in the view. So when we create a new
        purchase order line, the sequence is automatically max_sequence + 1
        """
        for purchase in self:
            purchase.max_line_sequence = (
                max(purchase.mapped("order_line.sequence") or [0]) + 1
            )

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence"
    )

    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()
        self._update_moves_sequence()
        return res

    def _update_moves_sequence(self):
        for order in self:
            if any(
                [
                    ptype in ["product", "consu"]
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                pickings = order.picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )
                if pickings:
                    picking = pickings[0]
                    order_lines = order.order_line.filtered(
                        lambda l: l.product_id.type in ["product", "consu"]
                    )
                    for move, line in zip(
                        sorted(picking.move_lines, key=lambda m: m.id), order_lines
                    ):
                        move.write({"sequence": line.sequence})

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        self._reset_sequence()
        if "order_line" in line_values:
            self._update_moves_sequence()
        return res

    def copy(self, default=None):
        return super(PurchaseOrder, self.with_context(keep_line_sequence=True)).copy(
            default
        )

    def action_create_invoice(self):

        res = super(PurchaseOrder, self).action_create_invoice()

        if res["res_id"]:
            invoice = self.env["account.move"].browse(res["res_id"])
        else:
            invoice = self.env["account.move"].search(res["domain"])

        for inv in invoice:
            for line in inv.line_ids:
                line.sequence = line.purchase_line_id.sequence
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _order = "sequence, id"

    sequence = fields.Integer(
        "Hidden Sequence",
        help="Gives the sequence of the line when " "displaying the purchase order.",
        default=9999,
    )

    sequence2 = fields.Integer(
        "Sequence",
        help="Displays the sequence of the line in " "the purchase order.",
        related="sequence",
        readonly=True,
    )

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for move, line in zip(res, self):
            move.update(sequence=line.sequence)
        return res

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        # We do not reset the sequence when copying an entire purchase order
        if not self.env.context.get("keep_line_sequence"):
            line.order_id._reset_sequence()
        return line
