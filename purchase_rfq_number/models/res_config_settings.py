from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_name_po = fields.Boolean(related="company_id.keep_name_po", readonly=False)
    auto_attachment_rfq = fields.Boolean(
        related="company_id.auto_attachment_rfq", readonly=False
    )
