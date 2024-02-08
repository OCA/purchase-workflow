from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_packaging_level_id = fields.Many2one(
        related="company_id.purchase_packaging_level_id",
        readonly=False,
        help="Count purchase order packaging needed for this packing level.",
    )
