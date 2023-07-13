# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PurchaseAdvanceReturnOption(models.TransientModel):
    _name = "purchase.advance.deduct.option"
    _description = "Select how to return advance in vendor bill"

    advance_deduct_option = fields.Selection(
        [
            ("proportional", "Deduct Deposit Proportionally"),
            ("full", "Deduct Full Deposit (Standard)"),
        ],
        string="Advance/Deposit Deduction Option",
        default="proportional",
        required=True,
    )

    def create_invoice(self):
        self.ensure_one()
        order = (
            self.env["purchase.order"]
            .browse(self._context.get("active_id"))
            .with_context(
                create_bill=self._context.get("create_bill"),
                advance_deduct_option=self.advance_deduct_option,
            )
        )
        return order.sudo().action_create_invoice()
