# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_line_warn_option = fields.Many2one(
        comodel_name="warn.option",
    )

    @api.onchange("purchase_line_warn_option")
    def _onchange_purchase_line_warn_option(self):
        if self.purchase_line_warn != "no-message" and self.purchase_line_warn_option:
            self.purchase_line_warn_msg = self.purchase_line_warn_option.name
