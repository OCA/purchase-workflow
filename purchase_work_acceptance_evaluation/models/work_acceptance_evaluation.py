# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkAcceptanceEvaluation(models.Model):
    _name = "work.acceptance.evaluation"
    _description = "Work Acceptance Evaluation"

    name = fields.Char(
        string="Case Name",
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
    state_required = fields.Selection(
        selection=[("draft", "Draft"), ("accept", "Accepted")],
        string="State Required",
        help="Status of Work Acceptance that user need to fill the evaluation",
    )
    score_ids = fields.One2many(
        comodel_name="work.acceptance.evaluation.score",
        inverse_name="evaluation_id",
        string="Score",
    )


class WorkAcceptanceEvaluationScore(models.Model):
    _name = "work.acceptance.evaluation.score"
    _description = "Work Acceptance Evaluation Score"
    _order = "score"

    name = fields.Char(
        string="Values",
        required=True,
    )
    evaluation_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation",
        string="Case Name",
    )
    score = fields.Integer(
        string="Score",
    )

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "{} ({})".format(rec.name, rec.score)))
        return result
