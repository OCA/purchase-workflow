# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def action_create_invoice(self):
        if (
            self.env.company.purchase_invoice_create_security
            and not self.user_has_groups(
                "purchase_invoice_create_security_group.group_purchase_invoice_create"
            )
        ):
            raise AccessError(
                _(
                    "You don't have rights to create invoices from purchase"
                    " order! Please ask access to administrator."
                )
            )
        return super().action_create_invoice()
