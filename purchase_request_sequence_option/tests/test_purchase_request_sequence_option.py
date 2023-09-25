# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseRequestSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestSequenceOption, self).setUp()
        self.PurchaseRequest = self.env["purchase.request"]
        self.pr_vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.env.ref("product.product_product_13").id,
                        "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                        "product_qty": 5.0,
                    },
                ),
            ],
        }
        self.pr_seq_opt = self.env.ref(
            "purchase_request_sequence_option.purchase_request_sequence_option"
        )

    def test_purchase_request_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.pr_seq_opt.use_sequence_option = True
        self.pr = self.PurchaseRequest.create(self.pr_vals.copy())
        self.assertIn("PR-1", self.pr.name)
        self.pr_copy = self.pr.copy()
        self.assertIn("PR-1", self.pr_copy.name)
        # Without sequence option
        self.pr_seq_opt.use_sequence_option = False
        self.pr = self.PurchaseRequest.create(self.pr_vals.copy())
        self.assertNotIn("PR-1", self.pr.name)
        self.pr_copy = self.pr.copy()
        self.assertNotIn("PR-1", self.pr_copy.name)
