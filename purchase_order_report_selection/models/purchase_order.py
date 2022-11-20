from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    report_field_ids = fields.One2many("purchase.report.field", "purchase_order_id")

    @api.model
    def create(self, value):
        result = super(PurchaseOrder, self).create(value)
        result.add_report_fields()
        return result

    @api.model
    def _default_report_po_fields(self):
        """This method returns default fields is using in PO reports

        Returns:
            list: fields in PO reports
        """
        return [
            "name",
            "taxes_id",
            "date_planned",
            "product_qty",
            "product_uom",
            "price_unit",
            "price_subtotal",
        ]

    @api.model
    def _default_report_rfq_fields(self):
        """This method returns default fields is using in RFQ reports

        Returns:
            list: fields in RFQ reports
        """
        return ["name", "date_planned", "product_qty", "product_uom"]

    @api.model
    def default_all_report_fields(self):
        """Combines the PO and RFQ fields"""
        default_fields_po = self._default_report_po_fields()
        default_fields_rfq = self._default_report_rfq_fields()
        return list(set(default_fields_po + default_fields_rfq))

    @api.model
    def get_all_report_fields(self):
        """This method returns default fields is using in PO and RFQ reports"""
        return self.env["ir.model.fields"].search(
            [
                ("model", "=", "purchase.order.line"),
                ("name", "in", self.default_all_report_fields()),
            ]
        )

    @api.model
    def generate_data(self):
        """Generates data to add to records

        Returns:
            list: generated data inside the list
        """
        default_fields_po = self._default_report_po_fields()
        default_fields_rfq = self._default_report_rfq_fields()
        field_ids = self.get_all_report_fields()
        data_values = list(
            map(
                lambda field: (
                    0,
                    0,
                    {
                        "field_id": field.id,
                        "is_show_po": field.name in default_fields_po,
                        "is_show_rfq": field.name in default_fields_rfq,
                    },
                ),
                field_ids,
            )
        )

        return data_values

    def add_report_fields(self):
        """Adds report fields to records"""
        data = self.generate_data()
        for record in self:
            record.report_field_ids = data
