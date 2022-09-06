from odoo import _, api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    product_use_components = fields.Boolean(
        related="product_tmpl_id.use_product_components"
    )
    partner_use_components = fields.Boolean(related="name.use_product_components")
    component_ids = fields.One2many(
        comodel_name="product.supplierinfo.component", inverse_name="supplierinfo_id"
    )
    product_variant_ids = fields.One2many(related="product_tmpl_id.product_variant_ids")

    @api.constrains("component_ids")
    def check_component_ids(self):
        """Checking a component for uniqueness"""
        for supplier in self:
            components = supplier.component_ids.mapped("component_id")
            if supplier.product_variant_ids & components:
                raise models.ValidationError(
                    _("Components must not contain parent products!")
                )
            grouped_data = self.env["product.supplierinfo.component"].read_group(
                domain=[("supplierinfo_id", "=", supplier.id)],
                fields=["component_id"],
                groupby=["component_id"],
            )
            if list(filter(lambda c: c.get("component_id_count") > 1, grouped_data)):
                raise models.ValidationError(_("Components must be unique!"))

    def action_open_component_view(self):
        """Open product components view"""
        self.ensure_one()
        if not (self.product_use_components and self.partner_use_components):
            raise models.UserError(
                _(
                    "You need to activate 'Use Product Component' "
                    "in both Product and Vendor to use it."
                )
            )
        view = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_supplierinfo_component_form_view"  # noqa
        )
        return {
            "name": _("Product Components"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.supplierinfo",
            "res_id": self.id,
            "view_id": view.id,
            "target": "new",
        }
