# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    branch_id = fields.Many2one(
        comodel_name="res.branch",
    )

    def action_view_invoice(self, invoices=False):
        """Add branch in bills from purchase"""
        res = super().action_view_invoice(invoices)
        if invoices:
            for inv in invoices:
                inv.branch_id = self[0].branch_id.id
        return res

    def action_create_invoice(self):
        """Not allow create bills from multi branch"""
        all_branch = [rec.branch_id.id for rec in self]
        if len(set(all_branch)) != 1:
            raise UserError(_("You cannot create bills with multi branch."))
        return super().action_create_invoice()
