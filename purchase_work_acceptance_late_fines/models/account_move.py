# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    late_wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="Late WA",
        domain=lambda self: self._domain_late_wa(),
        help="For the supplier with late penalty (during work acceptance), "
        "choosing the late WA to get the amount this partner need to pay.",
    )

    @api.model
    def _domain_late_wa(self):
        move_obj = self.env["account.move"]
        used_wa_ids = move_obj.search([("state", "!=", "cancel")]).mapped("late_wa_id")
        dom = [
            ("fines_late", ">", 0.0),
            ("state", "!=", "cancel"),
            ("id", "not in", used_wa_ids.ids),
        ]
        return dom

    @api.onchange("partner_id")
    def _onchange_partner_late_wa(self):
        self.late_wa_id = False
        self.invoice_line_ids = False
        self.line_ids = False
        if self.partner_id:
            domain = self._domain_late_wa()
            domain.append(("partner_id", "=", self.partner_id.id))
            return {"domain": {"late_wa_id": domain}}

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
        move_line = self.env["account.move.line"]
        self.line_ids = False
        late_wa = self.late_wa_id
        if self.type == "out_invoice" and late_wa:
            move_dict = self._prepare_move_wa_late(late_wa)
            move_line_dict = late_wa._prepare_late_wa_in_account_move_line()
            move_line_dict.update(
                {"move_id": self.id, "date_maturity": self.invoice_date_due}
            )
            self.write(move_dict)
            move_line.new(move_line_dict)
        self._onchange_currency()
