# Copyright 2023 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from odoo.addons.purchase.models.purchase import PurchaseOrder


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    owner_id = fields.Many2one(
        "res.partner",
        "Assign Owner",
        states=PurchaseOrder.READONLY_STATES,
        check_company=True,
        help="The assigned value will be set on the corresponding field of the "
        "incoming stock picking.",
    )

    def button_confirm(self):
        """For subcontracting orders
        Without this, the downstream component demands may misjudge the available
        quantities with owner consideration.
        """
        # TODO: Double-check if the logic is optimal
        for order in self:
            order = order.with_context(owner_id=order.owner_id.id)
            super(PurchaseOrder, order).button_confirm()
        return True

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res["owner_id"] = self.owner_id.id
        return res
