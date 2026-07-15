# Copyright (C) 2020-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    mass_addition_purchase_discount1 = fields.Float(
        compute="_compute_mass_addition_triple_discount"
    )

    mass_addition_purchase_discount2 = fields.Float(
        compute="_compute_mass_addition_triple_discount"
    )

    mass_addition_purchase_discount3 = fields.Float(
        compute="_compute_mass_addition_triple_discount"
    )

    @api.depends(
        "seller_ids",
        "seller_ids.discount1",
        "seller_ids.discount2",
        "seller_ids.discount3",
        "qty_to_process",
    )
    def _compute_mass_addition_triple_discount(self):
        po = self.pma_parent
        for product in self:
            product.mass_addition_purchase_discount1 = 0
            product.mass_addition_purchase_discount2 = 0
            product.mass_addition_purchase_discount3 = 0

            seller = product._select_seller(
                partner_id=po.partner_id,
                quantity=product.qty_to_process or 1,
                uom_id=product.quick_uom_id,
            )

            if not seller:
                continue

            product.mass_addition_purchase_discount1 = seller.discount1
            product.mass_addition_purchase_discount2 = seller.discount2
            product.mass_addition_purchase_discount3 = seller.discount3
