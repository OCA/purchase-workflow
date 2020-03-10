# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseRequisitionTierValidation(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.tier_definition = self.env["tier.definition"]

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "purchase.requisition",
            self.tier_definition._get_tier_validation_model_names(),
        )
