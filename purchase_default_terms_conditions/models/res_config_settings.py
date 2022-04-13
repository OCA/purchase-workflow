# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    purchase_note = fields.Text(
        related="company_id.purchase_note",
        string="Purchase Terms & Conditions",
        readonly=False,
    )

    use_purchase_note = fields.Boolean(
        string="Use Purchase Default Terms & Conditions",
        config_parameter="purchase.use_purchase_note",
    )
