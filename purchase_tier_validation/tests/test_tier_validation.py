# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


class TestPurchaseTierValidation(CommonTierValidation):
    def test_01_tier_definition_models(self):
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("purchase.order", res)
