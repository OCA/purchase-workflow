# Copyright 2018 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, exceptions, fields, models


class PurchaseOrderLineReassignWiz(models.TransientModel):
    _name = "purchase.order.line.reassign.wiz"
    _description = "Wizard to reassign purchase order lines to other PO"

    def _default_partner_id(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["purchase.order.line"].browse(active_ids)
        partner = lines[:1].order_id.partner_id
        if lines.filtered(lambda l: (l.invoice_lines or l.partner_id != partner)):
            raise exceptions.ValidationError(
                _("Selected line/s are invoiced or they have distinct vendors")
            )
        return partner

    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Move to purchase",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        default=lambda self: self._default_partner_id(),
    )
    allow_different_suppliers = fields.Boolean(
        help="Allow selecting orders from other suppliers."
    )

    def action_apply(self):
        active_ids = self.env.context.get("active_ids")
        lines = self.env["purchase.order.line"].browse(active_ids)
        lines.write({"order_id": self.purchase_order_id.id})
        return lines
