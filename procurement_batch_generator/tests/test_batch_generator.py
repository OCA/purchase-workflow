# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        wiz = pbgo.with_context(ctx).create({})
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
        wiz = pbgo.with_context(ctx).create({})
        self.assertEqual(len(wiz.line_ids), 2)
        wiz.line_ids.write({"procurement_qty": 12})
        wiz.validate()
