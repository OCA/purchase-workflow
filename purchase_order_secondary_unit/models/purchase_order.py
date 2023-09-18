# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "product.secondary.unit.mixin"]
    _name = "purchase.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom",
    }
    _product_uom_field = "uom_po_id"

    product_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_qty", copy=True
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_qty(self):
        if hasattr(super(), "_compute_product_qty"):
            return super()._compute_product_qty()
        return self._compute_helper_target_field_qty()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_id")
    def onchange_product_id(self):
        """If default purchases secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super().onchange_product_id()
        # Check to avoid executing onchange unnecessarily,
        # which can sometimes cause tests of other modules to fail
        if self.secondary_uom_id != self.product_id.purchase_secondary_uom_id:
            self.secondary_uom_id = self.product_id.purchase_secondary_uom_id
        if self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
        return res
