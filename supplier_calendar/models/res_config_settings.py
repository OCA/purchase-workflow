# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    supplier_calendar_id = fields.Many2one(
        related="company_id.supplier_calendar_id", readonly=False
    )
    supplier_calendar_natural_count = fields.Integer(
        compute="_compute_supplier_calendar_natural_count"
    )

    def _get_natural_vendors_domain(self):
        return [("supplier_rank", ">", 0), ("delay_calendar_type", "=", "natural")]

    @api.depends("supplier_calendar_id")
    def _compute_supplier_calendar_natural_count(self):
        count = self.env["res.partner"].search_count(self._get_natural_vendors_domain())
        for rec in self:
            rec.supplier_calendar_natural_count = count

    def action_set_vendors_default_supplier_calendar(self):
        self.env["res.partner"].search(self._get_natural_vendors_domain()).write(
            {"delay_calendar_type": "company_calendar"}
        )
        return {"type": "ir.actions.client", "tag": "reload"}
