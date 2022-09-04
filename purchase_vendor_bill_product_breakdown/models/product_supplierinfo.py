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
    product_variant_ids = fields.One2many(related="product_tmpl_id.product_variant_ids")
    price = fields.Float(
        compute="_compute_price",
        inverse="_inverse_price",
        store=True,
    )
    price_manual = fields.Float(
        copy=False,
    )

    @api.onchange("price")
    def _inverse_price(self):
        for rec in self.filtered(lambda item: not item.component_ids):
            rec.price_manual = rec.price

    @api.depends("component_ids", "partner_bill_components")
    def _compute_price(self):
        for rec in self.filtered(
            lambda item: item.component_ids and item.partner_bill_components
        ):
            rec.price = sum(rec.component_ids.mapped("price_total"))

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
