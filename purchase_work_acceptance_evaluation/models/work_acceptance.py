# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WorkAcceptance(models.Model):
    _inherit = "work.acceptance"

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

    def button_accept(self, force=False):
        for rec in self:
            rec._check_evaluation()
        return super().button_accept(force=force)

    def _check_evaluation(self):
        self.ensure_one()
        if self.user_has_groups(
            "purchase_work_acceptance_evaluation.group_enable_eval_on_wa"
        ):
            missing_results = self.evaluation_result_ids.filtered(
                lambda l: l.case_id.state_required == self.state and not l.score_id
            )
            if missing_results:
                cases = missing_results.mapped("case_id")
                raise UserError(
                    _("Please evaluate - %s") % ", ".join(cases.mapped("name"))
                )


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
        comodel_name="work.acceptance.evaluation",
        string="Case Name",
        required=True,
    )
    score_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation.score",
        string="Score",
        domain="[('evaluation_id', '=', case_id)]",
    )
    note = fields.Char()
    editable = fields.Boolean(compute="_compute_editable")

    @api.depends("case_id")
    def _compute_editable(self):
        for rec in self:
            rec.editable = (
                True
                if not rec.case_id.state_required
                else rec.wa_id.state == rec.case_id.state_required
            )
