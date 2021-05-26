# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_qty(self):
        installment_id = self._context.get("installment_id", False)
        if installment_id:
            installment = self.env["purchase.invoice.plan"].browse(installment_id)
            return self.product_qty * (installment.percent / 100)
        return super()._get_product_qty()


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    "%s %s : %s -- %s %s"
                    % (
                        "Invoice Plan",
                        rec.installment,
                        rec.plan_date,
                        rec.percent,
                        "%",
                    ),
                )
            )
        return result
