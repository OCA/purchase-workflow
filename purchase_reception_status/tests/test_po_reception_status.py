from odoo.tests.common import TransactionCase


class TestReceptionStatus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up test data for all test methods.
        """
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        cls.purchaseorder = cls.env["purchase.order"]
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        # Create PO once with static ordered quantity
        cls.po = cls.purchaseorder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 5,
                            "product_uom": cls.uom_unit.id,
                            "price_unit": 100.0,
                            "name": "Test Purchase Line",
                        },
                    )
                ],
            }
        )
        cls.po.button_confirm()

    def _update_qty_received(self, qty):
        """Helper to update received quantity."""
        for line in self.po.order_line:
            line.qty_received = qty

    def test_status_nothing_received(self):
        """
        Test that the reception_status is 'no' when no product quantity has been
        received.
        """
        self._update_qty_received(0)
        self.assertEqual(self.po.reception_status, "no")

    def test_status_partial_received(self):
        """
        Test that the reception_status is 'partial' when only part of the ordered
        quantity is received.
        """
        self._update_qty_received(2)
        self.assertEqual(self.po.reception_status, "partial")

    def test_status_fully_received(self):
        """
        Test that the reception_status is 'received' when the full ordered quantity
        is received.
        """
        self._update_qty_received(5)
        self.assertEqual(self.po.reception_status, "received")

    def test_force_received(self):
        """
        Test that the reception_status becomes 'received' when 'force_received' is set
        to True even if no quantity was received.
        """
        self._update_qty_received(0)
        self.po.button_done()
        self.po.write({"force_received": True})
        self.assertEqual(self.po.reception_status, "received")
