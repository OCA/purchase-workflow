# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase, new_test_user


class TestPurchaseRequisition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.purchase_user = new_test_user(
            cls.env, login="rfq_purchase_user", groups="purchase.group_purchase_user"
        )
        cls.vendor_a, cls.vendor_b, cls.vendor_c = cls.env["res.partner"].create(
            [{"name": name} for name in ("Vendor A", "Vendor B", "Vendor C")]
        )
        cls.kitchenset, cls.blankets, cls.tarpaulin = cls.env["product.product"].create(
            [
                {
                    "name": "Kitchen Set",
                    "seller_ids": [
                        Command.create({"partner_id": supplier.id})
                        for supplier in (cls.vendor_a, cls.vendor_b)
                    ],
                },
                {
                    "name": "Blankets",
                    "seller_ids": [
                        Command.create({"partner_id": supplier.id})
                        for supplier in (cls.vendor_b, cls.vendor_c)
                    ],
                },
                {"name": "Tarpaulin <samples>"},
            ]
        )

    def _create_template(self, *products, buyer=None):
        agreement = (
            self.env["purchase.requisition"]
            .with_user(self.purchase_user)
            .create(
                {
                    "requisition_type": "purchase_template",
                    "user_id": buyer and buyer.id,
                    "description": "<p>Quotation terms</p>",
                    "line_ids": [
                        Command.create(
                            {
                                "product_id": product.id,
                                "product_qty": quantity,
                                "price_unit": price,
                            }
                        )
                        for product, quantity, price in products
                    ],
                }
            )
        )
        agreement.action_confirm()
        return agreement

    def test_auto_rfq_from_suppliers(self):
        buyer = new_test_user(
            self.env, login="rfq_agreement_buyer", groups="purchase.group_purchase_user"
        )
        agreement = self._create_template(
            (self.kitchenset, 10, 12), (self.blankets, 100, 3), buyer=buyer
        )

        rfqs = agreement.auto_rfq_from_suppliers()

        self.assertEqual(len(rfqs), 3)
        self.assertEqual(agreement.purchase_ids, rfqs)
        self.assertEqual(rfqs.user_id, buyer)
        self.assertEqual(rfqs.company_id, agreement.company_id)
        self.assertEqual(rfqs.currency_id, agreement.currency_id)
        self.assertEqual(rfqs.mapped("state"), ["draft"] * 3)
        self.assertEqual(set(rfqs.mapped("origin")), {agreement.name})
        self.assertEqual(set(rfqs.mapped("notes")), {agreement.description})
        self.assertEqual(
            {
                rfq.partner_id: [
                    (line.product_id, line.product_qty, line.price_unit)
                    for line in rfq.order_line
                ]
                for rfq in rfqs
            },
            {
                self.vendor_a: [(self.kitchenset, 10, 12)],
                self.vendor_b: [(self.kitchenset, 10, 12), (self.blankets, 100, 3)],
                self.vendor_c: [(self.blankets, 100, 3)],
            },
        )
        self.assertFalse(agreement.message_ids.filtered_domain(self._message_domain()))

    def test_auto_rfq_from_suppliers_no_supplier(self):
        agreement = self._create_template(
            (self.tarpaulin, 10, 12), (self.blankets, 100, 3)
        )

        rfqs = agreement.auto_rfq_from_suppliers()

        self.assertEqual(len(rfqs), 2)
        self.assertEqual(rfqs.partner_id, self.vendor_b | self.vendor_c)
        self.assertEqual(rfqs.order_line.product_id, self.blankets)
        self.assertEqual(rfqs.user_id, self.purchase_user)
        self.assertEqual(agreement.line_ids.mapped("prod_has_supplier"), [False, True])
        message = agreement.message_ids.filtered_domain(self._message_domain())
        self.assertEqual(len(message), 1)
        self.assertIn("<li>Tarpaulin &lt;samples&gt;</li>", message.body)

    def test_suppliers_for_other_variants_and_companies_are_ignored(self):
        other_company = self.env["res.company"].create({"name": "Another company"})
        attribute = self.env["product.attribute"].create({"name": "Colour"})
        values = self.env["product.attribute.value"].create(
            [
                {"name": name, "attribute_id": attribute.id}
                for name in ("White", "Black")
            ]
        )
        template = self.env["product.template"].create(
            {
                "name": "Variant product",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(values.ids)],
                        }
                    )
                ],
            }
        )
        product, other_variant = template.product_variant_ids
        template.seller_ids = [
            Command.create({"partner_id": self.vendor_a.id, "product_id": product.id}),
            Command.create(
                {"partner_id": self.vendor_b.id, "product_id": other_variant.id}
            ),
            Command.create(
                {"partner_id": self.vendor_c.id, "company_id": other_company.id}
            ),
        ]
        agreement = self._create_template((product, 5, 10))

        self.assertEqual(agreement.auto_rfq_from_suppliers().partner_id, self.vendor_a)

        template.seller_ids.filtered(lambda s: s.partner_id == self.vendor_a).unlink()
        self.assertFalse(agreement.line_ids.prod_has_supplier)
        self.assertFalse(agreement.auto_rfq_from_suppliers())

    @staticmethod
    def _message_domain():
        return [("subject", "=", "RFQ Generation")]
