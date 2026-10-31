# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

import xlsxwriter

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base_import.models.base_import import ImportValidationError

TEMPLATE_FILENAME = "purchase_order_line_import_template.xlsx"


class PurchaseOrderLineImport(models.TransientModel):
    _name = "purchase.order.line.import"
    _description = "Purchase Order Line Import"

    order_id = fields.Many2one(
        comodel_name="purchase.order",
        required=True,
        ondelete="cascade",
    )
    file = fields.Binary(attachment=False)
    file_name = fields.Char()
    template_file = fields.Binary(attachment=False, readonly=True)

    def _get_import_columns(self):
        return [
            {
                "key": "default_code",
                "label": self.env._("Internal Reference"),
                "help": self.env._("Internal reference of the product to purchase."),
                "required": True,
            },
            {
                "key": "product_qty",
                "label": self.env._("Quantity"),
                "help": self.env._(
                    "Quantity to purchase, in the purchase unit of measure."
                ),
                "required": True,
            },
            {
                "key": "name",
                "label": self.env._("Description"),
                "help": self.env._(
                    "Line description. Leave empty to use the default one."
                ),
                "required": False,
            },
            {
                "key": "price_unit",
                "label": self.env._("Unit Price"),
                "help": self.env._("Unit price. Leave empty to use the vendor price."),
                "required": False,
            },
            {
                "key": "analytic_account",
                "label": self.env._("Analytic Account"),
                "help": self.env._(
                    "Code or name of the analytic account the whole line is "
                    "distributed to."
                ),
                "required": False,
            },
        ]

    @api.model
    def _normalize_header(self, header):
        return " ".join(str(header).split()).casefold()

    def _get_column_key_by_header(self):
        key_by_header = {}
        for wizard in (self, self.with_context(lang="en_US")):
            for column in wizard._get_import_columns():
                for header in (column["key"], column["label"]):
                    key_by_header[self._normalize_header(header)] = column["key"]
        return key_by_header

    def _get_header_keys(self, header_row):
        key_by_header = self._get_column_key_by_header()
        keys = []
        errors = []
        for header in header_row:
            normalized_header = self._normalize_header(header)
            key = key_by_header.get(normalized_header, False)
            if normalized_header and not key:
                errors.append(self.env._('Unknown column "%s".', header))
            keys.append(key)
        for column in self._get_import_columns():
            count = keys.count(column["key"])
            if count > 1:
                errors.append(
                    self.env._('Column "%s" appears more than once.', column["label"])
                )
            elif not count and column["required"]:
                errors.append(
                    self.env._('Required column "%s" is missing.', column["label"])
                )
        if errors:
            raise UserError("\n".join(errors))
        return keys

    def _read_file_rows(self):
        self.ensure_one()
        if not self.file:
            raise UserError(self.env._("Please select a file to import."))
        importer = self.env["base_import.import"].create(
            {
                "res_model": "purchase.order.line",
                "file": base64.b64decode(self.file),
                "file_name": self.file_name,
            }
        )
        try:
            __, rows = importer._read_file(
                {"quoting": '"', "separator": "", "encoding": ""}
            )
        except (ImportValidationError, ValueError) as error:
            raise UserError(str(error)) from error
        return rows

    def _get_rows_data(self):
        header_row, *data_rows = self._read_file_rows() or [[]]
        keys = self._get_header_keys(header_row)
        if not data_rows:
            raise UserError(self.env._("The file has no lines to import."))
        return [
            (
                row_number,
                {
                    key: str(value).strip()
                    for key, value in zip(keys, row, strict=False)
                    if key
                },
            )
            for row_number, row in enumerate(data_rows, start=2)
        ]

    @api.model
    def _parse_float(self, value, label):
        data = [[value]]
        options = {
            "float_thousand_separator": " ",
            "float_decimal_separator": "," if "," in value else ".",
        }
        try:
            self.env["base_import.import"]._parse_float_from_data(
                data, 0, label, options
            )
            return float(data[0][0])
        except (ImportValidationError, ValueError) as error:
            raise UserError(
                self.env._(
                    '%(label)s: "%(value)s" is not a valid number.',
                    label=label,
                    value=value,
                )
            ) from error

    def _get_product_domain(self, row):
        return [
            ("default_code", "=", row["default_code"]),
            ("purchase_ok", "=", True),
            ("company_id", "in", [False, self.order_id.company_id.id]),
        ]

    def _get_product(self, row):
        if not row.get("default_code"):
            raise UserError(self.env._("The internal reference is required."))
        products = self.env["product.product"].search(
            self._get_product_domain(row), limit=2
        )
        if not products:
            raise UserError(
                self.env._(
                    'No purchasable product found with internal reference "%s".',
                    row["default_code"],
                )
            )
        if len(products) > 1:
            raise UserError(
                self.env._(
                    'Several products found with internal reference "%s".',
                    row["default_code"],
                )
            )
        return products

    def _get_product_qty(self, row):
        if not row.get("product_qty"):
            raise UserError(self.env._("The quantity is required."))
        product_qty = self._parse_float(row["product_qty"], self.env._("Quantity"))
        if product_qty <= 0:
            raise UserError(self.env._("The quantity must be greater than zero."))
        return product_qty

    def _get_analytic_account_domain(self, row):
        return [
            "|",
            ("code", "=", row["analytic_account"]),
            ("name", "=", row["analytic_account"]),
            ("company_id", "in", [False, self.order_id.company_id.id]),
        ]

    def _get_analytic_distribution(self, row):
        accounts = self.env["account.analytic.account"].search(
            self._get_analytic_account_domain(row), limit=2
        )
        if not accounts:
            raise UserError(
                self.env._(
                    'No analytic account found for "%s".', row["analytic_account"]
                )
            )
        if len(accounts) > 1:
            raise UserError(
                self.env._(
                    'Several analytic accounts found for "%s".', row["analytic_account"]
                )
            )
        return {str(accounts.id): 100.0}

    def _prepare_order_line_vals(self, row):
        vals = {
            "order_id": self.order_id.id,
            "product_id": self._get_product(row).id,
            "product_qty": self._get_product_qty(row),
        }
        if row.get("name"):
            vals["name"] = row["name"]
        if row.get("price_unit"):
            vals["price_unit"] = self._parse_float(
                row["price_unit"], self.env._("Unit Price")
            )
        if row.get("analytic_account"):
            vals["analytic_distribution"] = self._get_analytic_distribution(row)
        return vals

    def _create_order_lines(self, vals_list):
        sequence = max(self.order_id.order_line.mapped("sequence"), default=0) + 1
        for index, vals in enumerate(vals_list):
            vals["sequence"] = sequence + index
        return self.env["purchase.order.line"].create(vals_list)

    def action_import(self):
        self.ensure_one()
        self.order_id._check_order_line_import_state()
        vals_list = []
        errors = []
        for row_number, row in self._get_rows_data():
            try:
                vals_list.append(self._prepare_order_line_vals(row))
            except UserError as error:
                errors.append(
                    self.env._(
                        "Row %(row)s: %(error)s", row=row_number, error=error.args[0]
                    )
                )
        if errors:
            raise UserError(
                "\n".join([self.env._("No line has been imported."), *errors])
            )
        lines = self._create_order_lines(vals_list)
        self.order_id.message_post(
            body=self.env._(
                "Lines imported from %(file)s: %(count)s.",
                count=len(lines),
                file=self.file_name,
            )
        )
        return {"type": "ir.actions.act_window_close"}

    def _generate_template(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet(self.env._("Lines"))
        optional_format = workbook.add_format({"bold": True, "bg_color": "#D9D9D9"})
        required_format = workbook.add_format({"bold": True, "bg_color": "#F4B183"})
        for col, column in enumerate(self._get_import_columns()):
            worksheet.write(
                0,
                col,
                column["label"],
                required_format if column["required"] else optional_format,
            )
            worksheet.write_comment(0, col, column["help"])
            worksheet.set_column(col, col, max(len(column["label"]) + 4, 18))
        worksheet.freeze_panes(1, 0)
        workbook.close()
        return output.getvalue()

    def action_download_template(self):
        self.ensure_one()
        self.template_file = base64.b64encode(self._generate_template())
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/template_file/"
            f"{TEMPLATE_FILENAME}?download=true",
            "target": "download",
        }
