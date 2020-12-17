# Copyright 2018 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    po_line_order_default = fields.Selection(
        related="company_id.default_po_line_order",
        string="Line Order",
        readonly=False,
    )
    po_line_direction_default = fields.Selection(
        related="company_id.default_po_line_direction",
        string="Sort Direction",
        readonly=False,
    )

    @api.onchange("po_line_order_default")
    def onchange_po_line_order_default(self):
        """ Reset direction line order when user remove order field value """
        if not self.po_line_order_default:
            self.po_line_direction_default = False
