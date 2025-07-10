# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkAcceptanceEvaluationReport(models.Model):
    _name = "work.acceptance.evaluation.report"
    _description = "Work Acceptance Evaluation Report"
    _order = "partner_id,date_accept"
    _auto = False

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
    )
    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
    )
    wa_state = fields.Selection(
        [("draft", "Draft"), ("accept", "Accepted"), ("cancel", "Cancelled")],
        string="Status",
    )
    date_accept = fields.Datetime(
        string="Accepted Date",
    )
    case_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation",
        string="Case Name",
    )
    score_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation.score",
        string="Score ID",
    )
    score = fields.Integer()
    note = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
    )

    def _select(self):
        return """
            select result.id, wa.partner_id, result.wa_id,
                   wa.state as wa_state,
                   wa.date_accept, result.case_id,
                   result.score_id, score.score, result.note,
                   wa.company_id
        """

    def _from(self):
        return """
            from work_acceptance_evaluation_result result
            join work_acceptance_evaluation_score score on score.id = result.score_id
            left join work_acceptance wa on result.wa_id = wa.id
        """

    @property
    def _table_query(self):
        return "%s %s" % (self._select(), self._from())
