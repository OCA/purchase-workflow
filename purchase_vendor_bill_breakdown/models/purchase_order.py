from odoo import _, api, fields, models
from odoo.tools.float_utils import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    use_product_components = fields.Boolean()

    @api.onchange("partner_id")
    def set_partner_use_product_components(self):
        """Set 'Use Product Components' based on product settings"""
        if self.partner_id:
            self.use_product_components = self.partner_id.use_product_components

    def _prepare_invoice(self):
        # Prepare invoice values components based
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        for line in self.order_line.filtered(lambda l: l._has_components()):
            invoice_lines = line._prepare_component_account_move_line()
            invoice_vals["invoice_line_ids"].extend(invoice_lines)
        return invoice_vals

    @api.depends("state", "order_line.qty_to_invoice")
    def _get_invoiced(self):
        super(PurchaseOrder, self)._get_invoiced()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self.filtered(
            lambda o: o.invoice_ids and o.use_product_components
        ):
            if all(
                order.order_line.filtered(lambda l: not l.display_type).mapped(
                    lambda l: float_is_zero(
                        l.qty_invoiced - l.qty_received, precision_digits=precision
                    )
                )
            ):
                order.invoice_status = "invoiced"

    def write(self, vals):
        use_product_components = vals.get("use_product_components")
        result = super(PurchaseOrder, self).write(vals)
        # Disable components activation after product receiving
        if use_product_components and self.mapped("invoice_ids"):
            raise models.UserError(
                _(
                    "You can not activate Product Components "
                    "if the Order has an invoice for any product."
                )
            )
        elif use_product_components:
            # Update components if set use_product_components
            for line in self.mapped("order_line"):
                line._update_purchase_order_line_components()
        return result
