# Copyright 2024 Ecosoft Co., Ltd. (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderSequenceOption, self).setUp()
        self.partner_1 = self.env.ref("base.res_partner_1")
        self.partner_2 = self.env.ref("base.res_partner_address_1")
        self.purchase_seq_option = self.env.ref(
            "purchase_order_sequence_option.purchase_sequence_option"
        )

    def _create_po(self, partner):
        purchase_form = Form(self.env["purchase.order"])
        purchase_form.partner_id = partner
        purchase_order = purchase_form.save()
        return purchase_order

    def test_purchase_order_sequence_options(self):
        """Test different kind of sequences"""
        self.purchase_seq_option.use_sequence_option = True
        # Company
        self.purchase_order_1 = self._create_po(self.partner_1)
        self.assertIn("POC", self.purchase_order_1.name)
        old_name = self.purchase_order_1.name
        self.purchase_order_1.button_confirm()
        self.assertEqual(old_name, self.purchase_order_1.name)
        # Individual
        self.purchase_order_2 = self._create_po(self.partner_2)
        self.assertIn("POI", self.purchase_order_2.name)
        old_name = self.purchase_order_2.name
        self.purchase_order_2.button_confirm()
        self.assertEqual(old_name, self.purchase_order_2.name)
        self.purchase_order_2.button_cancel()
        self.purchase_order_2.button_draft()
        self.purchase_order_2.button_confirm()
        self.assertEqual(old_name, self.purchase_order_2.name)
