from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _name = "product.supplierinfo.component"
    _description = "Supplierinfo Product Component"

    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Supplier Info"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="supplierinfo_id.name"
    )
    invalid_component_ids = fields.Many2many(
        comodel_name="product.product",
    )
    component_id = fields.Many2one(
        comodel_name="product.product",
        string="Component",
        required=True,
    )
    component_uom_category_id = fields.Many2one(
        related="component_id.uom_id.category_id"
    )
    current_price = fields.Float(
        compute="_compute_current_price",
        store=True,
        string="Current price",
        readonly=True,
    )
    product_uom_qty = fields.Float(
        string="Qty per Unit",
        default=1.0,
        required=True,
        readonly=False,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', component_uom_category_id)]",
        required=True,
    )
    price_total = fields.Float(
        compute="_compute_price_total",
        store=True,
    )

    @api.depends("product_uom_qty", "current_price")
    def _compute_price_total(self):
        for rec in self:
            rec.price_total = rec.current_price * rec.product_uom_qty

    @api.depends("component_id")
    def _compute_current_price(self):
        """Compute component price by Product Supplier or take standard_price"""
        for rec in self:
            supplier_id = rec.component_id.seller_ids.filtered(
                lambda s: s.name == rec.supplierinfo_id.name
            )
            rec.write(
                {
                    "current_price": supplier_id[0].price
                    if supplier_id
                    else rec.component_id.standard_price,
                }
            )

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value at component onchange"""
        if self.component_id:
            return
        parent_component = self.supplierinfo_id.product_variant_ids
        components = self.supplierinfo_id.component_ids.mapped("component_id")
        self.write(
            {
                "product_uom_qty": 1.0,
                "product_uom_id": self.component_id.uom_po_id
                or self.component_id.uom_id,
                "invalid_component_ids": parent_component | components,
            }
        )
