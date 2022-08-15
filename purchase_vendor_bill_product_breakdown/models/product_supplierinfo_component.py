from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _name = "product.supplierinfo.component"
    _description = "Supplierinfo Product Component"

    def get_component_domain(self):
        variant_ids = self._context.get("parent_product_ids", False)
        return [("id", "not in", variant_ids)] if variant_ids else []

    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Supplier Info"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", related="supplierinfo_id.name"
    )
    component_id = fields.Many2one(
        comodel_name="product.product",
        string="Component",
        domain=get_component_domain,
        required=True,
    )
    component_uom_category_id = fields.Many2one(
        related="component_id.uom_id.category_id"
    )
    component_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Select Pricelist", required=True
    )
    current_price = fields.Float(
        compute="_compute_current_price",
        store=True,
        string="Current price",
        readonly=True,
    )
    product_uom_qty = fields.Float(string="Qty per Unit", default=1.0, required=True)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', component_uom_category_id)]",
        required=True,
    )

    @api.model
    def default_get(self, fields):
        result = super(ProductSupplierInfoComponent, self).default_get(fields)
        supplierinfo_id = self._context.get("active_id", False)
        if supplierinfo_id:
            result.update(component_supplier_id=supplierinfo_id)
        return result

    @api.depends("component_id")
    def _compute_current_price(self):
        for rec in self:
            supplier_id = rec.component_id.seller_ids.filtered(
                lambda s: s.name == rec.component_supplier_id.name
            )
            rec.current_price = supplier_id.price or rec.component_id.standard_price

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value at component onchange"""
        if len(self.component_id) > 0:
            self.write(
                {
                    "product_uom_qty": 1.0,
                    "product_uom_id": self.component_id.uom_po_id
                    or self.component_id.uom_id,
                }
            )
