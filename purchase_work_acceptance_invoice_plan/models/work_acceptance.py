# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkAcceptance(models.Model):
    _inherit = "work.acceptance"

    installment_id = fields.Many2one(
        comodel_name="purchase.invoice.plan",
        string="Invoice Plan",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
