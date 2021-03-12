# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, SavepointCase


class TestQuickPurchase(SavepointCase):
    # TODO is the below still relevant ?
    """Test that when an included tax is mapped by a fiscal position,
    the included tax must be
    subtracted to the price of the product.
    """

    def _setUpBasicSaleOrder(self):
        self.po = self.env["purchase.order"].create({"partner_id": self.partner.id})
        with Form(self.po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = self.partner
        ctx = {"parent_id": self.po.id, "parent_model": "purchase.order"}
        self.product_1 = self.env.ref("product.product_product_8").with_context(ctx)
        self.product_2 = self.env.ref("product.product_product_11").with_context(ctx)
        self.product_1.qty_to_process = 5.0
        self.product_2.qty_to_process = 6.0

    def setUp(self):
        super(TestQuickPurchase, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_dozen = self.env.ref("uom.product_uom_dozen")
        self._setUpBasicSaleOrder()

    def test_quick_line_add_1(self):
        """
        set non-null quantity to any product with no PO line:
          -> a new PO line is created with that quantity
        """
        self.assertAlmostEqual(self.po.order_line[0].product_uom_qty, 5.0)
        self.assertAlmostEqual(self.po.order_line[1].product_uom_qty, 6.0)

    def test_quick_line_add_2(self):
        """
        same as previous, but include a different UoM as well
        We duplicate _setUpBasicSaleOrder except we ~simultaneously~
        write on qty_to_process as well as purchase_quick_uom_id
        (we want to make sure to test the twice triggered _inverse function)
        """
        po = self.env["purchase.order"].create({"partner_id": self.partner.id})
        with Form(po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = self.partner
        ctx = {"parent_id": self.po.id, "parent_model": "purchase.order"}
        self.product_1 = self.env.ref("product.product_product_8").with_context(ctx)
        self.product_2 = self.env.ref("product.product_product_11").with_context(ctx)
        self.product_1.write({"qty_to_process": 5.0, "purchase_quick_uom_id": self.uom_unit.id})
        self.product_2.write({"qty_to_process": 6.0, "purchase_quick_uom_id": self.uom_dozen.id})
        self.assertEqual(self.po.order_line[0].product_uom, self.uom_unit)
        self.assertEqual(self.po.order_line[1].product_uom, self.uom_dozen)

    def test_quick_line_update_1(self):
        """
        set non-null quantity to any product with an already existing PO line:
          -> same PO line is updated with that quantity
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        self.assertAlmostEqual(self.po.order_line[0].product_qty, 7.0)
        self.assertAlmostEqual(self.po.order_line[1].product_qty, 13.0)

    def test_quick_line_update_2(self):
        """
        same as previous update only UoM in isolation, not qty
        """
        self.product_1.purchase_quick_uom_id = self.uom_dozen
        self.product_2.purchase_quick_uom_id = self.uom_unit
        self.assertEqual(self.po.order_line[0].product_uom, self.uom_dozen)
        self.assertEqual(self.po.order_line[1].product_uom, self.uom_unit)

    def test_quick_line_update_3(self):
        """
        same as previous 2 tests combined: we do simultaneous qty + uom updates
        """
        self.product_1.qty_to_process = 7.0
        self.product_2.qty_to_process = 13.0
        self.product_1.purchase_quick_uom_id = self.uom_dozen
        self.product_2.purchase_quick_uom_id = self.uom_unit
        self.assertEqual(self.po.order_line[0].product_uom, self.uom_dozen)
        self.assertEqual(self.po.order_line[1].product_uom, self.uom_unit)
        self.assertAlmostEqual(self.po.order_line[0].product_qty, 7.0)
        self.assertAlmostEqual(self.po.order_line[1].product_qty, 13.0)

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
