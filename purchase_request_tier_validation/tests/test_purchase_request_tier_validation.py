# Copyright 2017-2020 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestPurchaseRequest(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # common models
        cls.purchase_request = cls.env["purchase.request"]
        cls.tier_definition = cls.env["tier.definition"]

    def test_get_under_validation_exceptions(self):
        self.assertIn(
            "route_id", self.purchase_request._get_under_validation_exceptions()
        )

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "purchase.request", self.tier_definition._get_tier_validation_model_names()
        )
