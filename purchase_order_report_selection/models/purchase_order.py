from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    po_line_report_template_id = fields.Many2one("po.line.report.template")
    report_field_ids = fields.One2many("purchase.report.field", "purchase_order_id")

    @api.onchange("po_line_report_template_id")
    def _onchange_po_line_report_template(self):
        records = self._get_prepared_data(
            self.po_line_report_template_id.report_field_ids
        )
        self.report_field_ids = records

    @api.model
    def _get_prepared_data(self, data):
        return [(5, 0, 0)] + [
            (
                0,
                0,
                {
                    "field_id": field.field_id.id,
                    "is_show_po": field.is_show_po,
                    "is_show_rfq": field.is_show_rfq,
                },
            )
            for field in data
        ]

    @api.constrains("report_field_ids")
    def _check_report_field_ids(self):
        for item in self:
            if not item.po_line_report_template_id.report_field_ids:
                item.po_line_report_template_id.report_field_ids = (
                    self._get_prepared_data(item.report_field_ids)
                )
            else:
                report_fields = item.report_field_ids.filtered(
                    lambda f: f.field_id
                    not in item.po_line_report_template_id.report_field_ids.mapped(
                        "field_id"
                    )
                )
                if report_fields:
                    data = self._get_prepared_data(report_fields)
                    item.po_line_report_template_id.report_field_ids = data[1:]

    def count_rfq_fields(self):
        """This method returns the number of marked fields to output in the RFQ report
        Returns:
            int: Number of marked fields
        """
        return len(self.report_field_ids.filtered(lambda r: r.is_show_rfq is True))

    def count_po_fields(self):
        """This method returns the number of marked fields to output in the PO report

        Returns:
            int: Number of marked fields
        """
        return len(self.report_field_ids.filtered(lambda r: r.is_show_po is True))
