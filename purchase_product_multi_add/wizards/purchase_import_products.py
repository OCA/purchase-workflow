# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseImportProducts(models.TransientModel):
    _name = "purchase.import.products"
    _description = "Purchase Import Products"

    products = fields.Many2many(comodel_name="product.product")
    items = fields.One2many(
        comodel_name="purchase.import.products.items",
        inverse_name="wizard_id",
        ondelete="cascade",
    )

    def create_items(self):
        for wizard in self:
            for product in wizard.products:
                self.env["purchase.import.products.items"].create(
                    {"wizard_id": wizard.id, "product_id": product.id}
                )
        view = self.env.ref(
            "purchase_product_multi_add.view_import_product_to_purchase2"
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_type": "form",
            "view_mode": "form",
            "views": [(view.id, "form")],
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    @api.model
    def _get_line_values(self, purchase, item):
        purchase_line = self.env["purchase.order.line"].new(
            {
                "order_id": purchase.id,
                "name": item.product_id.name,
                "product_id": item.product_id.id,
                "product_qty": item.quantity,
                "product_uom": item.product_id.uom_id.id,
            }
        )
        purchase_line.onchange_product_id()
        # Set qty after onchange because onchange reset it anyway
        purchase_line.product_qty = item.quantity
        line_values = purchase_line._convert_to_write(purchase_line._cache)
        return line_values

    def select_products(self):
        po_obj = self.env["purchase.order"]
        for wizard in self:
            purchase = po_obj.browse(self.env.context.get("active_id", False))

            if purchase:
                for item in wizard.items:
                    vals = self._get_line_values(purchase, item)
                    if vals:
                        self.env["purchase.order.line"].create(vals)

        return {"type": "ir.actions.act_window_close"}


class PurchaseImportProductsItem(models.TransientModel):
    _name = "purchase.import.products.items"
    _description = "Purchase Import Products Items"

    wizard_id = fields.Many2one(
        string="Wizard", comodel_name="purchase.import.products"
    )
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", required=True
    )
    quantity = fields.Float(
        digits="Product Unit of Measure", default=1.0, required=True
    )
