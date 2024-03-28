# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = ["purchase.order", "supplied.product.mixin"]
    _name = "purchase.order"

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        invoice_vals["use_only_supplied_product"] = self.use_only_supplied_product
        return invoice_vals
