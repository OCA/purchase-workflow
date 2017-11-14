# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseExceptionConfirm(models.TransientModel):
    _inherit = 'purchase.exception.confirm'

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore and self.related_model_id.approval_block_id:
            self.related_model_id.button_release_approval_block()
        return super(PurchaseExceptionConfirm, self).action_confirm()
