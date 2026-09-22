# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    company_partner_id = fields.Many2one(related="company_id.partner_id")
    company_invoice_address_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_company_invoice_address_id",
        store=True,
        readonly=False,
        precompute=True,
        domain="['|', ('id', '=', company_partner_id), '&',"
        " ('id', 'child_of', company_partner_id), ('type', '=', 'invoice')]",
        help="Address of your own company to which the vendor should send the invoice.",
    )

    @api.depends("company_id", "move_type")
    def _compute_company_invoice_address_id(self):
        for move in self:
            partner = move.company_id.partner_id
            if not move.is_purchase_document(include_receipts=True) or not partner:
                move.company_invoice_address_id = False
                continue
            move.company_invoice_address_id = partner.address_get(["invoice"])[
                "invoice"
            ]
