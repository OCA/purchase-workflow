# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_order_type_required = fields.Boolean(
        string="Require Purchase Order Type",
        help="If enabled, a purchase order can only be saved in the form once "
        "it has an order type.",
    )
