# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    purchase_selectable = fields.Boolean(
        string="Selectable in purchase orders",
        default=lambda self: self._default_purchase_selectable(),
    )

    @api.model
    def _default_purchase_selectable(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_partner_selectable_option.default_purchase_selectable")
        )
        return False if param == "0" else True
