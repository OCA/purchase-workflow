# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseIsolatedRFQ(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_2")
        vals = {"partner_id": self.partner.id, "order_sequence": False}
        self.rfq = self.env["purchase.order"].create(vals)

    def test_quotation_convert_to_order(self):
        """ Expect.
        - When quotation is converted to order
          - Status chagned to 'done'
          - New purchase.order of order_sequence = True created
        - RFQ can reference to Order and Order can reference to RFQ too
        """
        self.rfq.action_convert_to_order()
        po = self.rfq.purchase_order_id
        self.assertEqual(self.rfq.state, "done")
        self.assertFalse(self.rfq.order_sequence)
        self.assertTrue(po.order_sequence)
        self.assertEqual(po.state, "purchase")
        self.assertEqual(po.partner_id, self.partner)
        self.assertEqual(po.quote_id, self.rfq)
        # Exceptions Case
        with self.assertRaises(UserError) as e:
            po.action_convert_to_order()
        error_message = "Only quotation can convert to order"
        self.assertEqual(e.exception.name, error_message)
