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
    allowed_vendor_ids = fields.One2many(
        comodel_name="res.partner",
        string="Proveedor",
        compute="_compute_allowed_vendor_ids",
    )

    @api.depends("product_id")
    def _compute_allowed_vendor_ids(self):
        supplierinfo_model = self.env["product.supplierinfo"]
        self.allowed_vendor_ids = self.allowed_vendor_ids
        for item in self.filtered(lambda x: x.product_id):
            item.allowed_vendor_ids = supplierinfo_model.search(
                [
                    "|",
                    ("product_tmpl_id", "=", item.product_id.product_tmpl_id.id),
                    ("product_id", "=", item.product_id.id),
                ]
            ).mapped("name")

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
                        "name": self.vendor_id.id,
                        "min_qty": 0,
                        "company_id": self.company_id.id,
                    }
                )
            res["supplierinfo_id"] = suppinfo
        return res
