# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models

HELP_DURATION = "Duration is substracted from Receive date or added to Dispatch date"
HELP_DISPATCH = "When the goods exit the boarding place"


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    freight_rule_id = fields.Many2one(
        comodel_name="freight.rule",
        domain="[['partner_src_id','in', (False, incoterm_address_id)]]",
    )
    freight_duration = fields.Integer(
        compute="_compute_freight_duration",
        inverse="_inverse_freight_duration",
        store=True,
        help=HELP_DURATION,
    )
    receive_date = fields.Datetime(
        compute="_compute_receive_date",
        store=True,
    )
    dispatch_date = fields.Datetime(
        readonly=False,
        store=True,
        compute="_compute_dispatch_date",
        help=HELP_DISPATCH,
    )
    freight_change_policy = fields.Selection(
        string="Duration impact",
        selection=[
            ("dispatch", "Dispatch"),
            ("receive", "Received"),
            ("duration", "Duration"),
        ],
        required=True,
        default="dispatch",
        ondelete={"dispatch": "set default", "received": "set default"},
        help="Choose which field will be recomputed",
    )

    incoterm_date = fields.Datetime(
        related="dispatch_date",
        string="Incoterm date",
        help="Date of transfert of responsibility (is freight dispatch date)",
    )

    def _set_freight_fields(
        self, receive_date, dispatch_date, freight_duration, policy
    ):
        res = {
            "receive_date": receive_date,
            "dispatch_date": dispatch_date or receive_date,  # init
            "freight_duration": freight_duration or 0,
        }

        def recompute_freight_duration():
            if receive_date and dispatch_date:
                res["freight_duration"] = (receive_date - dispatch_date).days

        def recompute_dispatch_date():
            if receive_date:
                res["dispatch_date"] = receive_date - timedelta(days=freight_duration)

        def recompute_receive_date():
            if dispatch_date:
                res["receive_date"] = dispatch_date + timedelta(days=freight_duration)

        {
            "freight_duration": recompute_freight_duration,
            "dispatch_date": recompute_dispatch_date,
            "receive_date": recompute_receive_date,
        }[policy]()

        return res

    def _compute_freight(self, origin):

        lk = {
            "_compute_receive_date": {
                "policy": "receive",
                "field": "receive_date",
            },
            "_compute_dispatch_date": {
                "policy": "dispatch",
                "field": "dispatch_date",
            },
            "_compute_freight_duration": {
                "policy": "duration",
                "field": "freight_duration",
            },
        }
        policy = lk[origin]["policy"]
        field = lk[origin]["field"]

        for rec in self:
            if rec.freight_change_policy != policy:
                continue
            res = self._set_freight_fields(
                rec.receive_date, rec.dispatch_date, rec.freight_duration, field
            )
            rec[field] = res[field]

    @api.depends("freight_duration", "dispatch_date")
    def _compute_receive_date(self):
        self._compute_freight("_compute_receive_date")

    @api.depends("freight_duration", "receive_date")
    def _compute_dispatch_date(self):
        self._compute_freight("_compute_dispatch_date")

    @api.depends("freight_rule_id", "dispatch_date", "receive_date")
    def _compute_freight_duration(self):
        for rec in self:
            # inject duration from freight_rule
            if rec.freight_rule_id:
                rec.freight_duration = rec.freight_rule_id.duration
            self._compute_freight("_compute_freight_duration")

    def _inverse_freight_duration(self):
        for rec in self:
            # remove freight_rule when duration changes
            if (
                rec.freight_rule_id
                and rec.freight_duration != rec.freight_rule_id.duration
            ):
                rec.freight_rule_id = False

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res.update(
            {
                "freight_duration": self.freight_duration,
                "dispatch_date": self.dispatch_date,
            }
        )
        return res

    def write(self, vals):
        # change date_planned with ours
        super().write(vals)
        if "receive_date" or "dispatch_date" or "freight_duration" in vals:
            # not really efficient
            super().write({"date_planned": self.receive_date})


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ):
        # propagate to purchase lines
        values = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        if self.order_id.receive_date:
            values["date"] = self.order_id.receive_date
        return values
