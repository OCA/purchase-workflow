# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from .purchase import HELP_DURATION, HELP_DISPATCH


class StockPicking(models.Model):
    _inherit = "stock.picking"

    freight_duration = fields.Integer(
        store=True, readonly=True, copy=False, help=HELP_DURATION
    )
    dispatch_date = fields.Date(
        copy=False,
        readonly=True,
        help=HELP_DISPATCH,
    )
