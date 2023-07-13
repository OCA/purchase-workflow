# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default["order_line"] = [
            (0, 0, line.copy_data()[0])
            for line in self.order_line.filtered(lambda l: not l.is_deposit)
        ]
        return super(PurchaseOrder, self).copy_data(default)

    def action_create_invoice(self):
        has_deposit = len(self.filtered("order_line.is_deposit")) > 0
        if not has_deposit or self.env.context.get("advance_deduct_option"):
            return super().action_create_invoice()
        wizard = self.env.ref("purchase_deposit.view_purchase_advance_deduct_option")
        return {
            "name": _("Advance/Deposit Deduction Option"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.advance.deduct.option",
            "views": [(wizard.id, "form")],
            "view_id": wizard.id,
            "target": "new",
        }


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_deposit = fields.Boolean(
        string="Is a deposit payment",
        help="Deposit payments are made when creating bills from a purhcase"
        " order. They are not copied when duplicating a purchase order.",
    )

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        if self.is_deposit:
            res["quantity"] = -1 * self.qty_invoiced
        return res
