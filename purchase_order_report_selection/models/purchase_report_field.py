from lxml import etree

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class PurchaseReportField(models.Model):
    _name = "purchase.report.field"
    _inherit = ["base.report.field"]
    _description = "Purchase report field"

    is_show_rfq = fields.Boolean("RFQ")
    is_show_po = fields.Boolean("PO")

    po_line_report_template_id = fields.Many2one("po.line.report.template")
    purchase_order_id = fields.Many2one("purchase.order")

    @api.model
    def _domain_field_id(self):
        if self._name == "purchase.report.field":
            base_domain = [
                ("model", "=", "purchase.order.line"),
                ("name", "in", self._get_form_fields()),
            ]
            return base_domain
        return super()._domain_field_id()

    @api.model
    def _get_form_fields(self):
        view = self.env.ref("purchase.purchase_order_form")
        form_data = self.env.user.fields_view_get(view_id=view.id)
        form_fields = set()
        if form_data.get("arch"):
            for item in etree.fromstring(form_data["arch"]).xpath(
                "//field[@name='order_line']/tree/field"
            ):
                if item.attrib.get("modifiers"):
                    modifiers = (
                        item.attrib["modifiers"]
                        .replace("true", "True")
                        .replace("false", "False")
                    )
                    item_data = safe_eval(modifiers, {})
                    if not item_data.get("column_invisible"):
                        form_fields.add(item.attrib.get("name"))
                elif not item.attrib.get("invisible", False):
                    form_fields.add(item.attrib.get("name"))
        return list(form_fields)

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
