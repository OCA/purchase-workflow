from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _name = "product.supplierinfo.component"
    _description = "Supplierinfo Product Component"

    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="Supplier Info"
    )
    parent_product_ids = fields.One2many(related="supplierinfo_id.product_variant_ids")
    partner_id = fields.Many2one(related="supplierinfo_id.name")
    component_id = fields.Many2one(
        comodel_name="product.product",
        string="Component",
        required=True,
        domain="[('id', 'not in', parent_product_ids)]",
    )
    component_uom_category_id = fields.Many2one(
        related="component_id.uom_id.category_id"
    )
    product_uom_qty = fields.Float(
        string="Qty per Unit",
        default=1.0,
        required=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        domain=[("category_id", "=", component_uom_category_id)],
        required=True,
    )

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value on component onchange"""
        component = self.component_id
        self.update(
            {
                "product_uom_qty": 1.0,
                "product_uom_id": component.uom_po_id or component.uom_id,
            }
        )
