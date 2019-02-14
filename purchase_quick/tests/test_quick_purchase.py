# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestQuickPurchase(TransactionCase):
    """Test that when an included tax is mapped by a fiscal position,
    the included tax must be
    subtracted to the price of the product.
    """

    def setUp(self):
        super(TestQuickPurchase, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]

    def test_quick_purchase(self):
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")
        po_vals = {"partner_id": self.partner_id.id}
        self.po = self.PurchaseOrder.create(po_vals)
        with Form(self.po, "purchase.purchase_order_form") as po_form:
            po_form.partner_id = self.partner_id
        # test add purchase order line
        self.product_id_1.with_context(
            {"parent_id": self.po.id, "parent_model": "purchase.order"}
        ).qty_to_process = 5.0
        self.assertEqual(
            len(self.po.order_line),
            1,
            "Purchase: no purchase order line created",
        )
        self.product_id_2.with_context(
            {"parent_id": self.po.id, "parent_model": "purchase.order"}
        ).qty_to_process = 6.0
        self.assertEqual(
            len(self.po.order_line), 2, "Purchase order line count must be 2"
        )
        # test purchase line qty
        for line in self.po.order_line:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.product_qty, 5)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.product_qty, 6)

        # test update purchase order line qty
        self.product_id_1.with_context(
            {"parent_id": self.po.id, "parent_model": "purchase.order"}
        ).qty_to_process = 3.0
        self.product_id_2.with_context(
            {"parent_id": self.po.id, "parent_model": "purchase.order"}
        ).qty_to_process = 2.0
        self.assertEqual(
            len(self.po.order_line), 2, "Purchase order line count must be 2"
        )
        # test purchase line qty after update
        for line in self.po.order_line:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.product_qty, 3)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.product_qty, 2)

        # test that add_product open the right action
        product_act_from_po = self.po.add_product()
        self.assertEqual(product_act_from_po["type"], "ir.actions.act_window")
        self.assertEqual(product_act_from_po["res_model"], "product.product")
        self.assertEqual(product_act_from_po["view_mode"], "tree")
        self.assertEqual(product_act_from_po["target"], "current")
        self.assertEqual(
            product_act_from_po["view_id"][0],
            self.env.ref("purchase_quick.product_tree_view4purchase").id,
        )
        self.assertEqual(
            product_act_from_po["context"]["parent_id"], self.po.id
        )
