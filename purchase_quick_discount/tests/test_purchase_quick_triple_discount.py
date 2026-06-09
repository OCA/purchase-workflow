# @author Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


# Inspired by OCA/purchase_workflow/purchase_quick tests
@tagged("post_install", "-at_install")
class TestPurchaseQuickTripleDiscount(TransactionCase):
    @classmethod
    def _add_seller(cls, product, prices):
        product.seller_ids.filtered(lambda s: s.partner_id == cls.partner).unlink()
        for min_qty, price, discount in prices:
            cls.env["product.supplierinfo"].create(
                {
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "partner_id": cls.partner.id,
                    "price": price,
                    "min_qty": min_qty,
                    "discount": discount,
                }
            )

    @classmethod
    def _setUpBasicPurchaseOrder(cls):
        vals = {"partner_id": cls.partner.id}
        if hasattr(cls.env["purchase.order"], "order_type"):
            vals["order_type"] = cls.env.ref("purchase_order_type.po_type_blanket").id
        cls.po = cls.env["purchase.order"].create(vals)
        with Form(cls.po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = cls.partner
        ctx = {"parent_id": cls.po.id, "parent_model": "purchase.order"}
        cls.product_1 = cls.product_1.with_context(**ctx)
        cls.product_1.qty_to_process = 4

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_8")

        # {"min_qty", "price", "discount"},
        cls._add_seller(
            cls.product_1,
            [
                (0, 117, 10),
                (40, 217, 50),
            ],
        )

        cls._setUpBasicPurchaseOrder()

    # With Product 01, get the right discount →
    # for the moment the price link to the lowest min_qty
    def test_01_supplier_discount_selection_for_po(self):
        line_1 = self.po.order_line
        self.product_1._compute_mass_addition_discount()  # for coverage
        self.assertEqual(line_1.discount, 10)
