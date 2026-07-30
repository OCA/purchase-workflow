# Copyright (C) 2026  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    effective_date = fields.Datetime(
        compute="_compute_effective_dates",
        store=True,
        compute_sudo=True,
        help="Completion date of the first receipt order.",
    )

    last_effective_date = fields.Datetime(
        compute="_compute_effective_dates",
        store=True,
        compute_sudo=True,
        help="Completion date of the last receipt order.",
    )

    @api.depends("move_ids.date")
    def _compute_effective_dates(self):
        for line in self:
            moves = line.move_ids.filtered_domain(
                [
                    ("state", "=", "done"),
                    ("location_id.usage", "=", "supplier"),
                    ("date", "!=", False),
                ]
            ).sorted("date", reverse=False)
            line.effective_date = moves[:1].date
            line.last_effective_date = moves[-1:].date
