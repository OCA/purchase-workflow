from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    bill_components = fields.Boolean(
        string="Vendor Bill Breakdown",
    )

    @api.onchange("partner_id")
    def set_partner_bill_components(self):
        """Set "Bill components" based on partner settings"""
        for rec in self:
            rec.bill_components = rec.partner_id.bill_components

    def _prepare_invoice(self):
        # Prepare invoice values components based
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        for line in self.order_line:
            if line._has_components():
                invoice_vals["invoice_line_ids"].extend(
                    line._prepare_component_account_move_line()
                )
        return invoice_vals
