# © 2016 Chafique DELLI @ Akretion
# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = ["account.move", "supplied.product.mixin"]
    _name = "account.move"

    @api.onchange("invoice_vendor_bill_id")
    def _onchange_invoice_vendor_bill(self):
        if self.invoice_vendor_bill_id:
            self.use_only_supplied_product = (
                self.invoice_vendor_bill_id.use_only_supplied_product
            )
        return super()._onchange_invoice_vendor_bill()
