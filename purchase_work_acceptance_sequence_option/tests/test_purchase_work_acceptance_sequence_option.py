# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseWorkAcceptanceSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseWorkAcceptanceSequenceOption, self).setUp()
        self.WorkAcceptance = self.env["work.acceptance"]
        self.product_id = self.env.ref("product.product_product_6")
        self.date_now = fields.Datetime.now()
        self.wa_vals = {
            "partner_id": self.env.ref("base.res_partner_1").id,
            "date_due": self.date_now,
            "wa_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id.name,
                        "product_id": self.product_id.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                ),
            ],
        }
        self.wa_seq_opt = self.env.ref(
            "purchase_work_acceptance_sequence_option.work_acceptance_sequence_option"
        )

    def test_purchase_work_acceptance_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.wa_seq_opt.use_sequence_option = True
        self.wa = self.WorkAcceptance.create(self.wa_vals.copy())
        self.assertIn("WA-1", self.wa.name)
        self.wa_copy = self.wa.copy()
        self.assertIn("WA-1", self.wa_copy.name)
        # Without sequence option
        self.wa_seq_opt.use_sequence_option = False
        self.wa = self.WorkAcceptance.create(self.wa_vals.copy())
        self.assertNotIn("WA-1", self.wa.name)
        self.wa_copy = self.wa.copy()
        self.assertNotIn("WA-1", self.wa_copy.name)
