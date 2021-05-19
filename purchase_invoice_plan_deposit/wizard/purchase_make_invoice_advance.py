# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"

    def _create_invoice(self, order, po_line, amount):
        invoice = super()._create_invoice(order, po_line, amount)
        invoice_plan_id = self._context.get("invoice_plan_id")
        if invoice_plan_id:
            plan = self.env["purchase.invoice.plan"].browse(invoice_plan_id)
            plan.invoice_ids += invoice
            invoice.write(
                {
                    "date": plan.plan_date,
                    "invoice_date": plan.plan_date,
                }
            )
        return invoice

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Default advance amount from installment 0
        order = self.env["purchase.order"].browse(self.env.context.get("active_id"))
        if order.use_invoice_plan:
            advance = order.invoice_plan_ids.filtered(lambda l: l.installment == 0)
            if advance:
                res["amount"] = advance[:1].percent
        return res

    def create_invoices(self):
        order = self.env["purchase.order"].browse(self.env.context.get("active_id"))
        if order.use_invoice_plan:
            plan_advance = order.invoice_plan_ids.filtered(lambda l: l.installment == 0)
            if plan_advance:
                return super(
                    PurchaseAdvancePaymentInv,
                    self.with_context(invoice_plan_id=plan_advance.id),
                ).create_invoices()
        return super(PurchaseAdvancePaymentInv, self).create_invoices()
