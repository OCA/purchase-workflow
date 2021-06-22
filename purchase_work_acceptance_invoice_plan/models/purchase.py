# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_qty(self):
        installment_id = self.env.context.get("installment_id", False)
        wa_qty_line_ids = self.env.context.get("wa_qty_line_ids", [])
        if installment_id:
            if wa_qty_line_ids:
                qty = self.env["select.work.acceptance.invoice.plan.qty"].search(
                    [("id", "in", wa_qty_line_ids), ("order_line_id", "=", self.id)]
                )
                return qty[:1].quantity
            else:
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

    def _no_edit(self):
        no_edit = super()._no_edit()
        return no_edit or self.env["work.acceptance"].search_count(
            [
                ("installment_id", "=", self.id),
            ]
        )

    def _compute_new_invoice_quantity(self, invoice_move):
        if self.env.context.get("wa_id"):
            return
        return super()._compute_new_invoice_quantity(invoice_move)
