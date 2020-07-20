# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseWorkAcceptanceEvaluation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Config = self.env["res.config.settings"]
        self.WorkAcceptance = self.env["work.acceptance"]
        self.res_partner = self.env.ref("base.res_partner_3")
        self.employee = self.env.ref("base.user_demo")
        self.main_company = self.env.ref("base.main_company")
        self.score = self.env.ref("purchase_work_acceptance_evaluation.score_on_time")
        self.evaluation_id_1 = self.env.ref(
            "purchase_work_acceptance_evaluation.case_name_01"
        )
        self.evaluation_id_2 = self.env.ref(
            "purchase_work_acceptance_evaluation.case_name_02"
        )
        self.date_now = fields.Datetime.now()

        # Enable WA Evaluation
        with Form(self.Config) as c:
            c.group_enable_eval_on_wa = True
            c.save()
        self.Config.create({"group_enable_eval_on_wa": True}).execute()

    def _create_wa(self, case_id, score_id):
        wa_id = self.WorkAcceptance.create(
            {
                "partner_id": self.res_partner.id,
                "responsible_id": self.employee.id,
                "date_due": self.date_now,
                "date_receive": self.date_now,
                "company_id": self.main_company.id,
                "evaluation_result_ids": [
                    (0, 0, {"case_id": case_id, "score_id": score_id},)
                ],
            }
        )
        return wa_id

    def test_01_wa_check_state_required(self):
        # Check Create WA without score
        with self.assertRaises(UserError) as exc:
            work_acceptance = self._create_wa(self.evaluation_id_1.id, False)
        self.assertEqual(
            exc.exception.name, "Please evaluate - %s" % self.evaluation_id_1.name
        )
        work_acceptance = self._create_wa(self.evaluation_id_1.id, self.score.id)
        work_acceptance._default_evaluation_result_ids()
        work_acceptance.evaluation_result_ids.score_id.name_get()

        self.assertEqual(
            work_acceptance.evaluation_result_ids.case_id, self.evaluation_id_1
        )
        self.assertEqual(work_acceptance.evaluation_result_ids.score_id, self.score)
        work_acceptance.evaluation_result_ids.write(
            {"case_id": self.evaluation_id_2.id}
        )
        work_acceptance.evaluation_result_ids._onchange_evaluation_id()
        self.assertFalse(work_acceptance.evaluation_result_ids.score_id)
