# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    can_update_product_supplierinfo = fields.Boolean(
        compute="_compute_can_update_product_supplierinfo",
    )

    def action_update_product_supplierinfo(self):
        self.ensure_one()

        product_supplierinfo = (
            self.product_id._select_seller(
                partner_id=self.partner_id,
                quantity=self.product_qty,
                date=self.order_id.date_order
                and self.order_id.date_order.date()
                or fields.Date.context_today(self),
                uom_id=self.product_uom,
                params=self._get_select_sellers_params(),
            )
            if self.product_id
            else False
        )

        if product_supplierinfo:
            product_supplierinfo.write(
                {
                    "price": self.price_unit,
                }
            )
        else:
            self.product_id.seller_ids.create(
                {
                    "partner_id": self.partner_id.id,
                    "product_tmpl_id": self.product_id.product_tmpl_id.id,
                    "price": self.price_unit,
                }
            )

    @api.onchange("product_id", "partner_id", "price_unit")
    def _compute_can_update_product_supplierinfo(self):
        for line in self:
            # We need this condition because in some situations the onchange methods can fail.
            if (
                not line._origin.id
                or not line.product_id
                or not line.partner_id
                or not line.price_unit
            ):
                line.can_update_product_supplierinfo = False
                continue
            product_supplierinfo = (
                line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order
                    and line.order_id.date_order.date()
                    or fields.Date.context_today(self),
                    uom_id=line.product_uom,
                    params=line._get_select_sellers_params(),
                )
                if line.product_id
                else False
            )
            line.can_update_product_supplierinfo = bool(
                not product_supplierinfo
                or product_supplierinfo.price != line.price_unit
            )
