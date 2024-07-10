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
        domain="[['partner_src_id','in', (False)]]",
        string="Rule",
        # recomputed with more incoterm_address_id
        # in onchange()
    )
    freight_duration = fields.Integer(
        compute="_compute_freight_duration",
        inverse="_inverse_freight_duration",
        string="Duration",
        store=True,
        help=HELP_DURATION,
    )
    receive_date = fields.Datetime(
        compute="_compute_receive_date",
        store=True,
    )
    dispatch_date = fields.Datetime(
        # dispatch_date is computed
        # use case:
        # PO is created from a procurement with a receive_date (date_planned)
        # then, a duration is choosen (based on avg supplier transit delay)
        # so dispatch_date = recieve_date - duration
        # dispatch date is the date asked to the supplier
        readonly=False,
        store=True,
        compute="_compute_dispatch_date",
        help=HELP_DISPATCH,
    )
    freight_change_selector = fields.Selection(
        # choosen by the user
        # it's easier for user to reason about he can change
        # (change_selector) rather than computed field (change_policy)
        selection=[
            ("date", "Date"),
            ("duration", "Duration"),
        ],
        string="Change Selector",
        default="duration",
    )
    freight_change_policy = fields.Selection(
        # freight_change_policy: the field to recompute
        selection=[
            ("dispatch", "Dispatch"),
            ("receive", "Received"),
            ("duration", "Duration"),
        ],
        compute="_compute_freight_change_policy",
        required=True,
        default="receive",
        ondelete={"dispatch": "set default", "received": "set default"},
        help="Choose which field will be recomputed",
    )

    incoterm_date = fields.Datetime(
        related="dispatch_date",
        string="Incoterm date",
        help="Date of transfert of responsibility (is freight dispatch date)",
        readonly=True,
    )

    @api.onchange("incoterm_address_id")
    def onchange_freight_rule_id(self):
        return {
            "domain": {
                "freight_rule_id": [
                    ("partner_src_id", "in", (False, self.incoterm_address_id.id))
                ]
            }
        }

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

    @api.depends("freight_change_selector")
    def _compute_freight_change_policy(self):
        for rec in self:
            if rec.freight_change_selector == "date":
                rec.freight_change_policy = "duration"
            else:
                rec.freight_change_policy = "receive"

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res.update(
            {
                "freight_duration": self.freight_duration,
                "dispatch_date": self.dispatch_date,
                "scheduled_date": self.receive_date,
            }
        )
        return res

    def write(self, vals):
        # change date_planned with ours
        res = super().write(vals)
        if [
            x
            for x in ("receive_date", "dispatch_date", "freight_duration")
            if x in vals
        ]:
            # not really efficient
            for rec in self:
                res = super().write({"date_planned": rec.receive_date})
        return res


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
