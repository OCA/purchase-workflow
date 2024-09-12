# Copyright 2015 ForgeFlow S.L.
# Copyright 2018 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.depends("order_line.account_analytic_id")
    def _compute_analytic_accounts(self):
        for purchase in self:
            purchase.account_analytic_ids = purchase.mapped(
                "order_line.account_analytic_id"
            )

    @api.model
    def _search_analytic_accounts(self, operator, value):
        po_line_obj = self.env["purchase.order.line"].filtered(
            lambda x: x.account_analytic_id == value
        )
        if not value:
            return [("account_analytic_id", "=", False)]
        if isinstance(value, (tuple, list)):
            # we are searching on a list of ids
            domain = [("order_id", "!=", False), ("account_analytic_id", "in", value)]
        else:
            if isinstance(value, int):
                # we are searching on the id of the analytic_account
                domain = [
                    ("account_analytic_id", "=", value),
                ]
            else:
                # assume we are searching on the analytic account name
                domain = [
                    ("account_analytic_id.name", "ilike", value),
                ]
        po_lines = po_line_obj.search(domain)
        orders = po_lines.mapped("order_id")
        if operator in ("!=", "not in"):
            return [("id", "not in", orders.ids)]
        else:
            return [("id", "in", orders.ids)]

    account_analytic_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        string="Analytic Account(s)",
        compute="_compute_analytic_accounts",
        search="_search_analytic_accounts",
        readonly=True,
    )
