from odoo import fields, models


class POLineReportTemplate(models.Model):
    _name = "po.line.report.template"

    name = fields.Char()
    report_field_ids = fields.One2many(
        "purchase.report.field", "po_line_report_template_id"
    )
