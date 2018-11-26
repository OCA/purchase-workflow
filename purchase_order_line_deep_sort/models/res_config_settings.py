# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_po_line_order = fields.Selection(
        related='company_id.default_po_line_order',
        string="Line Order",
    )
    default_po_line_direction = fields.Selection(
        related='company_id.default_po_line_direction',
        string="Sort Direction",
    )
