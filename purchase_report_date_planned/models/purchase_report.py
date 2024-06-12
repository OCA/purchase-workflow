from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    date_planned = fields.Datetime(compute="_compute_date_planned", store=True)

    def _compute_date_planned(self):
        for record in self:
            order_line = record.order_id.order_line.filtered(
                lambda r: r.product_id == record.product_id
            )
            record.date_planned = order_line.date_planned

    def _select(self):
        select_str = super(PurchaseReport, self)._select()
        return select_str + ", l.date_planned as date_planned"

    def _group_by(self):
        group_by_str = super(PurchaseReport, self)._group_by()
        return group_by_str + ", l.date_planned"
