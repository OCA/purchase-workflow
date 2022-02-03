# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLineInvoiceWizard(models.TransientModel):
    _name = "purchase.order.line.invoice.wizard"
    _description = "Purchase Order Line Invoice Wizard"

    purchase_order_line_details_ids = fields.One2many(
        comodel_name="purchase.order.line.invoice.details", inverse_name="wizard_id"
    )

    @api.model
    def _check_unique_partner(self, lines):
        partner = lines.mapped("partner_id")
        if len(partner) != 1:
            raise UserError(_("""You have to select line from only one supplier."""))

    def _prepare_default_line_vals(self, purchase_line):
        return {
            "purchase_order_line_id": purchase_line.id,
            "order_id": purchase_line.order_id.id,
            "product_id": purchase_line.product_id.id,
            "name": purchase_line.name,
            "price_unit": purchase_line.price_unit,
            "product_qty": purchase_line.product_qty,
            "price_subtotal": purchase_line.price_subtotal,
            "qty_received": purchase_line.qty_received,
            "qty_invoiced": purchase_line.qty_invoiced,
            "currency_id": purchase_line.currency_id.id,
            "invoice_qty": max(
                purchase_line.qty_received - purchase_line.qty_invoiced, 0
            ),
        }

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        domain = [("id", "in", self.env.context.get("active_ids", []))]
        purchase_lines = self.env["purchase.order.line"].search(domain)
        if not purchase_lines:
            raise UserError(_("Please select a least one line to invoice."))
        details = []
        self._check_unique_partner(purchase_lines)
        for line in purchase_lines:
            vals = self._prepare_default_line_vals(line)
            details.append((0, 0, vals))
        if details:
            result["purchase_order_line_details_ids"] = details
        return result

    def create_invoice(self):
        self.ensure_one()
        invoice_lines_data = []
        purchase_order = self.purchase_order_line_details_ids.mapped(
            "purchase_order_line_id.order_id"
        )
        invoice_data = {
            "partner_id": purchase_order[0].partner_id.id,
            "move_type": "in_invoice",
            "invoice_origin": ",".join(purchase_order.mapped("name")),
            "fiscal_position_id": purchase_order[
                0
            ].partner_id.property_account_position_id,
        }
        journal_domain = [
            ("type", "=", "purchase"),
            ("company_id", "=", purchase_order[0].company_id.id),
            ("currency_id", "=", purchase_order[0].currency_id.id),
        ]
        default_journal_id = self.env["account.journal"].search(journal_domain, limit=1)
        if default_journal_id:
            invoice_data["journal_id"] = default_journal_id.id
        invoice = (
            self.env["account.move"]
            .with_context(default_move_type="in_invoice")
            .create(invoice_data)
        )
        for line in self.purchase_order_line_details_ids:
            purchase_order_line = line.purchase_order_line_id
            invoice_lines_data.append(
                (0, 0, purchase_order_line._prepare_account_move_line())
            )
        invoice.write({"invoice_line_ids": invoice_lines_data})
        return purchase_order.action_view_invoice(invoice)
