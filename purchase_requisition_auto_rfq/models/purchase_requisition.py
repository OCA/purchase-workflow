# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def auto_rfq_from_suppliers(self):
        """create purchase orders from registered suppliers for products in the
        requisition.

        The created PO for each supplier will only concern the products for
        which an existing product.supplierinfo record exist for that product.
        """
        self.ensure_one()
        seller_products, products_without_supplier = self._get_sellers()
        if products_without_supplier:
            self._post_products_without_supplier_message(products_without_supplier)
        return self._create_rfqs(seller_products)

    def _get_sellers(self):
        seller_products = defaultdict(lambda: self.env["product.product"])
        products_without_supplier = []
        for line in self.line_ids:
            sellers = line.product_id.product_tmpl_id.seller_ids
            if not sellers:
                products_without_supplier.append(line.product_id)
            for seller in sellers:
                seller_products[seller.name.id] |= line.product_id
        return seller_products, products_without_supplier

    def _create_rfqs(self, seller_products):
        rfqs = self.env["purchase.order"]
        for seller_id, sold_products in seller_products.items():
            purchase = self._create_purchase_order(seller_id)
            self._remove_lines_without_official_supplier(purchase, sold_products)
            rfqs |= purchase
        return rfqs

    def _remove_lines_without_official_supplier(self, purchase, sold_products):
        purchase.order_line.filtered(
            lambda l: l.product_id not in sold_products
        ).unlink()

    def _post_products_without_supplier_message(self, products):
        body = _(
            "<p><b>RFQ generation</b></p>"
            "<p>The following products have no "
            "registered suppliers and are not included in the "
            "generated RFQs:<ul>%s</ul></p>"
        )
        body %= "".join("<li>%s</li>" % product.name for product in products)
        self.message_post(body=body, subject=_("RFQ Generation"))

    def _create_purchase_order(self, seller_id):
        vals = {"partner_id": seller_id}
        ctx = {"default_requisition_id": self.id}
        po = self.env["purchase.order"].with_context(**ctx).create(vals)
        po._onchange_requisition_id()
        return po


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    prod_has_supplier = fields.Boolean(
        compute="_compute_prod_has_supplier", string="Product without suppliers"
    )

    @api.depends("product_id.product_tmpl_id.seller_ids")
    def _compute_prod_has_supplier(self):
        for rec in self:
            rec.prod_has_supplier = bool(rec.product_id.product_tmpl_id.seller_ids)
