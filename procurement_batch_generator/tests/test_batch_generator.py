# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProcurementBatchGenerator(TransactionCase):
    def test_product_product_wizard(self):
        """Create procurement requests, validate and check result"""
        pbgo = self.env["procurement.batch.generator"]
        ctx = self.env.context.copy()
        ctx.update(
            {
                "active_ids": [
                    self.env.ref("product.product_product_9").id,
                    self.env.ref("product.product_product_12").id,
                ],
                "active_model": "product.product",
            }
        )
        wiz = pbgo.with_context(**ctx).create({})
        self.assertEqual(len(wiz.line_ids), 2)
        wiz.line_ids.write({"procurement_qty": 42})
        wiz.validate()

    def test_product_template_wizard(self):
        pbgo = self.env["procurement.batch.generator"]
        ctx = self.env.context.copy()
        ctx.update(
            {
                "active_ids": [
                    self.env.ref("product.product_product_9").product_tmpl_id.id,
                    self.env.ref("product.product_product_12").product_tmpl_id.id,
                ],
                "active_model": "product.template",
            }
        )
        wiz = pbgo.with_context(**ctx).create({})
        self.assertEqual(len(wiz.line_ids), 2)
        wiz.line_ids.write({"procurement_qty": 12})
        wiz.validate()

    def _get_wizard(self, model, records, **extra_ctx):
        ctx = {"active_ids": records.ids, "active_model": model}
        ctx.update(extra_ctx)
        return self.env["procurement.batch.generator"].with_context(**ctx).create({})

    def test_defaults(self):
        product = self.env.ref("product.product_product_9")
        wiz = self._get_wizard("product.product", product)
        self.assertEqual(wiz.company_id, self.env.company)
        self.assertEqual(
            wiz.warehouse_id,
            self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            ),
        )
        line = wiz.line_ids
        self.assertEqual(line.product_id, product)
        self.assertEqual(line.product_tmpl_id, product.product_tmpl_id)
        self.assertEqual(line.uom_id, product.uom_id)
        self.assertFalse(line.product_has_variants)
        self.assertEqual(line.date_planned, fields.Date.context_today(wiz))

    def test_defaults_from_context(self):
        product = self.env.ref("product.product_product_9")
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        wiz = self._get_wizard(
            "product.product",
            product,
            default_company_id=warehouse.company_id.id,
            default_warehouse_id=warehouse.id,
        )
        self.assertEqual(wiz.company_id, warehouse.company_id)
        self.assertEqual(wiz.warehouse_id, warehouse)

    def test_supplier_and_variants(self):
        template = self.env.ref("product.product_product_4_product_template")
        self.assertGreater(len(template.product_variant_ids), 1)
        supplier = self.env["res.partner"].create({"name": "Test Supplier"})
        template.product_variant_ids[0].write(
            {"seller_ids": [(0, 0, {"partner_id": supplier.id, "min_qty": 1})]}
        )
        wiz = self._get_wizard("product.product", template.product_variant_ids[0])
        self.assertTrue(wiz.line_ids.product_has_variants)
        self.assertEqual(wiz.line_ids.partner_id, supplier)
        wiz = self._get_wizard("product.template", template)
        self.assertTrue(wiz.line_ids.product_has_variants)

    def test_no_lines(self):
        wiz = self._get_wizard("product.product", self.env["product.product"])
        self.assertFalse(wiz.line_ids)
        with self.assertRaises(UserError):
            wiz.validate()

    def test_negative_qty(self):
        product = self.env.ref("product.product_product_9")
        wiz = self._get_wizard("product.product", product)
        wiz.line_ids.write({"procurement_qty": -1})
        with self.assertRaises(UserError):
            wiz.validate()

    def test_zero_qty_is_skipped(self):
        products = self.env.ref("product.product_product_9") | self.env.ref(
            "product.product_product_12"
        )
        wiz = self._get_wizard("product.product", products)
        wiz.line_ids[0].procurement_qty = 0
        wiz.line_ids[1].procurement_qty = 5
        wiz.validate()
        group = self.env["procurement.group"].search(
            [("partner_id", "=", self.env.user.partner_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertTrue(group)

    def test_prepare_run_values(self):
        product = self.env.ref("product.product_product_9")
        wiz = self._get_wizard("product.product", product)
        group = self.env["procurement.group"].create(wiz._prepare_procurement_group())
        values = wiz.line_ids._prepare_run_values(group)
        self.assertEqual(values["warehouse_id"], wiz.warehouse_id)
        self.assertEqual(values["group_id"], group)
        self.assertEqual(values["date_planned"], wiz.line_ids.date_planned)
