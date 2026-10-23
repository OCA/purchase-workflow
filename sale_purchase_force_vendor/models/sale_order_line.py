# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_purchase_force_vendor_restrict = fields.Boolean(
        related="company_id.sale_purchase_force_vendor_restrict"
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
    )
    vendor_id_domain = fields.Binary(
        compute="_compute_vendor_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("product_id")
    def _compute_vendor_id_domain(self):
        for item in self:
            domain = (
                [("id", "in", item.product_id.variant_seller_ids.partner_id.ids)]
                if item.order_id.sale_purchase_force_vendor_restrict
                else []
            )
            item.vendor_id_domain = domain

    def _prepare_force_vendor_product_supplierinfo_vals(self):
        """We use this method so that we can overwrite it if we need to modify or
        add a value.
        """
        return {
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "partner_id": self.vendor_id.id,
            "min_qty": 0,
            "company_id": self.company_id.id,
        }

    def _prepare_procurement_values(self, group_id=False):
        """Inject in the procurement values the preferred vendor if any, and create
        supplierinfo record for it if it doesn't exist.
        """
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.vendor_id:
            product = self.product_id
            suppinfo = product.with_company(self.company_id.id)._select_seller(
                partner_id=self.vendor_id,
                # `_select_seller` discards every seller whose `min_qty` is
                # greater than the requested quantity, and every `min_qty` is
                # >= 0, so a negative quantity matches no seller at all. A
                # non-positive line is not a purchase, so degrade it to 0
                # rather than making up a purchase quantity for it. A seller
                # with a `min_qty` above 0 will not match either, which is
                # harmless: such a line creates no purchase and never consumes
                # `supplierinfo_id`.
                quantity=max(self.product_uom_qty, 0),
                uom_id=self.product_uom,
            )
            # Only a line that will actually trigger a purchase may register a
            # new vendor. Otherwise every return line would autocreate a
            # supplierinfo with no price, no product name and no product code.
            # `res["supplierinfo_id"]` is still always set (an empty recordset
            # when nothing matched) because `stock.move` reads that key with
            # direct access.
            if not suppinfo and self.product_uom_qty > 0:
                # By default user with group_sale_salesman group can not creates
                # supplierinfo records.
                suppinfo = (
                    self.env["product.supplierinfo"]
                    .sudo()
                    .create(self._prepare_force_vendor_product_supplierinfo_vals())
                )
            res["supplierinfo_id"] = suppinfo
        return res
