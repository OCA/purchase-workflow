# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPurchaseRequisition(SavepointCase):
    def setUp(self):
        super().setUp()
        self._init_products()
        self._init_requisitions()

    def _init_products(self):
        self._kitchenset = self.env.ref("purchase_requisition_auto_rfq.kitchenset")
        self._blankets = self.env.ref("purchase_requisition_auto_rfq.blankets")
        self._tarpaulin = self.env.ref("purchase_requisition_auto_rfq.tarpaulin")

    def _init_requisitions(self):
        uom = self._kitchenset.uom_po_id
        self._requisition1 = self.env["purchase.requisition"].create(
            {
                "name": "PR01",
                "line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self._kitchenset.id,
                            "product_qty": 10,
                            "product_uom_id": uom.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self._blankets.id,
                            "product_qty": 100,
                            "product_uom_id": uom.id,
                        },
                    ),
                ],
            }
        )

        self._requisition2 = self.env["purchase.requisition"].create(
            {
                "name": "PR02",
                "line_ids": [
                    (
                        0,
                        False,
                        {
                            "product_id": self._tarpaulin.id,
                            "product_qty": 10,
                            "product_uom_id": uom.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self._blankets.id,
                            "product_qty": 100,
                            "product_uom_id": uom.id,
                        },
                    ),
                ],
            }
        )

    def test_auto_rfq_from_suppliers(self):
        rfqs = self._requisition1.auto_rfq_from_suppliers()

        msg = "Expected 3 distinct RFQs, got %r" % rfqs
        self.assertEqual(3, len(rfqs), msg=msg)

        actual = self._get_supplier_products(rfqs)
        expected = {
            self.env.ref("base.res_partner_3"): [self._kitchenset, self._blankets],
            self.env.ref("base.res_partner_2"): [self._kitchenset],
            self.env.ref("base.res_partner_4"): [self._blankets],
        }

        self.assertDictEqual(expected, dict(actual))

        msg = "Expected 1 messages, got: %d" % len(self._requisition1.message_ids)
        self.assertEquals(1, len(self._requisition1.message_ids), msg=msg)

    def _get_supplier_products(self, rfqs):
        return {
            rfq.partner_id: [line.product_id for line in rfq.order_line] for rfq in rfqs
        }

    def test_auto_rfq_from_suppliers_no_supplier(self):
        rfqs = self._requisition2.auto_rfq_from_suppliers()

        msg = "Expected 2 distinct RFQs, got %r" % rfqs
        self.assertEqual(2, len(rfqs), msg=msg)

        actual = self._get_supplier_products(rfqs)
        expected = {
            self.env.ref("base.res_partner_3"): [self._blankets],
            self.env.ref("base.res_partner_4"): [self._blankets],
        }

        self.assertDictEqual(expected, dict(actual))
        self.assertEquals(2, len(self._requisition2.message_ids))

        found = False
        for msg in self._requisition2.message_ids:
            if msg.body and "RFQ generation" in msg.body:
                self.assertIn("Tarpaulin", msg.body)
                found = True

        self.assertTrue(found, msg="No message about missing supplier found")
