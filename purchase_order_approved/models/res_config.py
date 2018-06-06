# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_approve_active = fields.Boolean(
        related='company_id.purchase_approve_active',
        string="State 'Approved' in Purchase Orders",
    )
