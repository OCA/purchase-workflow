# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    cost_distribution_ok = fields.Boolean(
        "Products linked to Landed Costs",
        default="True",
        help="""If checked, storable Products from this Vendor will need
            to be linked to Landed Costs by default""",
    )
