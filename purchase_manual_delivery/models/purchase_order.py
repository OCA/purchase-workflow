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
        """An order is 'pending to receive' if any of its lines is"""
        for order in self:
            order.pending_to_receive = any(
                order.order_line.mapped("pending_to_receive")
            )

    def _create_picking(self):
        # Avoid creating deliveries on manual delivery orders
        if self.env.context.get("ignore_manual_delivery"):
            orders = self
        else:
            orders = self.filtered(lambda po: not po.manual_delivery)
        return super(PurchaseOrder, orders)._create_picking()
