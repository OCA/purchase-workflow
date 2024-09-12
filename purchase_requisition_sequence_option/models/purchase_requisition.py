# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def action_in_progress(self):
        self.ensure_one()
        seq = self.env["ir.sequence.option.line"].get_sequence(self)
        self = self.with_context(sequence_option_id=seq.id)
        return super().action_in_progress()
