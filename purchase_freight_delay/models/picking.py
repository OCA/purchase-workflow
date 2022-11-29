# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models

from .purchase import HELP_DISPATCH, HELP_DURATION


class StockPicking(models.Model):
    _inherit = "stock.picking"

    dispatch_date = fields.Datetime(
        # dispatch_date is not computed on purpose
        help=HELP_DISPATCH,
        copy=False,
        tracking=True,
    )
    freight_duration = fields.Integer(
        compute="_compute_freight_duration",
        store=True,
        readonly=False,
        copy=False,
        help=HELP_DURATION,
        tracking=True,
    )

    @api.depends("dispatch_date", "scheduled_date")
    def _compute_freight_duration(self):
        _set_freight_fields = self.env["purchase.order"]._set_freight_fields
        for rec in self:
            res = _set_freight_fields(
                rec.scheduled_date,
                rec.dispatch_date,
                rec.freight_duration,
                "freight_duration",
            )
            rec.freight_duration = res["freight_duration"]

    @api.depends("freight_duration", "dispatch_date")
    def _compute_scheduled_date(self):
        _set_freight_fields = self.env["purchase.order"]._set_freight_fields
        for rec in self:
            res = _set_freight_fields(
                rec.scheduled_date,
                rec.dispatch_date,
                rec.freight_duration,
                "receive_date",
            )
            rec.scheduled_date = res["receive_date"]
