# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_supplier_info(self, partner, line, price, currency):
        vals = super()._prepare_supplier_info(partner, line, price, currency)
        vals["secondary_uom_id"] = line.secondary_uom_id.id
        return vals


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "product.secondary.unit.mixin"]
    _name = "purchase.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom",
    }
    _product_uom_field = "uom_po_id"

    product_qty = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_product_qty",
        copy=True,
        precompute=True,
    )
    product_packaging_qty = fields.Float(
        compute="_compute_product_packaging_qty", store=True, precompute=True
    )
    product_packaging_id = fields.Many2one(
        compute="_compute_product_packaging_id", store=True, precompute=True
    )
    secondary_uom_price = fields.Float(
        string="Secondary Price",
        digits="Product Price",
        aggregator="avg",
        compute="_compute_secondary_uom_price",
        inverse="_inverse_secondary_uom_price",
        store=True,
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_qty(self):
        self._compute_helper_target_field_qty()
        return super()._compute_product_qty()

    @api.depends("price_unit", "secondary_uom_id", "secondary_uom_id.factor")
    def _compute_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id:
                rec.secondary_uom_price = rec.price_unit * rec.secondary_uom_id.factor
            else:
                rec.secondary_uom_price = 0.0

    @api.onchange("secondary_uom_price")
    def _inverse_secondary_uom_price(self):
        for rec in self:
            if rec.secondary_uom_id:
                rec.price_unit = rec.secondary_uom_price / rec.secondary_uom_id.factor

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
        product_sec_uom = (
            self.product_id.purchase_secondary_uom_id
            or self.product_id.product_tmpl_id.purchase_secondary_uom_id
        )
        if self.secondary_uom_id != product_sec_uom:
            self.secondary_uom_id = product_sec_uom
        if self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
        return res

    def _prepare_account_move_line(self, move=False):
        # Set secondary UoM values only when account_move_secondary_unit is installed
        # (i.e., the fields exist on account.move.line).
        res = super()._prepare_account_move_line(move)
        aml_fields = self.env["account.move.line"]._fields
        if "secondary_uom_id" in aml_fields and self.secondary_uom_id:
            res["secondary_uom_id"] = self.secondary_uom_id.id
        return res
