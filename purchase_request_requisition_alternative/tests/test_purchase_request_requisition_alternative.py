# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPurchaseRequestRequisitionAlternative(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.product = cls.env["product.product"].create(
            {"name": "Requested product", "type": "consu", "purchase_ok": True}
        )
        cls.other_product = cls.env["product.product"].create(
            {"name": "Another product", "type": "consu", "purchase_ok": True}
        )
        cls.request = cls.env["purchase.request"].create(
            {"requested_by": cls.env.user.id}
        )
        cls.request_line = cls.env["purchase.request.line"].create(
            {
                "request_id": cls.request.id,
                "product_id": cls.product.id,
                "name": "Requested product",
                "product_qty": 5.0,
            }
        )

    def _create_order(self, products):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "product_qty": 5.0,
                            "price_unit": 10.0,
                            "date_planned": "2026-01-01",
                        },
                    )
                    for product in products
                ],
            }
        )
        return order

    def _origin_order(self):
        """An order already linked to the request, as the request wizard
        leaves it."""
        order = self._create_order(self.product)
        self.request_line.purchase_lines = [(6, 0, order.order_line.ids)]
        return order

    # ------------------------------------------------------------------
    def test_alternative_is_linked_back_to_the_request(self):
        origin = self._origin_order()
        alternative = self._create_order(self.product)
        origin.alternative_po_ids = [(4, alternative.id)]

        self.assertIn(alternative.order_line, self.request_line.purchase_lines)
        self.assertIn(origin.order_line, self.request_line.purchase_lines)

    def test_only_lines_of_the_same_product_are_linked(self):
        """Linking unrelated products would inflate the purchased quantity."""
        origin = self._origin_order()
        alternative = self._create_order(self.product | self.other_product)
        origin.alternative_po_ids = [(4, alternative.id)]

        linked = self.request_line.purchase_lines
        self.assertTrue(
            all(line.product_id == self.product for line in linked),
            "a line of another product was linked to the request",
        )
        self.assertEqual(len(linked), 2)

    def test_writing_on_several_orders_at_once(self):
        """Regression: the hook used to read fields on a multi-record set."""
        first = self._origin_order()
        second = self._create_order(self.product)
        alternative = self._create_order(self.product)
        (first | second).write({"alternative_po_ids": [(4, alternative.id)]})

        self.assertIn(alternative.order_line, self.request_line.purchase_lines)

    def test_linking_twice_does_not_duplicate(self):
        origin = self._origin_order()
        alternative = self._create_order(self.product)
        origin.alternative_po_ids = [(4, alternative.id)]
        before = len(self.request_line.purchase_lines)

        origin.write({"alternative_po_ids": [(4, alternative.id)]})
        self.assertEqual(len(self.request_line.purchase_lines), before)

    def test_order_without_request_is_untouched(self):
        origin = self._create_order(self.product)
        alternative = self._create_order(self.product)
        origin.alternative_po_ids = [(4, alternative.id)]

        self.assertFalse(self.request_line.purchase_lines)

    def test_empty_alternative_does_nothing(self):
        """An RFQ with no line yet has nothing to link.

        Called directly: alternative_po_ids includes the order itself, so
        going through write() would never leave the set empty.
        """
        origin = self._origin_order()
        empty = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        origin._link_purchase_requests_to(empty)

        self.assertEqual(self.request_line.purchase_lines, origin.order_line)

    def test_wizard_carries_the_link_to_the_new_alternative(self):
        origin = self._origin_order()
        wizard = (
            self.env["purchase.requisition.create.alternative"]
            .with_context(active_id=origin.id)
            .create({"origin_po_id": origin.id, "partner_id": self.vendor.id})
        )
        action = wizard.action_create_alternative()
        alternative = self.env["purchase.order"].browse(action["res_id"])

        self.assertTrue(alternative.order_line)
        self.assertIn(alternative.order_line, self.request_line.purchase_lines)
