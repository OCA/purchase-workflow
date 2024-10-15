from odoo.tests import common


class TestPurchaseOrderDownPaymentToPayOrder(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Abigail Peterson"})

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

        cls.order_line_1 = cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_qty": 1.0,
                "price_unit": 100.0,
            }
        )
        cls.mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Credit Transfer to Suppliers",
                # "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )

    def test_order_payment(self):
        self.purchase_order_1.button_confirm()
        context = {
            "active_ids": [self.purchase_order_1.id],
            "active_id": self.purchase_order_1.id,
        }
        downpayment = (
            self.env["purchase.order.down.payment.wizard"]
            .with_context(**context)
            .create(
                {"advance_payment_method": "delivered", "payment_mode_id": self.mode.id}
            )
        )

        self.assertEqual(downpayment.order_id.id, self.purchase_order_1.id)
        downpayment.with_context(view_payment=True).create_payment()
        self.assertTrue(self.purchase_order_1.account_payment_line_ids)
        payment_line_id = (
            self.purchase_order_1.account_payment_line_ids
            and self.purchase_order_1.account_payment_line_ids[0]
        )
        self.assertEqual(
            payment_line_id.amount_currency, self.purchase_order_1.amount_total
        )
        self.assertEqual(payment_line_id.partner_id, self.purchase_order_1.partner_id)
