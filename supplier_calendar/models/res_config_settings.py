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
        """Vendors of the configured company, or shared, still in natural days."""
        self.ensure_one()
        return [
            ("supplier_rank", ">", 0),
            ("delay_calendar_type", "=", "natural"),
            ("company_id", "in", (False, self.company_id.id)),
        ]

    @api.depends("company_id", "supplier_calendar_id")
    def _compute_supplier_calendar_natural_count(self):
        for rec in self:
            rec.supplier_calendar_natural_count = self.env["res.partner"].search_count(
                rec._get_natural_vendors_domain()
            )

    def action_set_vendors_default_supplier_calendar(self):
        self.env["res.partner"].search(self._get_natural_vendors_domain()).write(
            {"delay_calendar_type": "company_calendar"}
        )
        return {"type": "ir.actions.client", "tag": "reload"}
