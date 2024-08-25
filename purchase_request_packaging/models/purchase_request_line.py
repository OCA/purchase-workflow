# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import FALSE_DOMAIN
from odoo.tools import float_compare, float_round


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    product_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Packaging",
        check_company=True,
        compute="_compute_product_packaging_id",
        store=True,
        readonly=False,
    )
    product_packaging_id_domain = fields.Binary(
        compute="_compute_product_packaging_id_domain"
    )
    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute="_compute_product_packaging_qty",
        store=True,
        readonly=False,
    )

    @api.depends("product_id", "product_qty", "product_uom_id")
    def _compute_product_packaging_id(self):
        for rec in self:
            product = rec.product_id
            qty = rec.product_qty
            uom = rec.product_uom_id
            if rec.product_packaging_id.product_id != product:
                rec.product_packaging_id = False
            if product and qty and uom:
                suggested_packaging = rec._suggest_product_packaging()
                rec.product_packaging_id = (
                    suggested_packaging or rec.product_packaging_id
                )

    @api.depends(
        "product_id",
    )
    def _compute_product_packaging_id_domain(self):
        for rec in self:
            product = rec.product_id
            if product:
                domain = [
                    ("purchase", "=", True),
                    ("product_id", "=", product.id),
                    "|",
                    ("company_id", "=", rec.company_id.id),
                    ("company_id", "=", False),
                ]
            else:
                domain = FALSE_DOMAIN
            rec.product_packaging_id_domain = domain

    @api.depends("product_packaging_id", "product_qty", "product_uom_id")
    def _compute_product_packaging_qty(self):
        for rec in self:
            qty = rec.product_qty
            packaging = rec.product_packaging_id
            if not packaging:
                rec.product_packaging_qty = 0
            else:
                packaging_uom = packaging.product_uom_id
                packaging_uom_qty = rec.product_uom_id._compute_quantity(
                    qty, packaging_uom
                )
                rec.product_packaging_qty = float_round(
                    packaging_uom_qty / packaging.qty,
                    precision_rounding=packaging_uom.rounding,
                )

    @api.constrains(
        "product_id",
        "product_packaging_id",
    )
    def _check_product_packaging_id(self):
        for rec in self:
            packaging = rec.product_packaging_id
            product = rec.product_id
            if not packaging or not product:
                continue
            if packaging.product_id != product:
                raise ValidationError(
                    _(
                        "Selected packaging (%(packaging)s) is not "
                        "linked to current product %(product)s",
                        packaging=rec.display_name,
                        product=product.display_name,
                    )
                )

    @api.onchange("product_packaging_qty")
    def _onchange_product_packaging_qty_load_product_qty(self):
        packaging = self.product_packaging_id
        if not packaging:
            return
        packaging_uom = packaging.product_uom_id
        uom = self.product_uom_id
        qty_per_packaging = packaging.qty
        product_qty = packaging_uom._compute_quantity(
            self.product_packaging_qty * qty_per_packaging, uom
        )
        if (
            float_compare(
                product_qty,
                self.product_qty,
                precision_rounding=uom.rounding,
            )
            != 0
        ):
            self.product_qty = product_qty

    def _suggest_product_packaging(self):
        self.ensure_one()
        product = self.product_id
        qty = self.product_qty
        uom = self.product_uom_id
        suggested_packaging = product.packaging_ids.filtered(
            lambda p: p.purchase
            and (p.product_id.company_id <= p.company_id <= self.company_id)
        )._find_suitable_product_packaging(qty, uom)
        return suggested_packaging
