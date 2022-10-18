# Copyright 2014-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_analytic_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        compute="_compute_analytic_account",
        inverse="_inverse_analytic_account",
        help="This account will be propagated to all lines, if you need "
        "to use different accounts, define the account at line level.",
    )

    @api.depends("order_line.account_analytic_id")
    def _compute_analytic_account(self):
        for rec in self:
            account = rec.mapped("order_line.account_analytic_id")
            if len(account) == 1:
                rec.account_analytic_id = account
            else:
                rec.account_analytic_id = False

    def _inverse_analytic_account(self):
        for rec in self:
            if rec.account_analytic_id:
                rec.order_line.account_analytic_id = rec.account_analytic_id
