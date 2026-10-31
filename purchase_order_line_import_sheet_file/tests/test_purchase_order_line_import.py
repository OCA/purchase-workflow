# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

import xlsxwriter

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

HEADER = [
    "Internal Reference",
    "Quantity",
    "Description",
    "Unit Price",
    "Analytic Account",
]


@tagged("post_install", "-at_install")
class TestPurchaseOrderLineImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.LineImport = cls.env["purchase.order.line.import"]
        # Instances
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product_1 = cls._create_product(default_code="TST-IMP-001")
        cls.product_2 = cls._create_product(default_code="TST-IMP-002")
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                "price": 7.5,
            }
        )
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Project",
                "code": "TST-PRJ",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.order = cls._create_purchase_order()

    @classmethod
    def _create_product(cls, **kwargs):
        vals = {
            "name": f"Test Product {kwargs.get('default_code', '')}",
            "type": "consu",
            "purchase_ok": True,
            "standard_price": 3.0,
        }
        vals.update(kwargs)
        return cls.env["product.product"].create(vals)

    @classmethod
    def _create_purchase_order(cls, **kwargs):
        vals = {"partner_id": cls.vendor.id}
        vals.update(kwargs)
        return cls.PurchaseOrder.create(vals)

    @staticmethod
    def _build_xlsx(rows):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet()
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                worksheet.write(row_index, col_index, value)
        workbook.close()
        return base64.b64encode(output.getvalue())

    def _create_wizard(self, rows=None, order=None, **kwargs):
        vals = {"order_id": (order or self.order).id}
        if rows is not None:
            vals.update(file=self._build_xlsx(rows), file_name="lines.xlsx")
        vals.update(kwargs)
        return self.LineImport.create(vals)

    def _get_reference_line(self, product, product_qty):
        order = self._create_purchase_order()
        return self.PurchaseOrderLine.create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "product_qty": product_qty,
            }
        )

    def test_open_wizard_from_order(self):
        action = self.order.action_open_line_import()
        self.assertEqual(action["res_model"], "purchase.order.line.import")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"], {"default_order_id": self.order.id})

    def test_open_wizard_from_order_line_list(self):
        action = self.PurchaseOrderLine.with_context(
            order_id=self.order.id
        ).action_open_line_import()
        self.assertEqual(action["context"], {"default_order_id": self.order.id})
        wizard = self.LineImport.with_context(**action["context"]).create({})
        self.assertEqual(wizard.order_id, self.order)

    def test_open_wizard_confirmed_order(self):
        self.order.order_line = [
            Command.create({"product_id": self.product_1.id, "product_qty": 1.0})
        ]
        self.order.button_confirm()
        with self.assertRaisesRegex(UserError, "request for quotation"):
            self.order.action_open_line_import()

    def test_download_template(self):
        wizard = self._create_wizard()
        action = wizard.action_download_template()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "download")
        self.assertIn(
            f"/web/content/purchase.order.line.import/{wizard.id}/template_file/",
            action["url"],
        )
        wizard.write({"file": wizard.template_file, "file_name": "template.xlsx"})
        self.assertEqual(wizard._read_file_rows(), [HEADER])
        with self.assertRaisesRegex(UserError, "no lines to import"):
            wizard.action_import()

    def test_import_all_columns(self):
        existing_line = self.PurchaseOrderLine.create(
            {
                "order_id": self.order.id,
                "product_id": self.product_1.id,
                "product_qty": 1.0,
                "sequence": 20,
            }
        )
        wizard = self._create_wizard(
            [
                HEADER,
                ["TST-IMP-001", 2, "Imported description", 1.13, "Test Project"],
                ["TST-IMP-002", 3.5, "Second line", "1.234,56", "TST-PRJ"],
            ]
        )
        result = wizard.action_import()
        self.assertEqual(result, {"type": "ir.actions.act_window_close"})
        new_lines = self.order.order_line - existing_line
        self.assertEqual(len(new_lines), 2)
        first_line, second_line = new_lines.sorted("sequence")
        self.assertEqual(first_line.product_id, self.product_1)
        self.assertEqual(first_line.product_qty, 2.0)
        self.assertEqual(first_line.name, "Imported description")
        self.assertAlmostEqual(first_line.price_unit, 1.13)
        self.assertEqual(
            first_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        self.assertEqual(second_line.product_id, self.product_2)
        self.assertEqual(second_line.product_qty, 3.5)
        self.assertAlmostEqual(second_line.price_unit, 1234.56)
        self.assertEqual(
            second_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        self.assertEqual(first_line.sequence, 21)
        self.assertEqual(second_line.sequence, 22)
        self.assertIn("lines.xlsx", self.order.message_ids[0].body)
        self.assertIn(": 2.", self.order.message_ids[0].body)

    def test_import_required_columns_only(self):
        wizard = self._create_wizard(
            [["Internal Reference", "Quantity"], ["TST-IMP-002", 4]]
        )
        wizard.action_import()
        line = self.order.order_line
        reference_line = self._get_reference_line(self.product_2, 4)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 4.0)
        self.assertEqual(line.name, reference_line.name)
        self.assertEqual(line.price_unit, reference_line.price_unit)
        self.assertEqual(line.price_unit, 7.5)
        self.assertEqual(
            line.analytic_distribution, reference_line.analytic_distribution
        )

    def test_import_empty_optional_cells(self):
        wizard = self._create_wizard(
            [HEADER, ["TST-IMP-002", 4, "", "", ""]],
        )
        wizard.action_import()
        reference_line = self._get_reference_line(self.product_2, 4)
        self.assertEqual(self.order.order_line.name, reference_line.name)
        self.assertEqual(self.order.order_line.price_unit, 7.5)
        self.assertFalse(self.order.order_line.analytic_distribution)

    def test_import_headers_by_key_and_case(self):
        wizard = self._create_wizard(
            [
                ["product_qty", "DEFAULT_CODE", "  unit   price "],
                [5, "TST-IMP-001", 2.5],
            ]
        )
        wizard.action_import()
        self.assertEqual(self.order.order_line.product_id, self.product_1)
        self.assertEqual(self.order.order_line.product_qty, 5.0)
        self.assertEqual(self.order.order_line.price_unit, 2.5)

    def test_import_csv(self):
        content = "default_code;product_qty;price_unit\nTST-IMP-001;4;1.234,56\n"
        wizard = self._create_wizard(
            file=base64.b64encode(content.encode()), file_name="lines.csv"
        )
        wizard.action_import()
        self.assertEqual(self.order.order_line.product_qty, 4.0)
        self.assertAlmostEqual(self.order.order_line.price_unit, 1234.56)

    def test_import_header_errors(self):
        wizard = self._create_wizard(
            [
                ["Quantity", "Quantity", "Unknown"],
                [1, 1, "x"],
            ]
        )
        with self.assertRaises(UserError) as error:
            wizard.action_import()
        message = error.exception.args[0]
        self.assertIn('Unknown column "Unknown".', message)
        self.assertIn('Column "Quantity" appears more than once.', message)
        self.assertIn('Required column "Internal Reference" is missing.', message)
        self.assertFalse(self.order.order_line)

    def test_import_row_errors_import_nothing(self):
        self.env["account.analytic.account"].create(
            {"name": "Test Project", "plan_id": self.analytic_plan.id}
        )
        self._create_product(default_code="TST-IMP-DUP")
        self._create_product(default_code="TST-IMP-DUP")
        self._create_product(default_code="TST-IMP-NOBUY", purchase_ok=False)
        wizard = self._create_wizard(
            [
                HEADER,
                ["TST-IMP-001", 1, "", "", ""],
                ["TST-IMP-MISSING", 1, "", "", ""],
                ["TST-IMP-DUP", 1, "", "", ""],
                ["TST-IMP-NOBUY", 1, "", "", ""],
                ["", 1, "", "", ""],
                ["TST-IMP-001", "", "", "", ""],
                ["TST-IMP-001", 0, "", "", ""],
                ["TST-IMP-001", "abc", "", "", ""],
                ["TST-IMP-001", 1, "", "abc", ""],
                ["TST-IMP-001", 1, "", "", "Unknown Project"],
                ["TST-IMP-001", 1, "", "", "Test Project"],
            ]
        )
        with self.assertRaises(UserError) as error:
            wizard.action_import()
        message = error.exception.args[0]
        self.assertTrue(message.startswith("No line has been imported."))
        for expected in [
            'Row 3: No purchasable product found with internal reference "TST-IMP-MIS',
            'Row 4: Several products found with internal reference "TST-IMP-DUP"',
            'Row 5: No purchasable product found with internal reference "TST-IMP-NOB',
            "Row 6: The internal reference is required.",
            "Row 7: The quantity is required.",
            "Row 8: The quantity must be greater than zero.",
            'Row 9: Quantity: "abc" is not a valid number.',
            'Row 10: Unit Price: "abc" is not a valid number.',
            'Row 11: No analytic account found for "Unknown Project".',
            'Row 12: Several analytic accounts found for "Test Project".',
        ]:
            self.assertIn(expected, message)
        self.assertNotIn("Row 2:", message)
        self.assertFalse(self.order.order_line)

    def test_import_confirmed_order(self):
        self.order.order_line = [
            Command.create({"product_id": self.product_1.id, "product_qty": 1.0})
        ]
        wizard = self._create_wizard([HEADER, ["TST-IMP-002", 1, "", "", ""]])
        self.order.button_confirm()
        with self.assertRaisesRegex(UserError, "request for quotation"):
            wizard.action_import()
        self.assertEqual(len(self.order.order_line), 1)

    def test_import_without_file(self):
        wizard = self._create_wizard()
        with self.assertRaisesRegex(UserError, "select a file"):
            wizard.action_import()

    def test_parse_float(self):
        for value, expected in [
            ("2", 2.0),
            ("1.13", 1.13),
            ("1,13", 1.13),
            ("1.234,56", 1234.56),
            ("1,234.56", 1234.56),
            ("1 234,56", 1234.56),
            ("1e3", 1000.0),
        ]:
            with self.subTest(value=value):
                self.assertAlmostEqual(
                    self.LineImport._parse_float(value, "Number"), expected
                )
        for value in ["abc", "1.234.567", "12-"]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(UserError, "is not a valid number"):
                    self.LineImport._parse_float(value, "Number")
