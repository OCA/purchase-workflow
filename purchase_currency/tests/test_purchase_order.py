# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestPurchaseOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env["res.company"].create({"name": "Odoo Test Company"})
        self.partner = self.env["res.partner"].create({"name": "Partner #1"})
        self.eur_currency = self.env.ref("base.EUR")
        self.usd_currency = self.env.ref("base.USD")
        self.product = self.env["product.product"].create(
            {
                "name": "Product #1",
            }
        )
        self.env.user.write(
            {"company_ids": [(4, self.company.id)], "company_id": self.company.id}
        )

    def test_create_purchase_order(self):
        """
        Test flow when set default currency for purchase order
        and vendor bill
        """
        self.env.company.currency_id = self.eur_currency
        form = Form(self.env["purchase.order"])
        form.partner_id = self.partner
        order = form.save()

        self.assertEqual(
            order.currency_id.id, self.eur_currency.id, "Order currency must be EUR"
        )

        self.env.company.default_purchase_currency_id = self.usd_currency
        form = Form(self.env["purchase.order"])
        form.partner_id = self.partner
        with form.order_line.new() as line:
            line.product_id = self.product
            line.product_qty = 10
            line.price_unit = 10.0
        order = form.save()
        self.assertEqual(
            order.currency_id.id, self.usd_currency.id, "Order currency must be USD"
        )
        order.button_confirm()
        with Form(order) as form, form.order_line.edit(0) as line:
            line.qty_received = 10.0
        result = order.action_create_invoice()
        record = self.env["account.move"].browse(result["res_id"])
        self.assertEqual(
            record.currency_id.id,
            self.usd_currency.id,
            "Vendor Bill currency must be USD",
        )
