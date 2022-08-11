from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _name = "product.supplierinfo.component"
    _description = "Supplierinfo Product Component"

    def get_component_domain(self):
        variant_ids = self._context.get("parent_product_ids", False)
        return [("id", "not in", variant_ids)] if variant_ids else []

    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Supplier Info", required=True
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
    valid_supplier_ids = fields.Many2many(
        comodel_name="product.supplierinfo",
        compute="_compute_valid_supplier_ids",
        store=True,
    )
    component_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Select Pricelist", required=True
    )
    price = fields.Float(string="Price", readonly=True)
    product_uom_qty = fields.Float(string="Qty per Unit", default=1, required=True)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', component_uom_category_id)]",
        required=True,
    )

    @api.depends("component_id")
    def _compute_valid_supplier_ids(self):
        for rec in self:
            rec.valid_supplier_ids = rec.component_id.seller_ids

    @api.onchange("component_supplier_id")
    def onchange_price(self):
        """Compute price by supplier"""
        for rec in self:
            rec.price = rec.component_supplier_id.price

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value at component onchange"""
        if len(self.component_id) > 0:
            self.write(
                {
                    "product_uom_qty": 1.0,
                    "product_uom_id": self.component_id.uom_po_id
                    or self.component_id.uom_id,
                    "component_supplier_id": self.env["product.supplierinfo"],
                    "price": 0.0,
                }
            )
