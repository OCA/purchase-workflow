# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = "purchase.create.invoice.plan"

    advance = fields.Boolean(
        string="Deposit on 1st Invoice",
        default=False,
    )
    advance_percent = fields.Float(
        string="Percent Deposit",
        default=1,
        required=True,
    )

    def purchase_create_invoice_plan(self):
        self = self.with_context(
            advance=self.advance, advance_percent=self.advance_percent
        )
        return super().purchase_create_invoice_plan()

    @api.constrains("num_installment")
    def _check_num_installment(self):
        if self.num_installment <= 1 and not self.advance:
            raise ValidationError(_("Number Installment must greater than 1"))
