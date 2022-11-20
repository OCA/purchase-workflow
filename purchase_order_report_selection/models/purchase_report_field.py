from odoo import api, fields, models


class PurchaseReportField(models.Model):
    _name = "purchase.report.field"
    _inherit = ["base.report.field"]
    _description = "Purchase report field"

    is_show_rfq = fields.Boolean("RFQ")
    is_show_po = fields.Boolean("PO")

    purchase_order_id = fields.Many2one("purchase.order")

    @api.model
    def _domain_field_id(self):
        if self._name == "purchase.report.field":
            purchase_order_fields = self.env[
                "purchase.order"
            ].default_all_report_fields()
            base_domain = [
                ("model", "=", "purchase.order.line"),
                ("name", "in", purchase_order_fields),
            ]
            return base_domain
        return super()._domain_field_id()

    def count_rfq_fields(self):
        """This method returns the number of marked fields to output in the RFQ report
        Returns:
            int: Number of marked fields
        """
        return len(self.filtered(lambda r: r.is_show_rfq is True))

    def count_po_fields(self):
        """This method returns the number of marked fields to output in the PO report

        Returns:
            int: Number of marked fields
        """
        return len(self.filtered(lambda r: r.is_show_po is True))
