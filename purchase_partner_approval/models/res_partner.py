# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    purchase_ok = fields.Boolean(
        string="Can Purchase To",
        copy=False,
        readonly=True,
    )
    candidate_purchase = fields.Boolean(
        string="Candidate Purchase To",
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "candidate_purchase" in fields and "candidate_purchase" not in res:
            # Set default when creating from Purchase App menu
            res["candidate_purchase"] = bool(res.get("supplier_rank"))
        return res

    def _set_purchase_ok(self):
        # Candidate Purchase is set/changed only in draft state
        # Can Purchase is set only when not in draft state
        # This allows for Candidate Purchase changes to be effetive only after approval
        for partner in self.filtered(lambda x: x.stage_id.state != "draft"):
            if partner.parent_id:
                # Child contacts inherit that same purchase_ok value
                ok = partner.parent_id.purchase_ok
            else:
                ok = partner.candidate_purchase and partner.stage_id.approved_purchase
            super(Partner, partner).write({"purchase_ok": ok})

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._set_purchase_ok()
        return new

    def write(self, vals):
        res = super().write(vals)
        # Do not set ok flag when moving to draft state
        if "stage_id" in vals:
            to_state = self.env["res.partner.stage"].browse(vals["stage_id"]).state
            to_state != "draft" and self._set_purchase_ok()
        return res
