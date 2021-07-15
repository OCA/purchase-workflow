# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class VendorEvaluationReport(models.Model):
    _name = "vendor.evaluation.report"
    _description = "Vendor Evaluation Report"
    _order = "partner_id,date_accept"
    _auto = False

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        index=True,
    )
    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
        index=True,
    )
    date_accept = fields.Datetime(
        string="Accepted Date",
    )
    case_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation",
        string="Case Name",
        index=True,
    )
    score_id = fields.Many2one(
        comodel_name="work.acceptance.evaluation.score",
        string="Score",
        index=True,
    )
    note = fields.Char(
        string="Note",
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            create or replace view %s as (
                select result.id, wa.partner_id, result.wa_id,
                       wa.date_accept, result.case_id, result.score_id, result.note
                from work_acceptance_evaluation_result result
                left join work_acceptance wa on result.wa_id = wa.id
                where wa.state = 'accept'
            )"""
            % self._table
        )
