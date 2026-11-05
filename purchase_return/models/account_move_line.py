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
    )

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'purchase_line_id' field as well.
        super()._copy_data_extend_business_fields(values)
        values["purchase_return_line_id"] = self.purchase_line_id.id
        return

    def _compute_account_id(self):
        # pylint: disable=missing-return
        super()._compute_account_id()
        product_lines = self.filtered(
            lambda line: line.display_type == "product"
            and line.move_id.is_invoice(True)
        )
        for line in product_lines:
            if line.purchase_return_line_id:
                fiscal_position = line.move_id.fiscal_position_id
                accounts = line.with_company(
                    line.company_id
                ).product_id.product_tmpl_id.get_product_accounts(
                    fiscal_pos=fiscal_position
                )
                line.account_id = accounts["vendor_returns"]
