# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_order_type_required = fields.Boolean(
        related="company_id.purchase_order_type_required",
        readonly=False,
    )
