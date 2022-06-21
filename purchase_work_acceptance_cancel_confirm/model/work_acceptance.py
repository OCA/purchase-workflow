# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class WorkAcceptance(models.Model):
    _name = "work.acceptance"
    _inherit = ["work.acceptance", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    def button_draft(self):
        self.clear_cancel_confirm_data()
        return super().button_draft()

    def button_cancel(self):
        if not self.filtered("cancel_confirm"):
            return self.open_cancel_confirm_wizard()
        return super().button_cancel()
