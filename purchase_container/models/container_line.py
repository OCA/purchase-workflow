from odoo import api, fields, models


class ContainerLine(models.Model):
    """Track individual products/quantities within a container."""

    _name = "container.line"
    _description = "Container Line"
    _order = "container_id, sequence, id"

    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain=[("purchase_ok", "=", True)],
    )
    product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id", string="Product Template", store=True
    )
    hs_code = fields.Char(
        related="product_tmpl_id.hs_code",
        string="HTS Code",
        store=True,
        help="Harmonized Tariff Schedule code for customs classification",
    )
    description = fields.Text()
    quantity = fields.Float(
        digits="Product Unit of Measure",
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id", string="UoM Category"
    )

    # Carton/package information
    carton_qty = fields.Integer(
        string="Cartons",
        help="Number of cartons/packages for this line",
    )
    units_per_carton = fields.Float(
        string="Units/Carton",
        help="Number of units per carton",
    )

    # Weight and volume
    weight = fields.Float(
        digits="Stock Weight",
        help="Total weight for this line",
    )
    volume = fields.Float(
        digits="Volume",
        help="Total volume for this line (CBM)",
    )

    # Purchase order reference
    purchase_line_id = fields.Many2one(
        "purchase.order.line",
        string="Purchase Order Line",
        help="Link to the original purchase order line",
    )
    purchase_order_id = fields.Many2one(
        related="purchase_line_id.order_id", string="Purchase Order", store=True
    )

    # Landed cost allocation
    landed_cost = fields.Monetary(
        currency_field="currency_id",
        help="Allocated landed cost for this line",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Set default values from product."""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_po_id or self.product_id.uom_id
            self.description = self.product_id.display_name

    @api.onchange("carton_qty", "units_per_carton")
    def _onchange_carton_info(self):
        """Auto-calculate quantity from carton information."""
        if self.carton_qty and self.units_per_carton:
            self.quantity = self.carton_qty * self.units_per_carton

    def name_get(self):
        result = []
        for line in self:
            name = f"{line.container_id.code}: {line.product_id.display_name}"
            if line.quantity:
                name += f" ({line.quantity} {line.product_uom_id.name or ''})"
            result.append((line.id, name))
        return result
