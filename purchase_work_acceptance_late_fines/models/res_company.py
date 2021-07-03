# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    wa_fines_rate = fields.Monetary(string="Fines Rate")
    wa_fines_late_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Late Delivery Fines Revenue Account",
    )
