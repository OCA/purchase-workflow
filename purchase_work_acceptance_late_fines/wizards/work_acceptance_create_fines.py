# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkAcceptanceCreateFine(models.TransientModel):
    _name = "work.acceptance.create.fines"
    _description = "Create Fines Invoice/Refund from WA"

    move_type = fields.Selection(
        selection=[
            ("out_invoice", "Customer Invoice"),
            ("in_refund", "Vendor Refund"),
        ],
        string="Type",
        required=True,
        default="out_invoice",
    )

    def action_create_fines(self):
        active_ids = self.env.context.get("active_ids", [])
        work_acceptances = self.env["work.acceptance"].browse(active_ids)
        return work_acceptances.action_create_fines_invoice(move_type=self.move_type)
