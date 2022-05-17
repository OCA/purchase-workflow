from odoo import _, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    bill_components = fields.Boolean(related="name.bill_components")
    component_ids = fields.One2many("product.supplierinfo.component", "supplierinfo_id")

    def action_open_component_view(self):
        """Open view with product components"""
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
