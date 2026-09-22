# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math

from odoo import _, api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    mass_addition_purchase_min_qty = fields.Float(
        compute="_compute_mass_addition_purchase"
    )

    mass_addition_purchase_multiplier_qty = fields.Float(
        compute="_compute_mass_addition_purchase"
    )

    mass_addition_purchase_min_qty_bad = fields.Boolean(
        compute="_compute_mass_addition_purchase_bad"
    )

    mass_addition_purchase_multiplier_qty_bad = fields.Boolean(
        compute="_compute_mass_addition_purchase_bad"
    )

    @api.depends(
        "qty_to_process",
        "mass_addition_purchase_min_qty",
        "mass_addition_purchase_multiplier_qty",
    )
    def _compute_mass_addition_purchase_bad(self):
        for product in self.filtered(lambda x: not x.qty_to_process):
            product.mass_addition_purchase_min_qty_bad = False
            product.mass_addition_purchase_multiplier_qty_bad = False

        for product in self.filtered(lambda x: x.qty_to_process):
            product.mass_addition_purchase_min_qty_bad = (
                product.mass_addition_purchase_min_qty
                and (product.qty_to_process < product.mass_addition_purchase_min_qty)
            )
            product.mass_addition_purchase_multiplier_qty_bad = (
                product.mass_addition_purchase_multiplier_qty
                and (
                    product.qty_to_process
                    % product.mass_addition_purchase_multiplier_qty
                )
            )

    @api.depends(
        "seller_ids",
        "seller_ids.price",
        "seller_ids.min_qty",
        "seller_ids.multiplier_qty",
        "qty_to_process",
    )
    def _compute_mass_addition_purchase(self):
        po = self.pma_parent
        for product in self:
            seller = product.seller_ids.filtered(
                lambda r: r.partner_id == po.partner_id
            ).sorted(key=lambda r: r.price)[0]
            product.mass_addition_purchase_min_qty = seller.min_qty
            product.mass_addition_purchase_multiplier_qty = seller.multiplier_qty

    def _inverse_set_process_qty(self):
        if self.env.context.get("parent_model") != "purchase.order":
            return super()._inverse_set_process_qty()

        for product in self:
            user_qty = product.qty_to_process or 0.0
            min_qty = product.mass_addition_purchase_min_qty or 0.0
            mult = product.mass_addition_purchase_multiplier_qty or 0.0

            # Respect minimum quantity
            target_qty = max(user_qty, min_qty)
            changeby = "min_qty" if target_qty != user_qty else False

            # Respect multiplier
            new_qty = target_qty
            if mult:
                new_qty = math.ceil(target_qty / mult) * mult
                if new_qty != target_qty:
                    changeby = "mult"

            if changeby == "min_qty":
                message = _(
                    "Quantity was too small.\n"
                    "The quantity has been automatically changed to %(qty)s %(uom)s."
                ) % {
                    "qty": target_qty,
                    "uom": product.uom_name,
                }

            elif changeby == "mult":
                message = _(
                    "The supplier only sells this product by %(mult)s %(uom)s.\n"
                    "The quantity has been automatically changed to %(qty)s %(uom)s."
                ) % {
                    "mult": mult,
                    "qty": new_qty,
                    "uom": product.uom_name,
                }

            else:
                continue

            self.env.user.notify_warning(
                title=_("Warning"),
                message=message,
            )

            product.qty_to_process = new_qty

        return super()._inverse_set_process_qty()
