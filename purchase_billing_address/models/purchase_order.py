# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    available_partner_invoice_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Allowed invoice addresses",
        compute="_compute_available_partner_invoice_ids",
    )

    partner_invoice_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice address",
        help="Invoice address for this purchase order",
        domain="[('id', 'in', available_partner_invoice_ids)]",
    )

    def _address_purchase_invoice_get(self):
        child_ids = self.partner_id.child_ids
        partner_invoice_ids = child_ids.filtered(
            lambda child: child.type == "purchase_invoice"
        )
        if not partner_invoice_ids:
            partner_invoice_ids = child_ids.child_ids.filtered(
                lambda child: child.type == "purchase_invoice"
            )
        return partner_invoice_ids.ids

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        result = super().onchange_partner_id()
        for order in self:
            purchase_invoice_address = order._address_purchase_invoice_get()
            order.partner_invoice_id = (
                purchase_invoice_address[0]
                if purchase_invoice_address
                else order.partner_id.id
            )
        return result

    @api.depends("partner_id")
    def _compute_available_partner_invoice_ids(self):
        for order in self:
            order.available_partner_invoice_ids = [
                Command.set(order._address_purchase_invoice_get())
            ]

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.partner_invoice_id:
            res["partner_id"] = self.partner_invoice_id.id
        return res
