from odoo import api, fields, models


class PurchaseOrderLineComponent(models.Model):
    _name = "purchase.order.line.component"
    _description = "Purchase Order Line Component"

    line_id = fields.Many2one(
        "purchase.order.line", string="Purchase Order Line", reuired=True
    )
    component_id = fields.Many2one("product.product", string="Component", required=True)
    component_uom_category_id = fields.Many2one(
        related="component_id.uom_id.category_id"
    )
    product_uom_qty = fields.Float(string="Qty/unit", default=1.0, required=True)
    total_qty = fields.Float(string="Total Qty", required=True)
    qty_invoiced = fields.Float(
        string="Billed Qty",
        compute="_compute_qty_invoiced",
        store=True,
        readonly=1,
    )
    qty_to_invoice = fields.Float(
        compute="_compute_qty_invoiced",
        string="To Invoice Quantity",
        store=True,
        readonly=True,
        digits="Component Unit of Measure",
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', component_uom_category_id)]",
        required=True,
    )

    price_unit = fields.Float(
        stirng="Unit Price",
        required=True,
        digits="Component Price",
    )
    price_subtotal = fields.Monetary(
        compute="_compute_price_subtotal", string="Subtotal", store=True
    )
    currency_id = fields.Many2one(
        related="line_id.order_id.currency_id",
        store=True,
        string="Currency",
        readonly=True,
    )

    def _update_qty(self, qty_received):
        """
        Update Total Quantity based on Quantity Received
        :param qty_received: Quantity Received
        :return None
        """
        for rec in self:
            rec.total_qty = rec.qty_invoiced + rec.product_uom_qty * qty_received

    @api.depends("total_qty", "price_unit", "line_id.taxes_id")
    def _compute_price_subtotal(self):
        """Compute subtotal value"""
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.line_id.taxes_id.compute_all(
                vals["price_unit"],
                vals["currency_id"],
                vals["product_qty"],
                vals["product"],
                vals["partner"],
            )
            line.update(
                {
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            "price_unit": self.price_unit,
            "currency_id": self.line_id.order_id.currency_id,
            "product_qty": self.total_qty,
            "product": self.component_id,
            "partner": self.line_id.order_id.partner_id,
        }

    @api.depends(
        "line_id.invoice_lines.move_id.state",
        "line_id.invoice_lines.quantity",
        "line_id.qty_received",
        "product_uom_qty",
        "total_qty",
        "line_id.order_id.state",
    )
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.line_id.invoice_lines.filtered(
                lambda l: l.product_id == line.component_id
            ):
                if inv_line.move_id.state not in ["cancel"]:
                    if inv_line.move_id.move_type == "in_invoice":
                        qty += inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom_id
                        )
                    elif inv_line.move_id.move_type == "in_refund":
                        qty -= inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom_id
                        )
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.line_id.order_id.state in ["purchase", "done"]:
                line.qty_to_invoice = line.total_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value at component onchange"""
        if not self.component_id:
            return
        self.write(
            {
                "product_uom_qty": 1,
                "product_uom_id": self.component_id.uom_po_id
                or self.component_id.uom_id,
                "price_unit": self.component_id.standard_price,
            }
        )

    @api.model
    def create(self, vals):
        # set default unit price
        component_id = vals.get("component_id", False)
        if not vals.get("price_unit", False) and component_id:
            component = self.env["product.product"].search([("id", "=", component_id)])
            if len(component) == 1:
                vals.update(price_unit=component.standard_price)
        return super(PurchaseOrderLineComponent, self).create(vals)
