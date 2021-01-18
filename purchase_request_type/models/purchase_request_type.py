# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequestType(models.Model):
    _name = "purchase.request.type"
    _description = "Type of purchase request"
    _order = "sequence"

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("purchase_request.seq_purchase_request")
        return [
            ("code", "=", seq_type.code),
            ("company_id", "in", [False, self.env.company.id]),
        ]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref("purchase_request.seq_purchase_request")
        return seq_type.id

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description", translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Entry Sequence",
        copy=False,
        domain=lambda self: self._get_domain_sequence_id(),
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Picking Type"
    )
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    reduce_step = fields.Boolean(string="Reduce Step", default=False)
