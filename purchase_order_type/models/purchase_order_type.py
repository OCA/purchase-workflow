# Copyright (C) 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Type of purchase order"
    _order = "sequence"

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return [
            ("code", "=", seq_type.code),
            ("company_id", "in", [False, self.env.company.id]),
        ]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return seq_type.id

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=lambda self: self._get_domain_sequence_id(),
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Payment Terms"
    )
    incoterm_id = fields.Many2one(comodel_name="account.incoterms", string="Incoterm")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    is_default = fields.Boolean(
        string="Default",
        help="Used as the fallback order type for a purchase order whose "
        "vendor does not provide one, and to correct a purchase order "
        "whose type no longer suits its company after the company "
        "changes.",
    )

    @api.constrains("is_default", "company_id")
    def _check_is_default_unique(self):
        for record in self.filtered("is_default"):
            other_count = self.search_count(
                [
                    ("is_default", "=", True),
                    ("company_id", "=", record.company_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if other_count:
                raise ValidationError(
                    _("Only one default order type is allowed per company.")
                )
