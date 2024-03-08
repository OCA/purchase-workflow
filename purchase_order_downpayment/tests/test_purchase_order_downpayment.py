from odoo.exceptions import UserError
from odoo.tests import common


class TestPurchaseOrderDownPayment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Abigail Peterson"})
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Ernest Reed"})
        cls.res_partner_3 = cls.env["res.partner"].create({"name": "Jennie Fletcher"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Desk Combination",
            }
        )

        # Purchase Order
        cls.purchase_order_1 = cls.env["purchase.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        cls.purchase_order_2 = cls.env["purchase.order"].create(
            {"partner_id": cls.res_partner_2.id}
        )
        cls.purchase_order_3 = cls.env["purchase.order"].create(
            {"partner_id": cls.res_partner_3.id}
        )

        cls.order_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )

        cls.order_line_2 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_2.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )
        cls.order_line_3 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_3.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )
        cls.order_line_3 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_3.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )

    def test_regular_payment(self):
        self.purchase_order_1.button_confirm()
        context = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        downpayment = (
            self.env["purchase.order.down.payment.wizard"]
            .with_context(**context)
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        self.assertEqual(downpayment.order_id.id, self.purchase_order_1.id)
        downpayment.with_context(view_payment=True).create_payment()
        self.assertTrue(self.purchase_order_1.account_payment_ids)
        payment_id = (
            self.purchase_order_1.account_payment_ids
            and self.purchase_order_1.account_payment_ids[0]
        )
        self.assertEqual(payment_id.amount, self.purchase_order_1.amount_total)
        self.assertEqual(payment_id.partner_id, self.purchase_order_1.partner_id)

    def test_percentage_payment(self):
        self.purchase_order_2.button_confirm()
        context = {
            "active_ids": [self.purchase_order_2.id],
            "active_id": self.purchase_order_2.id,
        }
        downpayment = (
            self.env["purchase.order.down.payment.wizard"]
            .with_context(**context)
            .create({"advance_payment_method": "percentage", "amount": 10})
        )
        self.assertEqual(downpayment.order_id.id, self.purchase_order_2.id)
        downpayment.with_context(view_payment=True).create_payment()
        self.assertTrue(self.purchase_order_2.account_payment_ids)
        payment_id = (
            self.purchase_order_2.account_payment_ids
            and self.purchase_order_2.account_payment_ids[0]
        )
        self.assertEqual(
            payment_id.amount, ((self.purchase_order_2.amount_total * 10) / 100)
        )
        self.assertEqual(payment_id.partner_id, self.purchase_order_2.partner_id)

        with self.assertRaises(UserError):
            self.env["purchase.order.down.payment.wizard"].with_context(
                **context
            ).create({"advance_payment_method": "percentage", "amount": 0})

    def test_fixed_payment(self):
        self.purchase_order_3.button_confirm()
        action = self.purchase_order_3.action_open_payment()
        action.get("domain")
        self.assertEqual(self.purchase_order_3.id, action.get("domain")[0][2])
        context = {
            "active_ids": [self.purchase_order_3.id],
            "active_id": self.purchase_order_3.id,
        }
        downpayment = (
            self.env["purchase.order.down.payment.wizard"]
            .with_context(**context)
            .create({"advance_payment_method": "fixed", "fixed_amount": 50})
        )
        self.assertEqual(downpayment.order_id.id, self.purchase_order_3.id)
        downpayment.create_payment()
        self.assertTrue(self.purchase_order_3.account_payment_ids)
        payment_id = (
            self.purchase_order_3.account_payment_ids
            and self.purchase_order_3.account_payment_ids[0]
        )
        self.assertEqual(payment_id.amount, 50)
        self.assertEqual(payment_id.partner_id, self.purchase_order_3.partner_id)

        with self.assertRaises(UserError):
            self.env["purchase.order.down.payment.wizard"].with_context(
                **context
            ).create({"advance_payment_method": "fixed", "fixed_amount": 0})
