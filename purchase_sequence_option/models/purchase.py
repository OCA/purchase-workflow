# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        seq = self.env["sequence.option"].get_sequence(self.new(vals))
        self = self.with_context(sequence_option_id=seq.id)
        res = super().create(vals)
        return res
