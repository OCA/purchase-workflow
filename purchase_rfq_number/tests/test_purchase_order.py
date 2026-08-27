# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        company = cls.env.company
        company.keep_name_po = False
        company.auto_attachment_rfq = True
        cls.partner = cls.env["res.partner"].create({"name": "RFQ Number Test Partner"})

    def test_enumeration(self):
        order1 = self.purchase_order_model.create({"partner_id": self.partner.id})

        purchase_for_quotation1_name = order1.name
        order2 = self.purchase_order_model.create({"partner_id": self.partner.id})
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
                "partner_id": self.partner.id,
            }
        )
        purchase_for_quotation1_name = order1.name
        order1.button_confirm()

        self.assertRegex(order1.name, "P")
        self.assertEqual(order1.rfq_number, purchase_for_quotation1_name)

    def test_error_confirmation_sequence(self):
        order = self.purchase_order_model.create(
            {
                "partner_id": self.partner.id,
                "state": "purchase",
            }
        )
        sequence_id = self.env["ir.sequence"].search(
            [
                ("code", "=", "purchase.order"),
                ("company_id", "in", [order.company_id.id, False]),
            ]
        )
        next_name = sequence_id.get_next_char(sequence_id.number_next_actual)
        # Re-confirming an already confirmed order is a no-op in core Odoo
        # (it doesn't raise anymore since 19.0); it must not consume/advance
        # the purchase order sequence either.
        order.button_confirm()
        order.update({"state": "draft"})
        # Now the RFQ can be confirmed
        order.button_confirm()
        self.assertEqual(next_name, order.name)

    def test_auto_attachment_rfq(self):
        order = self.purchase_order_model.create(
            {
                "partner_id": self.partner.id,
                "state": "draft",
            }
        )
        order.button_confirm()
        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", "purchase.order"), ("res_id", "=", order.id)]
        )
        self.assertEqual(attachment.res_id, order.id)
