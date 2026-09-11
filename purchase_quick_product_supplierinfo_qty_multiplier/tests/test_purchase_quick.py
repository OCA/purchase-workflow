# @author Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


# Inspired by OCA/purchase_workflow/purchase_quick tests
@tagged("post_install", "-at_install")
class TestPurchaseQuick(TransactionCase):
    @classmethod
    def _add_seller(cls, product, sellers):
        product.seller_ids.filtered(lambda s: s.partner_id == cls.partner).unlink()

        for seller in sellers:
            cls.env["product.supplierinfo"].create(
                {
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "partner_id": cls.partner.id,
                    "min_qty": seller.get("min_qty", 0),
                    "price": seller.get("price", 0),
                    "multiplier_qty": seller.get("multiplier_qty", 0),
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
        cls.product_2 = cls.product_2.with_context(**ctx)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_8")
        cls.product_2 = cls.env.ref("product.product_product_11")

        cls._add_seller(
            cls.product_1,
            [
                {"min_qty": 0, "price": 117, "multiplier_qty": 2},
                {"min_qty": 40, "price": 217, "multiplier_qty": 20},
            ],
        )

        cls._add_seller(
            cls.product_2,
            [
                {"min_qty": 3, "price": 1789, "multiplier_qty": 5},
            ],
        )

        cls._setUpBasicPurchaseOrder()

    # With Product 01, get the right supplier price →
    # for the moment the price link to the lowest min_qty
    def test_01_supplier_price_selection(self):
        self.product_1.qty_to_process = 12  # whatever
        self.assertEqual(self.product_1.seller_price, 117)

    # With Product 02, multiplier quantity 5 should be bad
    # but inverse function change it
    def test_02_multiplier_bad(self):
        self.product_2.qty_to_process = 4
        self.assertAlmostEqual(self.product_2.qty_to_process, 5)

    # With Product 02 multiplier quantity 6 is ok and qty not changed
    def test_03_multiplier_ok(self):
        self.product_2.qty_to_process = 10
        self.assertAlmostEqual(self.product_2.qty_to_process, 10)

    # With Product 02, minimum quantity 2 will be bad
    def test_04_min_qty_bad(self):
        self.product_2.qty_to_process = 2
        self.assertAlmostEqual(self.product_2.qty_to_process, 5)

    # With Product 02, minimum quantity bad + multiplier
    def test_05_min_qty_ok(self):
        self.product_2.qty_to_process = 11
        self.assertAlmostEqual(self.product_2.qty_to_process, 15)
