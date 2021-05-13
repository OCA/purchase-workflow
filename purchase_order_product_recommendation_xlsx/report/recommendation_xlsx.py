# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class RecommendationXlsx(models.AbstractModel):
    _name = "report.purchase_order_product_recommendation_xlsx.summary"
    _inherit = "report.report_xlsx.abstract"
    _description = "Abstract model to export as xlsx the product recommendation"

    def _get_lang(self, user_id):
        lang_code = self.env["res.users"].browse(user_id).lang
        return self.env["res.lang"]._lang_get(lang_code)

    def _create_product_pricelist_sheet(self, workbook, book, field_names):
        title_format = workbook.add_format(
            {"bold": 1, "align": "left", "valign": "vjustify"}
        )
        header_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vjustify",
                "fg_color": "#F2F2F2",
            }
        )
        lang = self._get_lang(book.create_uid.id)
        date_format = lang.date_format.replace("%d", "dd")
        date_format = date_format.replace("%m", "mm")
        date_format = date_format.replace("%Y", "YYYY")
        date_format = date_format.replace("/", "-")
        date_format = workbook.add_format({"num_format": date_format})
        sheet = workbook.add_worksheet(_("PRODUCTS"))
        sheet.set_column("A:A", 45)
        sheet.set_column("B:H", 15)
        # Title construction
        sheet.write("A1", _("Recommended products for supplier:"), title_format)
        sheet.write("B1", book.order_id.partner_id.name)
        sheet.write("A3", _("Date begin:"), title_format)
        sheet.write("B3", book.date_begin, date_format)
        sheet.write("D3", _("Date end:"), title_format)
        sheet.write("E3", book.date_end, date_format)
        # Header construction
        sheet.write(5, 0, _("Product"), header_format)
        next_col = 1
        line_obj = self.env["purchase.order.recommendation.line"]
        for name in field_names:
            sheet.write(5, next_col, line_obj._fields[name].string, header_format)
            next_col += 1
        sheet.write(5, next_col, _("Qty"), header_format)
        return sheet

    def _fill_data(self, workbook, sheet, book, field_names):
        decimal_format = workbook.add_format({"num_format": "0.00"})
        lang = self._get_lang(book.create_uid.id)
        date_format = lang.date_format.replace("%d", "dd")
        date_format = date_format.replace("%m", "mm")
        date_format = date_format.replace("%Y", "YYYY")
        date_format = date_format.replace("/", "-")
        date_format = workbook.add_format({"num_format": date_format})
        next_row = 6
        line_obj = self.env["purchase.order.recommendation.line"]
        for line in book.line_ids:
            if line.currency_id.position == "after":
                monetary_format = workbook.add_format(
                    {"num_format": "0.00 %s" % line.currency_id.symbol}
                )
            else:
                monetary_format = workbook.add_format(
                    {"num_format": "%s 0.00" % line.currency_id.symbol}
                )
            sheet.write(next_row, 0, line.product_id.display_name)
            next_col = 1
            for name in field_names:
                if line_obj._fields[name].type == "monetary":
                    sheet.write(next_row, next_col, line[name], monetary_format)
                elif line_obj._fields[name].type in ["date", "datetime"]:
                    sheet.write(next_row, next_col, line[name], date_format)
                else:
                    sheet.write(next_row, next_col, line[name], decimal_format)
                next_col += 1
            sheet.write(next_row, next_col, line.units_included, decimal_format)
            next_row += 1
        return sheet

    def generate_xlsx_report(self, workbook, data, objects):
        book = objects[0]
        field_names = sorted(
            book.line_ids.fields_get().keys() - self.get_restricted_fields()
        )
        sheet = self._create_product_pricelist_sheet(workbook, book, field_names)
        sheet = self._fill_data(workbook, sheet, book, field_names)

    def get_restricted_fields(self):
        return {
            "currency_id",
            "partner_id",
            "product_id",
            "units_included",
            "times_delivered",
            "times_received",
            "wizard_id",
            "purchase_line_id",
            "is_modified",
            "id",
            "display_name",
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
            "__last_update",
        }
