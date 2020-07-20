# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WorkAcceptance(models.Model):
    _inherit = "work.acceptance"
    _description = "Work Acceptance"

    evaluation_result_ids = fields.One2many(
        comodel_name="work.acceptance.evaluation.result",
        inverse_name="wa_id",
        string="Evaluation Results",
        default=lambda self: self._default_evaluation_result_ids(),
    )

    def _default_evaluation_result_ids(self):
        eval_result = self.env["work.acceptance.evaluation"].search([])
        result = [(0, 0, {"case_id": rec.id}) for rec in eval_result]
        return result

    @api.constrains("evaluation_result_ids")
    def _check_evaluation(self):
        if self.user_has_groups(
            "purchase_work_acceptance_evaluation.group_enable_eval_on_wa"
        ):
            Evaluation = self.env["work.acceptance.evaluation"]
            # i.e., {1: 'accept', 2: 'draft'}
            case_state = {c.id: c.state_required for c in Evaluation.search([])}
            for result in self.mapped("evaluation_result_ids"):
                if case_state[result.case_id.id] == self.state and not result.score_id:
                    raise UserError(_("Please evaluate - %s") % result.case_id.name)


class WorkAcceptanceEvaluationResult(models.Model):
    _name = "work.acceptance.evaluation.result"
    _description = "Work Acceptance Evaluation Result"

    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
        required=True,
        index=True,
        ondelete="cascade",
    )
    case_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation", string="Case Name", required=True,
    )
    score_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation.score",
        string="Score",
        domain="[('evaluation_id', '=', case_id)]",
    )

    @api.onchange("case_id")
    def _onchange_evaluation_id(self):
        self.score_id = False
