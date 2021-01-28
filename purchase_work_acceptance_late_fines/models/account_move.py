# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    late_wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="Late WA",
        domain=lambda self: self._domain_late_wa(),
        index=True,
        ondelete="restrict",
        help="For the supplier with late penalty (from work acceptance), "
        "choosing the late WA to get the amount this partner need to pay.",
    )

    @api.model
    def _domain_late_wa(self):
        AccountMove = self.env["account.move"]
        used_wa_ids = AccountMove.search([("state", "!=", "cancel")]).mapped(
            "late_wa_id"
        )
        dom = [
            ("fines_late", ">", 0.0),
            ("state", "!=", "cancel"),
            ("id", "not in", used_wa_ids.ids),
        ]
        if self.env.context.get("default_partner_id", False):
            dom.append(("partner_id", "=", self.env.context["default_partner_id"]))
        return dom

    @api.onchange("partner_id")
    def _onchange_partner_late_wa(self):
        if self.late_wa_id:
            self.late_wa_id = False
            self.invoice_line_ids = False
            self.line_ids = False
            if self.partner_id:
                self.with_context(
                    default_partner_id=self.partner_id.id
                )._domain_late_wa()

    def _prepare_move_wa_late(self, wa):
        move_dict = {
            "partner_id": wa.partner_id.id,
            "currency_id": wa.currency_id,
            "company_id": wa.company_id,
        }
        return move_dict

    @api.onchange("late_wa_id")
    def _onchange_late_wa_id(self):
        """ Auto fill values from WA delivery late fines """
        MoveLine = self.env["account.move.line"]
        if self.move_type == "out_invoice" and self.late_wa_id:
            self.invoice_line_ids = False
            self.line_ids = False
            move_dict = self._prepare_move_wa_late(self.late_wa_id)
            move_line_dict = self.late_wa_id._prepare_late_wa_move_line()
            move_line_dict.update(
                {"move_id": self.id, "date_maturity": self.invoice_date_due}
            )
            self.update(move_dict)
            MoveLine.new(move_line_dict)
        self._onchange_currency()
