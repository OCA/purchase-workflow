# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseRequisitionSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequisitionSequenceOption, self).setUp()
        self.PurchaseRequisition = self.env["purchase.requisition"]
        self.product_id = self.env.ref("product.product_product_6")
        self.te_vals = {
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id.id,
                        "product_uom_id": self.product_id.uom_po_id.id,
                        "product_qty": 5.0,
                    },
                ),
            ],
        }
        self.te_seq_opt = self.env.ref(
            "purchase_requisition_sequence_option.purchase_requisition_sequence_option"
        )

    def test_purchase_requisition_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.te_seq_opt.use_sequence_option = True
        self.te = self.PurchaseRequisition.create(self.te_vals.copy())
        self.te.action_in_progress()
        self.assertIn("TE-1", self.te.name)
        self.te_copy = self.te.copy()
        self.te_copy.action_in_progress()
        self.assertIn("TE-1", self.te_copy.name)
        # Without sequence option
        self.te_seq_opt.use_sequence_option = False
        self.te = self.PurchaseRequisition.create(self.te_vals.copy())
        self.te.action_in_progress()
        self.assertNotIn("TE-1", self.te.name)
        self.te_copy = self.te.copy()
        self.te_copy.action_in_progress()
        self.assertNotIn("TE-1", self.te_copy.name)
