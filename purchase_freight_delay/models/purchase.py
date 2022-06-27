# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DTF,
    DEFAULT_SERVER_DATE_FORMAT as DF,
)

HELP_DURATION = "Duration is substracted from Received date or added to Dispatch date"
HELP_DISPATCH = "When the goods exit the boarding place"


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    freight_rule_id = fields.Many2one(comodel_name="freight.rule", copy=False)
    freight_duration = fields.Integer(
        compute="_compute_freight_duration",
        inverse="_inverse_freight_duration",
        store=True,
        copy=False,
        help=HELP_DURATION,
    )
    dispatch_date = fields.Date(
        copy=False,
        readonly=False,
        compute="_compute_dispatch_date",
        inverse="_inverse_dispatch_date",
        help=HELP_DISPATCH,
    )
    freight_duration_policy = fields.Selection(
        string="Duration impact",
        selection=[("dispatch", "Dispatch"), ("received", "Received")],
        required=True,
        copy=False,
        default="dispatch",
        ondelete={"dispatch": "set default", "received": "set default"},
        help="Choose which date field'll be impacted modifying duration field",
    )

    def onchange(self, values, field_name, field_onchange):
        def get_data(myfield):
            "Get current data after all onchanges played"
            mydata = result["value"].get(myfield) or values.get(myfield) or False
            if "date" in myfield and isinstance(mydata, str):
                format_date = DTF
                if myfield == "dispatch_date":
                    format_date = DF
                mydata = datetime.strptime(mydata, format_date)
            return mydata

        result = super().onchange(values, field_name, field_onchange)
        if not values.get("dispatch_date") and not values.get("date_planned"):
            return result
        # we tracks these fields to amend behavior
        ffields = [
            "dispatch_date",
            "date_planned",
            "freight_duration",
            "freight_duration_policy",
        ]
        trigger = False
        for elm in ffields:
            if field_onchange.get(elm) == "1":
                trigger = trigger or True
        if trigger:
            vals = {}
            ffields.append("state")
            for myfield in ffields:
                vals[myfield] = get_data(myfield)
            res = self._update_freight_fields_and_co(vals=vals)
            if res:
                res["dispatch_date"] = res["dispatch_date"].strftime(DF)
                res["date_planned"] = res["date_planned"].strftime(DTF)
                result["value"].update(res)
        return result

    def _update_freight_fields_and_co(self, vals=None):
        from_onchange = False
        if vals:
            from_onchange = True
        else:
            self.ensure_one()
            if not self.dispatch_date and not self.date_planned:
                return
            # we switch to dict to share behavior between compute and onchange.
            # it's required while there are onchanges in native code
            vals = {
                "dispatch_date": self.dispatch_date,
                "date_planned": self.date_planned,
                "freight_duration": self.freight_duration,
                "freight_duration_policy": self.freight_duration_policy,
                "state": self.state,
            }
        if vals["state"] in ("done", "cancel"):
            return vals
        if not vals["dispatch_date"]:
            # initialisation
            # TOFIX While form is not saved, dispatch_date is reset to False
            vals["dispatch_date"] = self._origin.dispatch_date or vals["date_planned"]
        if vals["freight_duration_policy"] == "dispatch" or not vals["dispatch_date"]:
            vals["dispatch_date"] = vals["date_planned"] - timedelta(
                days=vals["freight_duration"] or 0
            )
        else:
            vals["date_planned"] = vals["dispatch_date"] + timedelta(
                days=vals["freight_duration"] or 0
            )
        if from_onchange:
            return vals
        else:
            # we switch back to compute syntax
            self.dispatch_date = vals["dispatch_date"]
            self.date_planned = vals["date_planned"]
            self.freight_duration = vals["freight_duration"]
            self.freight_duration_policy = vals["freight_duration_policy"]

    @api.depends("freight_duration", "date_planned")
    def _compute_dispatch_date(self):
        for rec in self:
            rec._update_freight_fields_and_co()

    def _inverse_dispatch_date(self):
        for rec in self:
            rec._update_freight_fields_and_co()

    @api.depends("freight_rule_id")
    def _compute_freight_duration(self):
        for rec in self:
            if rec.freight_rule_id:
                rec.freight_duration = rec.freight_rule_id.duration
                rec._update_freight_fields_and_co()

    def _inverse_freight_duration(self):
        for rec in self:
            rec._update_freight_fields_and_co()
            if rec.freight_duration and rec.freight_rule_id:
                rec.freight_rule_id = False
            if not rec.freight_duration and not rec.freight_rule_id:
                rec.order_line._set_initial_date_planned(self)

    def _prepare_picking(self):
        # TODO
        res = super()._prepare_picking()
        res.update(
            {
                # "freight_rule_id": self.freight_rule_id.id,
                "freight_duration": self.freight_duration,
                "dispatch_date": self.dispatch_date,
            }
        )
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _set_initial_date_planned(self, po):
        """Same code as in _onchange_quantity() and other places"""
        for rec in self:
            seller = rec.product_id._select_seller(
                partner_id=po.partner_id,
                quantity=rec.product_qty,
                date=po.date_order and po.date_order.date(),
                uom_id=rec.product_uom,
                params={"order_id": po},
            )
            if seller:
                rec.date_planned = rec._get_date_planned(seller).strftime(DTF)
