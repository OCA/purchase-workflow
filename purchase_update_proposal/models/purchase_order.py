# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from odoo import _, fields, models
from odoo.exceptions import UserError

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
    check_price_on_proposal = fields.Boolean(
        related="partner_id.check_price_on_proposal"
    )
    proposal_display = fields.Boolean(
        string="Display/Hide Proposal",
        help="If checked, rejected proposals are hidden.",
    )
    partially_received = fields.Boolean(
        compute="_compute_partially_received",
        store=False,
        compute_sudo=True,
        help="Checked if at least partially delivered",
    )

    def _compute_partially_received(self):
        for rec in self:
            received = [x.received for x in rec.order_line if x.received]
            if received:
                rec.partially_received = True
            else:
                rec.partially_received = False

    def _check_updatable_proposal(self):
        """Override original method"""
        for rec in self:
            prevent_update = False
            if rec.partially_received:
                for __, vals in rec._prepare_proposal_data().items():
                    for elm in vals:
                        if "product_qty" in elm:
                            prevent_update = prevent_update or True
                        else:
                            prevent_update = prevent_update or False
                if prevent_update:
                    rec.proposal_updatable = "no"
                else:
                    rec.proposal_updatable = "yes"
            else:
                rec.proposal_updatable = "yes"

    def _compute_proposal(self):
        for rec in self:
            rec.proposal_count = len(rec.proposal_ids)

    def populate_all_purchase_lines(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda s: s.id not in self.proposal_ids.mapped("line_id").ids
            and s.received != "all"
        )
        self.write({"proposal_date": False})
        lines.button_update_proposal()

    def submit_proposal(self):
        self.ensure_one()
        self._prepare_proposal_data()
        self._check_updatable_proposal()
        if self.proposal_updatable == "yes":
            self.write({"proposal_state": "submitted"})

    def reset_proposal(self):
        self.ensure_one()
        self.write({"proposal_state": "draft"})
        self._check_updatable_proposal()

    def reject_proposal(self):
        self.ensure_one()
        self.write({"proposal_state": "rejected"})
        self._check_updatable_proposal()

    def approve_proposal(self):
        """
        We need to update purchase lines with approved lines.
        If 1 purchase line has created more than 1 line,
        we update the first one and create another purchase line
        """
        self.ensure_one()
        if not self._get_purchase_groups():
            raise UserError(_("You are not authorized to approve this proposal"))
        self._check_updatable_proposal()
        if self.proposal_updatable == "no":
            # example: qty is in proposal and purchase is partially received
            return
        body = []
        initial_state = False
        # these proposals'll reset these lines
        lines_to_0 = self.proposal_ids.filtered(lambda s: s.qty == 0.0).mapped(
            "line_id"
        )
        data = self._prepare_proposal_data()
        if data:
            self._hook_pending_proposal_approval()
            if self._product_qty_key_in_data(data) and self.state in [
                "confirmed",
                "approved",
            ]:
                # We have to reset order because of changed qty in confirmed order
                initial_state = self.state
                self.action_cancel()
                self.action_cancel_draft()
            self._update_proposal_to_purchase_line(data, body)
            self.message_post(body="\n".join(body))
        if initial_state in ("approved", "confirmed"):
            # altered quantity implied to reset order, then we approve them again
            self.signal_workflow("purchase_confirm")
            self.signal_workflow("purchase_approve")
        # Cancellation cases
        if lines_to_0:
            lines_to_0.cancel_from_proposal()
        # clean accepted proposals
        self.env["purchase.line.proposal"].search([("order_id", "=", self.id)]).unlink()
        self.write({"proposal_state": "approved"})

    def _product_qty_key_in_data(self, data):
        """Check if 'product_qty' key is anywhere in data"""
        self.ensure_one()
        qty2update = False
        for __, vals in data.items():
            for key in vals:
                if "product_qty" in key:
                    qty2update = qty2update or True
                else:
                    qty2update = qty2update or False
        return qty2update

    def _hook_for_cancel_process(self):
        "TODO remove: Kept for compatibility"
        self._hook_pending_proposal_approval()

    def _hook_pending_proposal_approval(self):
        """Cancellation here is a fake one, in fact it's a workaround
        to cleanly update purchase when picking has been created.
        Context can't be used because it disappears in the global odoo process
        So you may make changes in your custom process to capture falsy cancellation
        """
        return

    def _prepare_proposal_data(self):
        self.ensure_one()
        res = defaultdict(list)
        for elm in self.proposal_ids:
            # If new quantity is null, we don't update the purchaseline fields.
            if elm.qty == 0.0:
                continue
            vals = {"product_qty": elm.qty}
            if elm.line_id in res:
                # we already have a purchase_line as origin of these data
                # then we'll create a new line by copy
                vals["date_planned"] = elm.date or elm.line_id.date_planned
                if elm.price_u and self.partner_id.check_price_on_proposal:
                    vals["price_unit"] = elm.price_u or elm.line_id.price_unit
                else:
                    vals["price_unit"] = elm.line_id.price_unit
            else:
                # it'll be used for write
                if elm.price_u and self.partner_id.check_price_on_proposal:
                    vals["price_unit"] = elm.price_u
                if elm.date:
                    vals["date_planned"] = elm.date
                # We check original data are not the same than new ones
                updated_vals = {x: vals[x] for x in vals if vals[x] != elm[x]}
                vals = updated_vals
            res[elm.line_id].append(vals)
        self._check_data2update(res)
        if len(res) == 0:
            return {}
        return res

    def _check_data2update(self, data):
        for key, val in data.items():
            if isinstance(val, list) and not val[0]:
                raise UserError(_("No data to update for line ID '%s'") % key.id)

    def _update_proposal_to_purchase_line(self, data, body):
        for line_id in data:
            # we update first line
            line_id.write(data[line_id][0])
            body.append(
                _("Updated line '%(line)s' with %(data)s")
                % {"line": line_id.id, "data": data[line_id][0]}
            )
            if len(data[line_id]) > 1:
                todo = len(data[line_id]) - 1
                while todo:
                    # create other lines if any
                    vals = data[line_id][todo]
                    new_vals = {}
                    for elm in ["date_planned", "price_unit", "product_qty"]:
                        if elm in vals:
                            new_vals.update({elm: vals[elm]})
                    line_id.copy(new_vals)
                    body.append(_("Created line: %s") % vals)
                    todo -= 1

    def write(self, vals):
        if not self._get_purchase_groups() and self._fields_prevent_to_update(vals):
            # The user is not an Odoo purchaser, we must prevent to update other fields
            logger.info("Fields being written %s" % vals.keys())
            raise UserError(
                _("You can only update purchase proposal, not other fields")
            )
        if (  # mainly executed when run on form view
            len(self) == 1
            and self.proposal_display
            and self.proposal_state != "rejected"
        ):
            vals["proposal_display"] = False
        return super(PurchaseOrder, self).write(vals)

    def _get_purchase_groups(self):
        """Guess if the user is a standard purchaser"""
        return [
            x
            for x in self.env.user.groups_id
            if x in self.env.ref("purchase.group_purchase_user")
            or x in self.env.ref("purchase.group_purchase_manager")
        ]

    def _fields_prevent_to_update(self, vals):
        if [x for x in vals.keys() if x[:9] != "proposal_"]:
            return True
        return False

    def _subscribe_portal_vendor(self):
        self.ensure_one()
        cial_partner = self.partner_id.commercial_partner_id
        partner_ids = cial_partner.child_ids.ids
        partner_ids.append(cial_partner.id)
        users = self.env["res.users"].search([("partner_id", "in", partner_ids)])
        if users:
            users = users.filtered(
                lambda s: self.env.ref(
                    "purchase_update_proposal.group_supplier_own_purchase"
                )
                in s.groups_id
            )
            if users:
                self.message_subscribe_users(users.ids)

    def button_switch2other_view(self):
        self.ensure_one()
        view = self.env.ref("purchase_update_proposal.supplier_purchase_order_form")
        if self.env.context.get("from_supplier_view"):
            view = self.env.ref("purchase.purchase_order_form")
        return {
            "res_model": "purchase.order",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "type": "ir.actions.act_window",
            "view_id": view.id,
        }
