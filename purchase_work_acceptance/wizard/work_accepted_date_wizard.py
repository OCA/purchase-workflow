# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SelectWorkAcceptanceWizard(models.TransientModel):
    _name = "work.accepted.date.wizard"
    _description = "Select work accepted date"

    date_accept = fields.Datetime(
        string="Accepted Date",
        required=True,
    )

    def button_accept(self):
        active_id = self.env.context.get("active_id")
        work_acceptance = self.env["work.acceptance"].browse(active_id)
        work_acceptance.with_context(manual_date_accept=False).button_accept(
            force=self.date_accept
        )
