# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WorkAcceptance(models.Model):
    _inherit = "work.acceptance"

    late_days = fields.Integer(
        string="Late Days",
        compute="_compute_late_days",
        inverse="_inverse_late_days",
        tracking=True,
        help="Compute the day(s) from Received Date - Due Date",
    )
    fines_rate = fields.Monetary(
        string="Fines Rate",
        default=lambda self: self.env.company.wa_fines_rate,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    fines_late = fields.Monetary(
        string="Fines Amount",
        compute="_compute_fines_late",
        store=True,
        readonly=True,
        tracking=True,
        states={"draft": [("readonly", False)]},
    )
    fines_invoice_count = fields.Integer(
        compute="_compute_fines_invoice_ids", string="Fines Invoice Count"
    )
    fines_invoice_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="late_wa_id",
        string="Fines Invoices",
    )

    @api.depends("fines_invoice_ids")
    def _compute_fines_invoice_ids(self):
        for rec in self:
            rec.fines_invoice_count = len(rec.fines_invoice_ids)

    def action_view_invoice(self, move_ids=False):
        action = self.env.ref("account.action_move_out_invoice_type")
        result = action.read()[0]
        active_ids = self._context.get("active_ids", False)
        fines_invoice = self._context.get("fines_invoice", False)
        # Case smart button
        if fines_invoice:
            active_ids = self.ids
        wa_ids = self.env["work.acceptance"].browse(active_ids)
        # create fines invoice from tree view
        if len(wa_ids) > 1:
            result["domain"] = "[('id', 'in', " + str(move_ids.ids) + ")]"
        # view invoice from smart button
        elif len(wa_ids.fines_invoice_ids.ids) > 1 and fines_invoice:
            result["domain"] = (
                "[('id', 'in', " + str(wa_ids.fines_invoice_ids.ids) + ")]"
            )
        # create fines invoice from form view
        else:
            res = self.env.ref("account.view_move_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = move_ids and move_ids.id or wa_ids.fines_invoice_ids.id
        return result

    def action_create_fines_invoice_form(self):
        return self.with_context(
            active_ids=self.ids, active_model="work.acceptance", active_id=self.id
        ).action_create_fines_invoice()

    def action_create_fines_invoice(self):
        move_obj = self.env["account.move"]
        active_ids = self._context.get("active_ids", False)
        wa_ids = self.env["work.acceptance"].browse(active_ids)
        created_invoice = move_obj.search(
            [("late_wa_id", "in", wa_ids.ids), ("state", "!=", "cancel")]
        )
        if created_invoice:
            document = ", ".join(created_invoice.mapped("late_wa_id.name"))
            raise UserError(_("%s created Fines invoice." % document))
        if any(wa_id.fines_late <= 0.0 for wa_id in wa_ids):
            raise UserError(_("Can not create invoice(s) are not fines"))
        move_dict = [
            {
                "partner_id": wa.partner_id.id,
                "move_type": "out_invoice",
                "late_wa_id": wa.id,
                "invoice_line_ids": [
                    (0, 0, wa._prepare_late_wa_in_account_move_line())
                ],
            }
            for wa in wa_ids
        ]
        move_ids = move_obj.create(move_dict)
        result = self.action_view_invoice(move_ids)
        return result

    def _prepare_late_wa_in_account_move_line(self, name=False):
        """ param name for specific variable name"""
        return {
            "name": name or _("Work Acceptance Late Delivery Fines %s") % (self.name),
            "account_id": self.env.company.wa_fines_late_account_id,
            "price_unit": self.fines_late,
        }

    @api.depends("date_accept", "date_due")
    def _compute_late_days(self):
        today = fields.Datetime.now()
        for rec in self:
            date_accept = rec.date_accept or today
            if rec.date_due and rec.date_due <= date_accept:
                rec.late_days = (date_accept - rec.date_due).days
            else:
                rec.late_days = 0

    def _inverse_late_days(self):
        for rec in self:
            rec.date_due = fields.Datetime.now() - relativedelta(days=rec.late_days)

    @api.depends("late_days", "fines_rate")
    def _compute_fines_late(self):
        for rec in self:
            if rec.late_days and rec.fines_rate:
                rec.fines_late = rec.late_days * rec.fines_rate
            else:
                rec.fines_late = 0
