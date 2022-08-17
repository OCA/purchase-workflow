from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    bill_components = fields.Boolean(related="order_id.bill_components")
    component_ids = fields.One2many("purchase.order.line.component", "line_id")
    last_qty_invoiced = fields.Float(
        compute="_compute_last_qty_invoiced",
        string="Billed Qty",
        store=True,
    )

    def get_supplier(self):
        """Get supplier info by purchase orders vendor"""
        partner_id = self.order_id.partner_id.id
        suppliers = self.product_id.seller_ids.filtered(
            lambda seller: seller.name.id == partner_id
        )
        return suppliers[0] if len(suppliers) > 0 else False

    def _update_purchase_order_line_components(self):
        """
        Updates purchase order line components based on supplierinfo
        :return None
        """
        supplierinfo = self.get_supplier()
        if not supplierinfo:
            return False
        self.component_ids.unlink()
        self.write(
            {
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "line_id": self.id,
                            "component_id": component.component_id.id,
                            "product_uom_qty": component.product_uom_qty,
                            "total_qty": 0,
                            "product_uom_id": component.product_uom_id.id,
                        },
                    )
                    for component in supplierinfo.component_ids
                ]
            }
        )

    def _has_components(self):
        return len(self.component_ids) > 0 and self.bill_components

    @api.model
    def create(self, vals):
        result = super(PurchaseOrderLine, self).create(vals)
        # Create components for product
        result._update_purchase_order_line_components()
        return result

    def write(self, vals):
        qty_received = vals.get("qty_received", False)
        result = super(PurchaseOrderLine, self).write(vals)
        for rec in self:
            # update product components qty
            if qty_received and rec._has_components():
                rec.component_ids._update_qty(rec.qty_received - rec.last_qty_invoiced)
            # update components at change product_id
            product_id = vals.get("product_id", False)
            if product_id and rec.bill_components:
                rec._update_purchase_order_line_components()
        return result

    def action_open_component_view(self):
        """Open view with product components"""
        self.ensure_one()
        view_id = self.env.ref(
            "purchase_vendor_bill_product_breakdown.purchase_order_line_components_form_view"
        ).id
        self.get_supplier()
        return {
            "name": _("Product Components"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "views": [(view_id, "form")],
            "view_id": view_id,
            "target": "new",
        }

    def _prepare_component_account_move_line(self):
        """Prepare account move lines for components"""
        self.ensure_one()
        lines = []
        for component in self.component_ids:
            if component.qty_to_invoice != 0:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "display_type": self.display_type,
                            "sequence": self.sequence,
                            "name": "%s: %s"
                            % (self.order_id.name, component.component_id.name),
                            "product_id": component.component_id.id,
                            "product_uom_id": component.product_uom_id.id,
                            "quantity": component.qty_to_invoice,
                            "component_qty": self.qty_received - self.last_qty_invoiced,
                            "price_unit": self.currency_id._convert(
                                component.price_unit,
                                self.currency_id,
                                self.company_id,
                                fields.Date.today(),
                                round=False,
                            ),
                            "tax_ids": [(6, 0, self.taxes_id.ids)],
                            "analytic_account_id": self.account_analytic_id.id,
                            "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
                            "purchase_line_id": self.id,
                        },
                    )
                )
        return lines

    def _prepare_account_move_line(self, move=False):
        """Mark lines to skip"""
        result = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        if self._has_components():
            result["skip_record"] = True
        return result

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "qty_received",
        "product_uom_qty",
        "order_id.state",
    )
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self:
            if line._has_components():
                line.qty_invoiced = line.last_qty_invoiced

    @api.model
    def _compute_invoice_qty(self, component_qty, invoice_count):
        index = 0
        count_components = len(component_qty)
        invoice_qty = 0.0
        iter_index = int(count_components / invoice_count)
        while index != count_components:
            invoice_qty += sum(set(component_qty[index : index + iter_index]))
            index += iter_index
        return invoice_qty

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
    )
    def _compute_last_qty_invoiced(self):
        for line in self:
            if not line._has_components():
                continue
            invoice_lines = line.invoice_lines.filtered(
                lambda l: l.product_id in line.component_ids.mapped("component_id")
            )
            move_count = len(invoice_lines.mapped("move_id"))
            invoice_qty = (
                0
                if move_count == 0
                else self._compute_invoice_qty(
                    invoice_lines.mapped("component_qty"),
                    move_count,
                )
            )
            # invoice_qty = sum(set(invoice_lines.mapped("component_qty")))
            invoice_move_type = set(invoice_lines.mapped("move_id").mapped("move_type"))
            line.last_qty_invoiced = (
                invoice_qty
                if "in_refund" not in invoice_move_type
                else invoice_qty * -1
            )
