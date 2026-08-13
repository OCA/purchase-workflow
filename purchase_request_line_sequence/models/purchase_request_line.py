# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"
    _order = "sequence, id"

    sequence = fields.Integer(
        default=10,
        index=True,
        help="Order of the line inside the request. Drag the handle in the "
        "list to change it.",
    )
    line_number = fields.Integer(
        string="#",
        compute="_compute_line_number",
        help="Position of the line in the request, recomputed on the fly. It "
        "is a display aid, not a stable identifier: removing a line "
        "renumbers the ones below it.",
    )

    @api.depends("request_id", "request_id.line_ids", "sequence")
    def _compute_line_number(self):
        numbers = {}
        for request in self.request_id:
            for position, line in enumerate(request.line_ids, start=1):
                numbers[line.id] = position
        for line in self:
            line.line_number = numbers.get(line.id, 0)
