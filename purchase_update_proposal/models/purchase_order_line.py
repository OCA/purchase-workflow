# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    proposal_count = fields.Integer(related="order_id.proposal_count", store=False)
    supplier_cancel_status = fields.Char(
        string="Status",
        compute="_compute_supplier_cancel_status",
        help="Indicate if the line is cancelled",
    )
    received = fields.Selection(
        selection=[("", "No"), ("partially", "Partially"), ("all", "All")],
        compute="_compute_received",
        compute_sudo=True,
        store=False,
        help="Defined if quantity is partially or "
        "completely received (at least the quantity of the line)",
    )

    def _compute_received(self):
        for rec in self:
            received = sum(
                rec.move_ids.filtered(lambda s: s.state == "done").mapped(
                    "product_uom_qty"
                )
            )
            if received >= rec.product_qty:
                rec.received = "all"
            elif not received:
                rec.received = ""
            else:
                rec.received = "partially"

    @api.multi
    def _compute_supplier_cancel_status(self):
        for rec in self:
            if rec.state == "cancel":
                rec.supplier_cancel_status = _("Cancel")

    @api.multi
    def button_update_proposal(self):
        order_ids = [x.order_id for x in self]
        if len(set(order_ids)) > 1:
            raise UserError(_("You shouldn't update proposal on multiple orders"))
        for rec in self:
            vals = {
                "qty": rec.product_qty,
                "line_id": rec.id,
                "order_id": rec.order_id.id,
            }
            # We only want create proposal line from purchase line
            self.env["purchase.line.proposal"].sudo().create(vals)
        if not self:
            return
        order = self[0].order_id
        order.write({"proposal_state": "draft"})
        action = {
            "res_model": "purchase.order",
            "res_id": order.id,
            "view_mode": "form",
            "target": "current",
            "type": "ir.actions.act_window",
        }
        if "supplier_view" in self.env.context:
            # This view is dedicated to the supplier
            action["view_id"] = self.env.ref(
                "purchase_update_proposal.supplier_purchase_order_form"
            ).id
        else:
            action["view_id"] = self.env.ref("purchase.purchase_order_form").id
        return action

    @api.multi
    def button_supplier_update_proposal(self):
        """Call button_update_proposal() but from the view supplier_purchase_order_form
        We can't pass the context from the view because
        the button is linked to the tree view of order_line
        """
        self.ensure_one()
        return self.with_context(supplier_view=True).button_update_proposal()
