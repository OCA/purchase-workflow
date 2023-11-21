# Copyright 2022 Tecnativa - Víctor Martínez
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

    def _prepare_procurement_values(self, group_id=False):
        """Inject in the procurement values the preferred vendor if any, and create
        supplierinfo record for it if it doesn't exist.
        """
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.vendor_id:
            product = self.product_id
            suppinfo = product.with_company(self.company_id.id)._select_seller(
                partner_id=self.vendor_id,
                quantity=self.product_uom_qty,
                uom_id=self.product_uom,
            )
            if not suppinfo:
                suppinfo = self.env["product.supplierinfo"].create(
                    {
                        "product_tmpl_id": product.product_tmpl_id.id,
                        "partner_id": self.vendor_id.id,
                        "min_qty": 0,
                        "company_id": self.company_id.id,
                    }
                )
            res["supplierinfo_id"] = suppinfo
        return res
