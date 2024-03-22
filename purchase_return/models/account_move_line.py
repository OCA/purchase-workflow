# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_return_line_id = fields.Many2one(
        "purchase.return.order.line",
        "Purchase Return Order Line",
        ondelete="set null",
        copy=False,
        index=True,
    )
    purchase_return_order_id = fields.Many2one(
        "purchase.return.order",
        "Purchase Return Order",
        related="purchase_return_line_id.order_id",
        copy=False,
        readonly=True,
    )

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'purchase_line_id' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values["purchase_return_line_id"] = self.purchase_line_id.id
        return

    def _get_computed_account(self):
        account = super(AccountMoveLine, self)._get_computed_account()
        if self.purchase_return_line_id:
            fiscal_position = self.move_id.fiscal_position_id
            accounts = self.product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=fiscal_position
            )
            return accounts["vendor_returns"]
        return account
