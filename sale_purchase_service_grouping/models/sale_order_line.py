# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_get_po_domain(self):
        """Returns the domain used to find the target Purchase Order

        The domain is used to extend the original domain with expression.AND.
        The original domain already looks like this:

        .. code-block:: python

            [
                ("partner_id", "=", partner_supplier.id),
                ("state", "=", "draft"),
                ("company_id", "=", line.company_id.id),
            ]
        """
        self.ensure_one()
        grouping = self.product_id.categ_id.purchase_service_grouping
        if not grouping:
            return
        elif grouping == "sale.order":
            return [
                ("order_line.sale_line_id.order_id", "=", self.order_id.id),
            ]
        elif grouping == "product.category":
            return [
                ("order_line.product_id.categ_id", "=", self.product_id.categ_id.id),
            ]
        elif grouping == "product.template":
            return [
                (
                    "order_line.product_id.product_tmpl_id",
                    "=",
                    self.product_id.product_tmpl_id.id,
                ),
            ]
        elif grouping == "product":
            return [
                ("order_line.product_id", "=", self.product_id.id),
            ]

    def _purchase_service_create(self, quantity=False):
        # Override. Always create a new purchase.order
        #
        # We do this by tricking odoo into thinking there isn't any existing purchase
        # order to insert the products into.
        #
        # We process all lines with no special grouping together as a recordset, as to
        # benefit from the original method's optimizations.
        #
        # See :meth:`~purchase_order.search`.
        records_group = self.filtered("product_id.categ_id.purchase_service_grouping")
        records_no_group = self - records_group
        res = super(SaleOrderLine, records_no_group)._purchase_service_create(quantity)
        for rec in records_group:
            extra_domain = rec._purchase_service_get_po_domain()
            rec_ctx = rec.with_context(purchase_service_grouping_domain=extra_domain)
            res[rec] = super(SaleOrderLine, rec_ctx)._purchase_service_create(
                quantity=quantity
            )
        return res
