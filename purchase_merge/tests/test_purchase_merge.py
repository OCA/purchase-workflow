from odoo.exceptions import UserError
from odoo.tests import common


class TestPurchaseMerge(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PurchaseMerge = cls.env["purchase.merge.automatic.wizard"]
        cls.product_1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.product_2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Partner 2"})
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
        cls.purchase_order_eur = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.EUR").id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_2.id, "price_unit": 10})
                ],
            }
        )
        cls.purchase_order_usd = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner.id,
                "currency_id": cls.env.ref("base.USD").id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_2.id, "price_unit": 10})
                ],
            }
        )
        cls.fiscal_position_1 = cls.env["account.fiscal.position"].create(
            {"name": "Fiscal Position 1"}
        )
        cls.fiscal_position_2 = cls.env["account.fiscal.position"].create(
            {"name": "Fiscal Position 2"}
        )
        cls.incoterm_1 = cls.env["account.incoterms"].create(
            {"name": "Incoterm 1", "code": "INC1"}
        )
        cls.incoterm_2 = cls.env["account.incoterms"].create(
            {"name": "Incoterm 2", "code": "INC2"}
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

    def test_purchase_order_currency(self):
        purchase_order_dst = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst.write({"state": "sent"})
        purchase_merge_4 = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [self.purchase_order_eur.id, self.purchase_order_usd.id])
                ],
                "dst_purchase_id": purchase_order_dst.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders with different currencies: .+",
        ):
            purchase_merge_4._check_all_values(purchase_merge_4.purchase_ids)

    def test_purchase_order_fiscal_position(self):
        purchase_order_fp_1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "fiscal_position_id": self.fiscal_position_1.id,
            }
        )
        purchase_order_fp_2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "fiscal_position_id": self.fiscal_position_2.id,
            }
        )
        purchase_order_dst = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst.write({"state": "sent"})
        purchase_merge = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [purchase_order_fp_1.id, purchase_order_fp_2.id])
                ],
                "dst_purchase_id": purchase_order_dst.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders with different fiscal positions: .+",
        ):
            purchase_merge._check_all_values(purchase_merge.purchase_ids)

    def test_purchase_order_incoterms(self):
        purchase_order_inc_1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "incoterm_id": self.incoterm_1.id,
            }
        )
        purchase_order_inc_2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "incoterm_id": self.incoterm_2.id,
            }
        )
        purchase_order_dst = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst.write({"state": "sent"})
        purchase_merge = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [purchase_order_inc_1.id, purchase_order_inc_2.id])
                ],
                "dst_purchase_id": purchase_order_dst.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders with different incoterms: .+",
        ):
            purchase_merge._check_all_values(purchase_merge.purchase_ids)

    def test_purchase_order_payment_terms(self):
        purchase_order_pt_1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "payment_term_id": self.env.ref(
                    "account.account_payment_term_end_following_month"
                ).id,
            }
        )
        purchase_order_pt_2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
                "payment_term_id": self.env.ref(
                    "account.account_payment_term_15days"
                ).id,
            }
        )
        purchase_order_dst = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst.write({"state": "sent"})
        purchase_merge = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [purchase_order_pt_1.id, purchase_order_pt_2.id])
                ],
                "dst_purchase_id": purchase_order_dst.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders with different payment terms: .+",
        ):
            purchase_merge._check_all_values(purchase_merge.purchase_ids)

    def test_purchase_order_partners(self):
        purchase_order_partner1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_partner2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_2.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_2.id, "price_unit": 10})
                ],
            }
        )
        purchase_order_dst.write({"state": "sent"})
        purchase_merge = self.PurchaseMerge.create(
            {
                "purchase_ids": [
                    (6, 0, [purchase_order_partner1.id, purchase_order_partner2.id])
                ],
                "dst_purchase_id": purchase_order_dst.id,
            }
        )
        with self.assertRaisesRegex(
            UserError,
            r"You can't merge purchase orders with different suppliers: .+",
        ):
            purchase_merge._check_all_values(purchase_merge.purchase_ids)

    def test_merge_no_dst_and_moves_activity(self):
        """
        Test merge when no destination is set and
        that an activity is correctly moved (testing openupgrade).
        """
        src_po = self.purchase_order_1
        dst_po = self.purchase_order_2

        activity = self.env["mail.activity"].create(
            {
                "res_model_id": self.env.ref("purchase.model_purchase_order").id,
                "res_id": src_po.id,
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "summary": "Test Activity",
            }
        )
        self.assertEqual(activity.res_id, src_po.id)
        wizard = self.PurchaseMerge.create(
            {"purchase_ids": [(6, 0, [src_po.id, dst_po.id])]}
        )
        wizard.action_merge()
        self.assertEqual(
            activity.res_id, dst_po.id, "Activity should have been moved to dst_po."
        )
        self.assertEqual(src_po.state, "cancel", "Source PO should be cancelled.")
        self.assertEqual(
            len(dst_po.order_line), 2, "Destination PO should have 2 lines."
        )
