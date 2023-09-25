# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def copy(self, default=None):
        self.ensure_one()
        seq = self.env["ir.sequence.option.line"].get_sequence(self)
        self = self.with_context(sequence_option_id=seq.id)
        return super().copy(default)

    @api.model
    def create(self, vals):
        seq = self.env["ir.sequence.option.line"].get_sequence(self.new(vals))
        self = self.with_context(sequence_option_id=seq.id)
        return super().create(vals)