from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _name = "product.supplierinfo.component"
    _description = "Supplierinfo Product Component"

    supplierinfo_id = fields.Many2one(
        "product.supplierinfo", string="Supplier Info", required=True
    )
    partner_id = fields.Many2one("res.partner", related="supplierinfo_id.name")
    component_id = fields.Many2one("product.product", string="Component", required=True)
    component_uom_category_id = fields.Many2one(
        related="component_id.uom_id.category_id"
    )
    product_uom_qty = fields.Float(string="Qty per Unit", default=1, required=True)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit od Measure",
        domain="[('category_id', '=', component_uom_category_id)]",
        required=True,
    )

    @api.onchange("component_id")
    def onchange_component_id(self):
        """Set default value at component onchange"""
        if not self.component_id:
            return
        self.write(
            {
                "product_uom_qty": 1.0,
                "product_uom_id": self.component_id.uom_po_id
                or self.component_id.uom_id,
            }
        )
