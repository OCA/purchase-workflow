# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PurchaseExceptionConfirm(models.TransientModel):
    _inherit = "purchase.exception.confirm"

    def action_confirm(self):
        self.ensure_one()
        if self.ignore and self.related_model_id.approval_block_id:
            self.related_model_id.button_release_approval_block()
        return super(PurchaseExceptionConfirm, self).action_confirm()
