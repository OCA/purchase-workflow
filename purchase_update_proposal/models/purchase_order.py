# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    proposal_ids = fields.One2many(
        comodel_name="purchase.line.proposal", inverse_name="order_id"
    )
    proposal_count = fields.Integer(compute="_compute_proposal")
    proposal_state = fields.Selection(
        selection=[
            ("draft", "To Submit"),
            ("submitted", "To Approve by an internal user"),
            ("rejected", "Rejected"),
            ("approved", "Approved"),
        ],
        readonly=True,
        copy=False,
        default="draft",
    )
    proposal_updatable = fields.Selection(
        selection=[("", "undefined"), ("yes", "Yes"), ("no", "No")],
        default="",
        copy=False,
        help="Computed to be sure that stock move are in a state "
        "compatible with update",
    )
    proposal_date = fields.Date(
        string="Update all dates at once",
        help="Update all date of the order with this date",
        copy=False,
    )

    def _check_updatable_proposal(self):
        self = self.sudo()
        for rec in self:
            moves = self.env["stock.move"].search(
                [("purchase_line_id", "in", rec.order_line.ids)]
            )
            if any(
                True
                for x in moves
                if x.state
                in (
                    "cancel",
                    "done",
                )
            ):
                rec.proposal_updatable = "no"
            else:
                rec.proposal_updatable = "yes"

    @api.multi
    def _compute_proposal(self):
        for rec in self:
            rec.proposal_count = len(rec.proposal_ids)

    @api.multi
    def populate_all_purchase_lines(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda s: s.id not in self.proposal_ids.mapped("line_id").ids
        )
        lines.button_update_proposal()

    @api.onchange("proposal_date")
    def onchange_proposal_date(self):
        for rec in self:
            vals = [
                (1, x.id, {"date": rec.proposal_date})
                for x in rec.proposal_ids
            ]
            rec.proposal_ids = vals

    @api.multi
    def submit_proposal(self):
        self.ensure_one()
        self._prepare_proposal_data()
        self._check_updatable_proposal()
        if self.proposal_updatable == "yes":
            self.write({"proposal_state": "submitted"})

    @api.multi
    def reset_proposal(self):
        self.ensure_one()
        self.write({"proposal_state": "draft"})
        self._check_updatable_proposal()

    @api.multi
    def reject_proposal(self):
        self.ensure_one()
        self.write({"proposal_state": "rejected"})
        self._check_updatable_proposal()

    @api.multi
    def approve_proposal(self):
        """
        We need to update purchase lines with approvaled lines.
        If 1 purchase line has created more than 1 line,
        we update the first one and create another purchase line
        """
        self.ensure_one()
        if not self._get_purchase_groups:
            raise UserError("You are not authorized to approve this proposal")
        self._check_updatable_proposal()
        if self.proposal_updatable == "no":
            return
        body = []
        data = self._prepare_proposal_data()
        initial_state = self.state
        if initial_state in ["confirmed", "approved"]:
            self.wkf_action_cancel()
            self.action_cancel_draft()
        if data:
            self._update_proposal_to_purchase_line(data, body)
            self.env["purchase.line.proposal"].search(
                [("order_id", "=", self.id)]
            ).unlink()
        self.write({"proposal_state": "approved"})
        self.message_post(body="\n".join(body))
        self._post_process_approved_proposal(initial_state)

    def _post_process_approved_proposal(self, initial_state):
        """Customize according to your needs according delegation
        attributed to users with only this group group_purchase_proposal_user
        """
        if initial_state in ("approved", "confirmed"):
            self.signal_workflow("purchase_confirm")
            self.signal_workflow("purchase_approved")

    def _prepare_proposal_data(self):
        self.ensure_one()
        res = defaultdict(list)
        for elm in self.proposal_ids:
            if not elm.qty and not elm.price_u and not elm.date:
                raise UserError(
                    _("You must fill at least Qty, Date or Price on proposal")
                )
            vals = {"product_qty": elm.qty}
            if elm.line_id in res:
                # we already have a purchase_line as origin of these data
                # then we'll create a new line
                vals["order_id"] = elm.order_id.id
                vals["price_unit"] = elm.price_u or elm.line_id.price_unit
                vals["date_planned"] = elm.date or elm.line_id.date_planned
                vals["product_id"] = elm.line_id.product_id.id
                vals["name"] = elm.line_id.product_id.display_name
                vals["proposal"] = elm
            else:
                # it'll be used for write
                if elm.price_u:
                    vals["price_unit"] = elm.price_u
                if elm.date:
                    vals["date_planned"] = elm.date
                # We check original data are not the same than new ones
                updated_vals = {x: vals[x] for x in vals if vals[x] != elm[x]}
                vals = updated_vals
            res[elm.line_id].append(vals)
        self._check_data2update(res)
        return res

    def _check_data2update(self, data):
        for key, val in data.items():
            if isinstance(val, list) and not val[0]:
                raise UserError(
                    _("No data to update for line ID '%s'") % key.id)

    def _update_proposal_to_purchase_line(self, data, body):
        for line_id in data:
            # we update first line
            line_id.write(data[line_id][0])
            body.append(_("Updated line '%s' with %s") % (line_id.id, data[line_id][0]))
            if len(data[line_id]) > 1:
                todo = len(data[line_id]) - 1
                while todo:
                    # create other lines if any
                    self.env["purchase.order.line"].create(data[line_id][todo])
                    body.append(_("Created line: %s" % data[line_id][todo]))
                    todo -= 1

    @api.multi
    def write(self, vals):
        if not self._get_purchase_groups() and [
                x for x in vals.keys() if x[:9] != "proposal_"]:
            # The user is not an Odoo purchaser, we must prevent to update other fields
            logger.info("Fields being writing %s" % vals.keys())
            raise UserError(
                _("You can only update purchase proposal, not other fields")
            )
        return super(PurchaseOrder, self).write(vals)

    @api.model
    def _get_purchase_groups(self):
        """ Guess if the user is a standard purchaser
        """
        return [
            x
            for x in self.env.user.groups_id
            if x in self.env.ref("purchase.group_purchase_user")
            or x in self.env.ref("purchase.group_purchase_manager")
        ]
