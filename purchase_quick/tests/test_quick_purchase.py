# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestQuickPurchase(SavepointCase):
    @classmethod
    def _add_seller(cls, product, prices):
        # drop existing seller
        product.seller_ids.filtered(lambda s: s.name == cls.partner).unlink()
        for min_qty, price in prices:
            cls.env["product.supplierinfo"].create(
                {
                    "product_tmpl_id": product.product_tmpl_id.id,
                    "name": cls.partner.id,
                    "price": price,
                    "min_qty": min_qty,
                }
            )

    @classmethod
    def _setUpBasicSaleOrder(cls):
        cls.po = cls.env["purchase.order"].create({"partner_id": cls.partner.id})
        with Form(cls.po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = cls.partner
        ctx = {"parent_id": cls.po.id, "parent_model": "purchase.order"}
        cls.product_1 = cls.product_1.with_context(ctx)
        cls.product_2 = cls.product_2.with_context(ctx)
        cls.product_1.qty_to_process = 5.0
        cls.product_2.qty_to_process = 6.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.user = cls.env.ref("base.user_demo")
        cls.product_1 = cls.env.ref("product.product_product_8")
        cls.product_2 = cls.env.ref("product.product_product_11")
        cls._add_seller(cls.product_1, [(0, 10), (10, 8)])
        cls._add_seller(cls.product_2, [(0, 5), (10, 4)])
        cls._setUpBasicSaleOrder()

    def test_product_seller_price(self):
        self.assertEqual(self.product_1.seller_price, 10)
        self.product_1.qty_to_process = 10.0
        self.assertEqual(self.product_1.seller_price, 8)
        self.product_1.quick_uom_id = self.uom_dozen
        self.assertEqual(self.product_1.seller_price, 96)

    def test_product_seller_price_with_currency(self):
        self.po.currency_id = self.env.ref("base.EUR")
        usd = self.env.ref("base.USD")
        usd.rate_ids[1:].unlink()
        usd.rate_ids.name = self.po.date_order.date()
        usd.rate_ids.rate = 2
        self.assertEqual(self.product_1.seller_price, 5)
        self.product_1.qty_to_process = 10.0
        self.assertEqual(self.product_1.seller_price, 4)
        self.product_1.quick_uom_id = self.uom_dozen
        self.assertEqual(self.product_1.seller_price, 48)

    def test_quick_line_add_1(self):
        """
        set non-null quantity to any product with no PO line:
          -> a new PO line is created with that quantity
        """
        line_1, line_2 = self.po.order_line
        self.assertAlmostEqual(line_1.product_uom_qty, 5.0)
        self.assertAlmostEqual(line_1.price_unit, 10)
        self.assertAlmostEqual(line_2.product_uom_qty, 6.0)
        self.assertAlmostEqual(line_2.price_unit, 5)

    def test_quick_line_add_2(self):
        """
        same as previous, but include a different UoM as well
        We duplicate _setUpBasicSaleOrder except we ~simultaneously~
        write on qty_to_process as well as quick_uom_id
        (we want to make sure to test _inverse function when it is triggered twice)
        """
        po = self.env["purchase.order"].create({"partner_id": self.partner.id})
        with Form(po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = self.partner
        ctx = {"parent_id": self.po.id, "parent_model": "purchase.order"}
        self.product_1 = self.product_1.with_context(ctx)
        self.product_2 = self.product_2.with_context(ctx)
        self.product_1.write({"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id})
        self.product_2.write({"qty_to_process": 6.0, "quick_uom_id": self.uom_dozen.id})

        line_1, line_2 = self.po.order_line
        self.assertAlmostEqual(line_1.product_uom_qty, 5.0)
        self.assertAlmostEqual(line_1.product_qty, 5.0)
        self.assertEqual(line_1.product_uom, self.uom_unit)
        self.assertAlmostEqual(line_1.price_unit, 10)

        self.assertAlmostEqual(line_2.product_uom_qty, 72.0)  # 12 * 6
        self.assertAlmostEqual(line_2.product_qty, 6.0)
        self.assertEqual(line_2.product_uom, self.uom_dozen)
        self.assertAlmostEqual(line_2.price_unit, 48)  # 12 * 4

    def test_quick_line_update_1(self):
        """
        set non-null quantity to any product with an already existing PO line:
          -> same PO line is updated with that quantity
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        line_1, line_2 = self.po.order_line
        self.assertAlmostEqual(line_1.product_qty, 7.0)
        self.assertAlmostEqual(line_1.price_unit, 10.0)
        self.assertAlmostEqual(line_2.product_qty, 13.0)
        self.assertAlmostEqual(line_2.price_unit, 4.0)

    def test_quick_line_update_2(self):
        """
        same as previous update only UoM in isolation, not qty
        """
        self.product_1.quick_uom_id = self.uom_dozen
        self.product_2.quick_uom_id = self.uom_unit
        line_1, line_2 = self.po.order_line

        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertAlmostEqual(line_1.product_qty, 5.0)
        self.assertAlmostEqual(line_1.product_uom_qty, 60.0)
        self.assertAlmostEqual(line_1.price_unit, 96)

        self.assertEqual(line_2.product_uom, self.uom_unit)
        self.assertAlmostEqual(line_2.product_qty, 6.0)
        self.assertAlmostEqual(line_2.product_uom_qty, 6.0)
        self.assertAlmostEqual(line_2.price_unit, 5.0)

    def test_quick_line_update_3(self):
        """
        same as previous 2 tests combined: we do simultaneous qty + uom updates
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        self.product_1.quick_uom_id = self.uom_dozen
        self.product_2.quick_uom_id = self.uom_unit

        line_1, line_2 = self.po.order_line
        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertEqual(line_2.product_uom, self.uom_unit)

        self.assertEqual(line_1.product_uom, self.uom_dozen)
        self.assertAlmostEqual(line_1.product_qty, 7.0)
        self.assertAlmostEqual(line_1.product_uom_qty, 84.0)
        self.assertAlmostEqual(line_1.price_unit, 96)

        self.assertEqual(line_2.product_uom, self.uom_unit)
        self.assertAlmostEqual(line_2.product_qty, 13.0)
        self.assertAlmostEqual(line_2.product_uom_qty, 13.0)
        self.assertAlmostEqual(line_2.price_unit, 4.0)

    def test_quick_line_delete(self):
        """
        set null quantity to any product with existing PO line:
          -> PO line is deleted
        """
        self.product_1.qty_to_process = 0.0
        self.product_2.qty_to_process = 0.0
        self.assertEqual(len(self.po.order_line), 0)

    def test_open_quick_view(self):
        """
        Test that the "Add" button opens the right action
        """
        product_act_from_po = self.po.add_product()
        self.assertEqual(product_act_from_po["type"], "ir.actions.act_window")
        self.assertEqual(product_act_from_po["res_model"], "product.product")
        self.assertEqual(product_act_from_po["view_mode"], "tree")
        self.assertEqual(product_act_from_po["target"], "current")
        self.assertEqual(
            product_act_from_po["view_id"][0],
            self.env.ref("purchase_quick.product_tree_view4purchase").id,
        )
        self.assertEqual(product_act_from_po["context"]["parent_id"], self.po.id)

    def test_several_po_for_one_product(self):
        """
        Test that when we try to mass add a product that already has
        several lines with the same product we get a raise
        """
        self.po.order_line[0].copy()
        with self.assertRaises(ValidationError):
            self.product_1.qty_to_process = 3.0

    def test_purchaser_can_edit_products(self):
        """
        While in the quick purchase interface, a purchaser with no edit rights
        on product.product can still edit product.product quick quantities
        """
        po = self.env["purchase.order"].create({"partner_id": self.partner.id})
        ctx = {
            "parent_id": po.id,
            "parent_model": "purchase.order",
            "quick_access_rights_purchase": 1,
        }
        product = self.env.ref("product.product_product_8")
        with self.assertRaises(AccessError):
            product.with_user(self.user).write(
                {"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id}
            )
        product_in_quick_edit = product.with_user(self.user).with_context(ctx)
        product_in_quick_edit.write(
            {"qty_to_process": 5.0, "quick_uom_id": self.uom_unit.id}
        )
