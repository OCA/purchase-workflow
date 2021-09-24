from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_return_line_id = fields.Many2one(
        "purchase.return.order.line",
        "Purchase Return Order Line",
        ondelete="set null",
        index=True,
    )
    purchase_return_order_id = fields.Many2one(
        "purchase.return.order",
        "Purchase Return Order",
        related="purchase_return_line_id.order_id",
        readonly=True,
    )

    def _copy_data_extend_business_fields(self, values):
        # OVERRIDE to copy the 'purchase_line_id' field as well.
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        values["purchase_return_line_id"] = self.purchase_line_id.id
