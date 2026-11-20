# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from markupsafe import Markup

from odoo import _, api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def auto_rfq_from_suppliers(self):
        """Create one RFQ per supplier for the products they supply."""
        self.ensure_one()
        seller_products, products_without_supplier = self._get_sellers()
        if products_without_supplier:
            self._post_products_without_supplier_message(products_without_supplier)
        return self._create_rfqs(seller_products)

    def _get_sellers(self):
        seller_products = defaultdict(lambda: self.env["product.product"])
        products_without_supplier = self.env["product.product"]
        for line in self.line_ids:
            sellers = line._get_rfq_suppliers()
            if not sellers:
                products_without_supplier |= line.product_id
            for seller in sellers:
                seller_products[seller.id] |= line.product_id
        return seller_products, products_without_supplier

    def _create_rfqs(self, seller_products):
        rfqs = self.env["purchase.order"]
        for seller_id, sold_products in seller_products.items():
            rfqs |= self._create_purchase_order(seller_id, sold_products)
        return rfqs

    def _post_products_without_supplier_message(self, products):
        body = Markup(
            _(
                "<p><b>RFQ generation</b></p>"
                "<p>The following products have no "
                "registered suppliers and are not included in the "
                "generated RFQs:<ul>%s</ul></p>"
            )
        )
        items = Markup("").join(
            Markup("<li>%s</li>") % product.name for product in products
        )
        self.message_post(body=body % items, subject=_("RFQ Generation"))

    def _create_purchase_order(self, seller_id, sold_products):
        purchase_order = self.env["purchase.order"].with_company(self.company_id)
        order = purchase_order.new(
            {
                "partner_id": seller_id,
                "requisition_id": self.id,
                "company_id": self.company_id.id,
                "user_id": self.user_id.id or self.env.uid,
            }
        )
        # Reuse the values populated by Odoo's New Quotation button.
        order._onchange_requisition_id()
        order.order_line = order.order_line.filtered(
            lambda line: line.product_id in sold_products
        )
        return purchase_order.create(order._convert_to_write(order._cache))


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    prod_has_supplier = fields.Boolean(
        compute="_compute_prod_has_supplier", string="Product without suppliers"
    )

    def _get_rfq_suppliers(self):
        self.ensure_one()
        product = self.product_id.with_company(self.requisition_id.company_id)
        return product._prepare_sellers().partner_id

    @api.depends(
        "requisition_id.company_id",
        "product_id.seller_ids",
        "product_id.seller_ids.company_id",
        "product_id.seller_ids.product_id",
        "product_id.seller_ids.partner_id.active",
    )
    def _compute_prod_has_supplier(self):
        for line in self:
            line.prod_has_supplier = bool(line._get_rfq_suppliers())
