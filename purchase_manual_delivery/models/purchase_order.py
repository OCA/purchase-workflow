# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    pending_to_receive = fields.Boolean(compute="_compute_pending_to_receive")
    manual_delivery = fields.Boolean(
        string="Manual delivery",
        compute="_compute_manual_delivery",
        help=(
            "Stock transfers need to be created manually to receive this PO's products"
        ),
        readonly=False,
        store=True,
    )

    @api.depends("company_id")
    def _compute_manual_delivery(self):
        """The manual delivery option is derived from the company of the order"""
        for po in self:
            po.manual_delivery = po.company_id.purchase_manual_delivery

    def _compute_pending_to_receive(self):
        for order in self:
            order.pending_to_receive = True
            if not any(order.mapped("order_line.pending_to_receive")):
                order.pending_to_receive = False

    def button_confirm_manual(self):
        return super(
            PurchaseOrder, self.with_context(manual_delivery=True)
        ).button_confirm()

    def button_approve(self, force=False):
        if self.manual_delivery:
            self = self.with_context(manual_delivery=True)
        return super().button_approve(force=force)

    def _create_picking(self):
        if self.env.context.get("manual_delivery", False) and self.manual_delivery:
            # We do not want to create the picking when confirming the order
            # if it comes from manual confirmation
            return
        return super()._create_picking()
