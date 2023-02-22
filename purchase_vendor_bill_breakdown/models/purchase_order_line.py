from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    use_product_components = fields.Boolean(related="order_id.use_product_components")
    component_ids = fields.One2many(
        comodel_name="purchase.order.line.component",
        inverse_name="line_id",
        ondelete="cascade",
    )
    last_qty_invoiced = fields.Float(
        compute="_compute_last_qty_invoiced",
        string="Billed Qty",
        store=True,
    )
    supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo", compute="_compute_supplier_id", store=True
    )
    show_breakdown = fields.Boolean(compute="_compute_show_breakdown")

    def _compute_show_breakdown(self):
        """Compute show/hide the product breakdown button"""
        for rec in self:
            rec.show_breakdown = (
                rec.supplier_id.product_use_components
                and rec.supplier_id.partner_use_components
                and rec.use_product_components
            )

    @api.constrains("component_ids")
    def check_component_ids(self):
        """Checking a component for uniqueness"""
        for rec in self:
            components = rec.component_ids.mapped("component_id")
            if rec.supplier_id.product_variant_ids & components:
                raise models.ValidationError(
                    _("Components must not contain parent products!")
                )
            grouped_data = self.env["purchase.order.line.component"].read_group(
                domain=[("line_id", "=", rec.id)],
                fields=["component_id"],
                groupby=["component_id"],
            )
            if list(filter(lambda c: c.get("component_id_count") > 1, grouped_data)):
                raise models.ValidationError(_("Components must be unique!"))

    @api.depends(
        "order_id", "product_id", "order_id.partner_id", "product_id.seller_ids"
    )
    def _compute_supplier_id(self):
        """Compute supplierifo by product and vendor"""
        for rec in self:
            rec.supplier_id = self.env["product.supplierinfo"].search(
                [
                    ("product_tmpl_id", "=", rec.product_id.product_tmpl_id.id),
                    ("name", "=", rec.order_id.partner_id.id),
                ],
                limit=1,
            )

    def _update_purchase_order_line_components(self):
        """Updates purchase order line components based on supplierinfo"""
        if self.supplier_id:
            self.component_ids.unlink()
            components = self.supplier_id.component_ids
            if self.env.user.has_group("product.group_product_variant"):
                components = self.env[
                    "product.supplierinfo.component"
                ]._get_component_by_product_variant(components)
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
                        for component in components
                    ],
                }
            )

    def _has_components(self):
        """
        Checking Order line has component and activated 'Use Product Component'
        :return: bool
        """
        return self.component_ids and self.use_product_components

    @api.model
    def create(self, vals):
        result = super(PurchaseOrderLine, self).create(vals)
        # Create components for product
        if result.use_product_components:
            result._update_purchase_order_line_components()
        return result

    def write(self, vals):
        qty_received = vals.get("qty_received")
        product_id = vals.get("product_id")
        result = super(PurchaseOrderLine, self).write(vals)
        if not (qty_received or product_id):
            return result
        for rec in self.filtered(lambda r: r._has_components()):
            # update product components qty
            if qty_received:
                rec.component_ids._update_qty(rec.qty_received - rec.last_qty_invoiced)
            # update components at change product_id
            if product_id:
                rec._update_purchase_order_line_components()
        return result

    def action_open_component_view(self):
        """Open view with product components"""
        self.ensure_one()
        if not self.use_product_components:
            raise models.UserError(
                _("You need to activate 'Use Product Component' to use it.")
            )
        view = self.env.ref(
            "purchase_vendor_bill_breakdown.purchase_order_line_components_form_view"
        )
        return {
            "name": _("Product Components"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "view_id": view.id,
            "target": "new",
        }

    def _prepare_component_account_move_line(self):
        """Prepare account move lines for components"""
        self.ensure_one()
        return [
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
            for component in self.component_ids.filtered(
                lambda c: c.qty_to_invoice != 0
            )
        ]

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
        lines = self.filtered(lambda l: l._has_components() and l.invoice_lines)
        super(PurchaseOrderLine, self - lines)._compute_qty_invoiced()
        # Compute qty_invoiced for product with components
        for line in lines:
            line.qty_invoiced = line.last_qty_invoiced

    @api.model
    def _compute_invoiced_qty(self, component_qty, invoice_count):
        """Compute invoiced qty by components qty in invoice"""
        invoice_qty = 0.0
        if invoice_count:
            index, count_components = 0, len(component_qty)
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
        """Compute invoiced qty for the product with components"""
        for line in self.filtered(lambda l: l._has_components()):
            invoice_lines = line.invoice_lines.filtered(
                lambda l: l.product_id in line.component_ids.mapped("component_id")
            )
            move_ids = invoice_lines.mapped("move_id")
            invoice_qty = self._compute_invoiced_qty(
                invoice_lines.mapped("component_qty"), len(move_ids)
            )
            if "in_refund" in move_ids.mapped("move_type"):
                invoice_qty *= -1
            line.last_qty_invoiced = invoice_qty

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        super(PurchaseOrderLine, self)._onchange_quantity()
        if (
            not self.product_id
            or self.invoice_lines
            or not self.env.user.has_group("product.group_product_variant")
        ):
            return
        # Compute unit price by product variant components
        params = {"order_id": self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params,
        )
        price = sum(
            self._get_component_by_product_variant(seller.component_ids).mapped(
                "price_total"
            )
        )
        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and self.order_id.currency_id
            and seller.currency_id != self.order_id.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                self.order_id.currency_id,
                self.order_id.company_id,
                self.date_order or fields.Date.today(),
            )

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit
