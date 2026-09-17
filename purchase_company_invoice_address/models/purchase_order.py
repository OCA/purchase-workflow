# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

READONLY_STATES = {
    "purchase": [("readonly", True)],
    "done": [("readonly", True)],
    "cancel": [("readonly", True)],
}


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    company_partner_id = fields.Many2one(related="company_id.partner_id")
    company_invoice_address_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_company_invoice_address_id",
        store=True,
        readonly=False,
        precompute=True,
        states=READONLY_STATES,
        domain="['|', ('id', '=', company_partner_id), '&',"
        " ('id', 'child_of', company_partner_id), ('type', '=', 'invoice')]",
        help="Address of your own company to which the vendor should send the invoice.",
    )

    @api.depends("company_id")
    def _compute_company_invoice_address_id(self):
        for order in self:
            partner = order.company_id.partner_id
            order.company_invoice_address_id = (
                partner.address_get(["invoice"])["invoice"] if partner else False
            )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals["company_invoice_address_id"] = self.company_invoice_address_id.id
        return invoice_vals
