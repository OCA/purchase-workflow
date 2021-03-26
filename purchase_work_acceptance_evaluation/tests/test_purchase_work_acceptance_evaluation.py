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
        # Enable WA Evaluation
        with Form(self.Config) as c:
            c.group_enable_eval_on_wa = True
            c.save()
        self.Config.create({"group_enable_eval_on_wa": True}).execute()

    def test_01_wa_check_state_required(self):
        """Creat new WA with 3 evaluation criterias, I expect that user must
        fill in the evaluation based on state_requried"""
        with Form(self.WorkAcceptance) as f:
            f.partner_id = self.res_partner
            f.responsible_id = self.employee
            f.date_due = fields.Datetime.now()
            f.date_receive = fields.Datetime.now()
            f.company_id = self.main_company

        work_acceptance = f.save()
        self.assertEqual(len(work_acceptance.evaluation_result_ids), 3)
        # 1st criteria state_required = accept, 2nd and 3rd state_required = draft
        eval_resuls = work_acceptance.evaluation_result_ids
        eval_resuls[0].case_id.state_required = "accept"
        eval_resuls[1].case_id.state_required = "draft"
        eval_resuls[2].case_id.state_required = "draft"
        # User need to fill in 2nd and 3rd criteria
        with self.assertRaises(UserError) as e:
            work_acceptance.button_accept()
        self.assertEqual(
            e.exception.args[0],
            "Please evaluate - %s"
            % ", ".join([eval_resuls[1].case_id.name, eval_resuls[2].case_id.name]),
        )
        # Set score and accept again
        eval_resuls[1].score_id = eval_resuls[1].case_id.score_ids[0]
        eval_resuls[2].score_id = eval_resuls[2].case_id.score_ids[0]
        work_acceptance.button_accept()
        self.assertEqual(work_acceptance.state, "accept")

    def test_02_wa_evaluation_score_name_get(self):
        with Form(self.WorkAcceptance) as f:
            f.partner_id = self.res_partner
            f.responsible_id = self.employee
            f.date_due = fields.Datetime.now()
            f.date_receive = fields.Datetime.now()
            f.company_id = self.main_company

        work_acceptance = f.save()
        score_resuls = work_acceptance.mapped("evaluation_result_ids.case_id.score_ids")
        name = "{} ({})".format(score_resuls[0].name, score_resuls[0].score)
        res = score_resuls[0].name_get()
        self.assertEqual(len(res), 1)
        rec_id, name_get = res[0]
        self.assertEqual(score_resuls[0].id, rec_id)
        self.assertIn(name, name_get)
