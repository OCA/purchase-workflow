from odoo.exceptions import UserError
from odoo.tests import common


class TestPurchaseMerge(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseMerge, cls).setUpClass()
        cls.PurchaseMerge = cls.env["purchase.merge.automatic.wizard"]
        cls.product_1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.product_2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.purchase_order_1 = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "price_unit": 10})
                ],
            }
        )
        cls.purchase_order_2 = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_2.id, "price_unit": 10})
                ],
            }
        )

    def test_count_purchase_order_lines(self):
        self.purchase_merge_1 = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [self.purchase_order_1.id, self.purchase_order_2.id])
                ],
                "dst_purchase_id": self.purchase_order_2.id,
            }
        )
        self.purchase_merge_1.action_merge()
        self.purchase_order_line_1 = len(self.purchase_order_2.order_line)
        self.assertEqual(self.purchase_order_line_1, 2)

    def test_purchase_ids(self):
        self.purchase_merge_2 = self.PurchaseMerge.create(
            {
                "dst_purchase_id": self.purchase_order_2.id,
            }
        )
        self.assertEqual(self.purchase_merge_2.action_merge(), False)

    def test_default_purchase_ids(self):
        context = {
            "active_ids": [self.purchase_order_1.id, self.purchase_order_2.id],
            "active_model": self.PurchaseOrder._name,
        }
        self.purchase_merge_3 = self.PurchaseMerge.with_context(**context).create({})
        self.assertEqual(len(self.purchase_merge_3.dst_purchase_id), 1)
        self.assertEqual(len(self.purchase_merge_3.purchase_ids), 2)

    def test_purchase_order_states(self):
        self.purchase_order_3 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        self.purchase_order_3.write({"state": "sent"})
        self.purchase_merge_4 = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [self.purchase_order_1.id, self.purchase_order_3.id])
                ],
                "dst_purchase_id": self.purchase_order_3.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders that aren't in draft state like: .+",
        ):
            self.purchase_merge_4._check_state(self.purchase_merge_4.purchase_ids)
