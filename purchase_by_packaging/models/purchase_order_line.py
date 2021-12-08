# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _can_be_purchased_error_condition(self):
        self.ensure_one()
        return self.product_packaging and not self.product_packaging.can_be_purchased

    @api.constrains("product_packaging")
    def _check_product_packaging_can_be_purchased(self):
        for line in self:
            if line._can_be_purchased_error_condition():
                raise ValidationError(
                    _(
                        "Packaging %s on product %s must be set as 'Can be purchased'"
                        " in order to be used on a purchase order."
                    )
                    % (line.product_packaging.name, line.product_id.name)
                )

    @api.onchange("product_packaging")
    def _onchange_product_packaging(self):
        if self._can_be_purchased_error_condition():
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "This product packaging must be set as 'Can be purchased' in"
                        " order to be used on a purchase order."
                    ),
                },
            }
        return super()._onchange_product_packaging()

    @api.constrains(
        "product_id", "product_packaging", "product_packaging_qty", "product_qty"
    )
    def _check_product_packaging_purchase_only_by_packaging(self):
        for line in self:
            if not line.product_id.purchase_only_by_packaging:
                continue
            if (
                not line.product_packaging
                or float_compare(
                    line.product_packaging_qty,
                    0,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                <= 0
            ):
                raise ValidationError(
                    _(
                        "Product %s can only be purchased with a packaging and a "
                        "packaging quantity." % line.product_id.name
                    )
                )

    def _force_qty_with_package(self):
        """

        :return:
        """
        self.ensure_one()
        qty = self.product_id._convert_purchase_packaging_qty(
            self.product_qty,
            self.product_uom or self.product_id.uom_id,
            packaging=self.product_packaging,
        )
        self.product_qty = qty
        return True

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        self._force_packaging()
        self._force_qty_with_package()
        res = super()._onchange_quantity()
        return res

    def _get_product_packaging_having_multiple_qty(self, product, qty, uom):
        if uom != product.uom_id:
            qty = uom._compute_quantity(qty, product.uom_id)
        return product.get_first_purchase_packaging_with_multiple_qty(qty)

    def _inverse_product_packaging_qty(self):
        # Force skipping of auto assign
        # if we are writing the product_qty directly via inverse
        super(
            PurchaseOrderLine, self.with_context(_skip_auto_assign=True)
        )._inverse_product_packaging_qty()

    def _inverse_qty_delivered(self):
        # Force skipping of auto assign
        super(
            PurchaseOrderLine, self.with_context(_skip_auto_assign=True)
        )._inverse_qty_delivered()

    def write(self, vals):
        """Auto assign packaging if needed"""
        if vals.get("product_packaging") or self.env.context.get("_skip_auto_assign"):
            # setting the packaging directly, skip auto assign
            return super().write(vals)
        for line in self:
            line_vals = vals.copy()
            packaging = self._get_autoassigned_packaging(line_vals)
            if packaging:
                line_vals.update({"product_packaging": packaging})
            super(PurchaseOrderLine, line).write(line_vals)
        return True

    @api.model
    def create(self, vals):
        """Auto assign packaging if needed"""
        # Fill the packaging if they are empty and the quantity is a multiple
        if not vals.get("product_packaging"):
            packaging = self._get_autoassigned_packaging(vals)
            if packaging:
                vals.update({"product_packaging": packaging})
        return super().create(vals)

    def _get_autoassigned_packaging(self, vals=None):
        if not vals:
            vals = []
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if "product_id" in vals
            else self.product_id
        )
        if product and product.purchase_only_by_packaging:
            quantity = (
                vals["product_qty"] if "product_qty" in vals else self.product_qty
            )
            uom = (
                self.env["uom.uom"].browse(vals["product_uom"])
                if "product_uom" in vals
                else self.product_uom
            )
            packaging = self._get_product_packaging_having_multiple_qty(
                product, quantity, uom
            )
            if packaging:
                return packaging.id
        return None

    def _force_packaging(self):
        if not self.product_packaging and self.product_id.purchase_only_by_packaging:
            packaging_id = self._get_autoassigned_packaging()
            if packaging_id:
                self.product_packaging = packaging_id

    def _check_package(self):
        if self.product_packaging:
            rounded_up_qty = float_round(
                self.product_packaging_qty,
                precision_rounding=self.product_packaging.purchase_rounding,
                rounding_method="UP",
            )
            if self.product_packaging_qty != rounded_up_qty:
                self.product_packaging_qty = rounded_up_qty
                q = self.product_id.uom_id._compute_quantity(
                    self.product_packaging.actual_purchase_qty, self.product_uom
                )
                qty = self.product_qty
                if qty and q and round(qty % q, 2):
                    new_qty = qty - (qty % q) + q
                    return {
                        "warning": {
                            "title": _("Warning"),
                            "message": _(
                                "Increased quantity to %.2f %s since package '%s' "
                                "contains %.2f %s and can only be splitted "
                                "into %s pieces."
                            )
                            % (
                                new_qty,
                                self.product_id.uom_id.name,
                                self.product_packaging.name,
                                self.product_packaging.qty,
                                self.product_id.uom_id.name,
                                round(1 / self.product_packaging.purchase_rounding, 0),
                            ),
                        },
                    }
            return {}
