# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_model = cls.env["purchase.order"]
        company = cls.env.company
        company.keep_name_po = False
        company.auto_attachment_rfq = True

    def test_enumeration(self):
        order1 = self.purchase_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )

        purchase_for_quotation1_name = order1.name
        order2 = self.purchase_order_model.create(
            {"partner_id": self.env.ref("base.res_partner_1").id}
        )
        purchase_for_quotation2_name = order2.name

        self.assertRegex(purchase_for_quotation1_name, "RFQ")
        self.assertRegex(purchase_for_quotation2_name, "RFQ")
        self.assertLess(
            int(purchase_for_quotation1_name[4:]), int(purchase_for_quotation2_name[4:])
        )

        order2.button_confirm()
        order1.button_confirm()

        self.assertRegex(order1.name, "P")
        self.assertEqual(order1.rfq_number, purchase_for_quotation1_name)

        self.assertRegex(order2.name, "P")
        self.assertEqual(order2.rfq_number, purchase_for_quotation2_name)
        self.assertLess(int(order2.name[3:]), int(order1.name[3:]))

    def test_with_rfq_number(self):
        rfq_number = "rfq_number"
        order1 = self.purchase_order_model.create(
            {
                "rfq_number": rfq_number,
                "partner_id": self.env.ref("base.res_partner_1").id,
            }
        )
        purchase_for_quotation1_name = order1.name
        order1.button_confirm()

        self.assertRegex(order1.name, "P")
        self.assertEqual(order1.rfq_number, purchase_for_quotation1_name)

    def test_redudant_confirmation(self):
        order = self.purchase_order_model.create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "state": "done",
            }
        )
        # The order is never actually confirmed, so it's current name
        # is taken from the RFQ sequence.
        name_orig = order.name
        self.assertTrue(name_orig.startswith("RFQ"))
        sequence_id = self.env["ir.sequence"].search(
            [
                ("code", "=", "purchase.order"),
                ("company_id", "in", [order.company_id.id, False]),
            ]
        )
        next_name = sequence_id.get_next_char(sequence_id.number_next_actual)
        # A void call to button confirm does not waste a number
        order.button_confirm()
        self.assertEqual(order.name, name_orig)
        order.update({"state": "draft"})
        # Now the RFQ can be confirmed and a new PO number will be assigned
        order.button_confirm()
        self.assertEqual(next_name, order.name)
        self.assertEqual(order.rfq_number, name_orig)

    def test_auto_attachment_rfq(self):
        order = self.purchase_order_model.create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "state": "draft",
            }
        )
        order.button_confirm()
        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", "purchase.order"), ("res_id", "=", order.id)]
        )
        self.assertEqual(attachment.res_id, order.id)
