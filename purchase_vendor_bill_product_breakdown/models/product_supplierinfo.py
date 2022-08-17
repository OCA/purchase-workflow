from odoo import _, api, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    product_bill_components = fields.Boolean(related="product_tmpl_id.bill_components")
    partner_bill_components = bill_components = fields.Boolean(
        related="name.bill_components"
    )
    component_ids = fields.One2many(
        comodel_name="product.supplierinfo.component", inverse_name="supplierinfo_id"
    )
    product_variant_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_product_variant_ids",
        store=True,
    )
    price = fields.Float(compute="_compute_price", store=True, readonly=True)

    @api.depends("component_ids", "partner_bill_components")
    def _compute_price(self):
        for rec in self.filtered(
            lambda item: item.component_ids and item.partner_bill_components
        ):
            rec.price = sum(rec.component_ids.mapped("price_total"))

    @api.depends("product_tmpl_id", "product_tmpl_id.product_variant_ids")
    def _compute_product_variant_ids(self):
        for rec in self:
            rec.product_variant_ids = rec.product_tmpl_id.product_variant_ids

    def action_open_component_view(self):
        """Open product components view"""
        self.ensure_one()
        view_id = self.env.ref(
            "purchase_vendor_bill_product_breakdown.product_supplierinfo_component_form_view"
        ).id
        return {
            "name": _("Product Components"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.supplierinfo",
            "res_id": self.id,
            "views": [(view_id, "form")],
            "view_id": view_id,
            "target": "new",
        }
