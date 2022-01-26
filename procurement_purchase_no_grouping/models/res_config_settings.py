# Copyright 2020 - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Configuration of default value for procurement purchase grouping."""

    _inherit = "res.config.settings"
    _description = "Procurement purchase grouping settings"

    procured_purchase_grouping = fields.Selection(
        related="company_id.procured_purchase_grouping",
        readonly=False,
    )
