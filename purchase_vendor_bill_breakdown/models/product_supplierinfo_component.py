from odoo import api, fields, models


class ProductSupplierInfoComponent(models.Model):
    _inherit = "product.supplierinfo.component"

    current_price = fields.Float(
        compute="_compute_current_price",
        store=True,
        string="Current price",
    )
    price_total = fields.Float(
        compute="_compute_price_total",
        store=True,
    )

    @api.depends("product_uom_qty", "current_price")
    def _compute_price_total(self):
        """Compute component price total"""
        for rec in self:
            rec.price_total = rec.current_price * rec.product_uom_qty

    @api.model
    def get_supplier_by_args(self, product_id, partner_id):
        """Get first supplier by product and vendor name"""
        return self.env["product.supplierinfo"].search(
            [("product_tmpl_id", "=", product_id), ("name", "=", partner_id)], limit=1
        )

    @api.depends("component_id", "component_id.seller_ids")
    def _compute_current_price(self):
        """Compute component price by Product Supplier or take standard_price"""
        for rec in self:
            price = (
                self.get_supplier_by_args(
                    rec.component_id.product_tmpl_id.id, rec.supplierinfo_id.name.id
                ).price
                or rec.component_id.standard_price
            )
            rec.update({"current_price": price})
