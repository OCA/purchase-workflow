# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseWorkAcceptanceTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tier_definition = cls.env["tier.definition"]
        cls.reviewer = new_test_user(
            cls.env,
            login="wa_reviewer",
            groups="base.group_user,purchase.group_purchase_user",
        )
        cls.tier_definition.create(
            {
                "model_id": cls.env["ir.model"]._get_id("work.acceptance"),
                "review_type": "individual",
                "reviewer_id": cls.reviewer.id,
            }
        )
        cls.work_acceptance = cls.env["work.acceptance"].create(
            {"partner_id": cls.partner.id, "date_due": fields.Datetime.now()}
        )

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "work.acceptance", self.tier_definition._get_tier_validation_model_names()
        )

    def test_tier_validation_flow(self):
        self.assertTrue(self.work_acceptance.need_validation)
        with self.assertRaises(ValidationError):
            self.work_acceptance.button_accept()
        self.work_acceptance.request_validation()
        self.assertIn(self.reviewer, self.work_acceptance.reviewer_ids)
        self.work_acceptance.with_user(self.reviewer).validate_tier()
        self.assertEqual(self.work_acceptance.validation_status, "validated")
        self.work_acceptance.invalidate_recordset(["need_validation"])
        self.work_acceptance.button_accept()
        self.assertEqual(self.work_acceptance.state, "accept")
