# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.tests.common import TransactionCase


# We use TransactionCase instead of CommonTierValidation to avoid
# unnecessary test setups (like creating companies and dummy models)
# which can cause NotNullViolation database errors when modules like
# hr_timesheet are installed in the same environment.
class TestPurchaseTierValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_01_tier_definition_models(self):
        res = self.env["tier.definition"]._get_tier_validation_model_names()
        self.assertIn("purchase.order", res)
